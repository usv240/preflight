"""Preflight rehearsal coded agent (Data Fabric I/O).

Reads a DischargeCase from Data Fabric, runs the Preflight engine, and writes the results back as
Obligation + EvidencePack + HumanDecision records, and updates the case status. Two stages map to the
Maestro flow around the human gate:

    python integration/rehearse_case.py block    <patientAlias>   # rehearse -> catch flaw -> BLOCK
    python integration/rehearse_case.py release  <patientAlias>   # apply approved remedy -> RELEASE

Default patientAlias = "PT-1041 (synthetic)" (the golden demo case).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "integration"))

from engine import chaos as chaos_mod  # noqa: E402
from engine.compiler import compile_obligations  # noqa: E402
from engine.evaluator import readiness_score, run_test_set  # noqa: E402
from engine.models import DischargeCase, ObligationStatus, PlanItem  # noqa: E402
from engine.remedy import apply_remedy, propose_remedy  # noqa: E402
from uipath_client import UiPathClient  # noqa: E402

GOLDEN = "PT-1041 (synthetic)"


def df_record_to_case(rec: dict) -> DischargeCase:
    plan = [PlanItem(type=p["type"], payload=p.get("payload", {}), promise_text=p.get("promise_text", ""))
            for p in json.loads(rec.get("planJson") or "[]")]
    return DischargeCase(
        patient_alias=rec.get("patientAlias", ""),
        plan_items=plan,
        world=json.loads(rec.get("worldJson") or "{}"),
        owners=json.loads(rec.get("ownersJson") or "{}"),
    )


def find_case(c: UiPathClient, alias: str) -> dict | None:
    rows = c.query("DischargeCase", "patientAlias", "=", alias)
    return rows[0] if rows else None


def _write_obligations(c: UiPathClient, case_id: str, obligations, results) -> None:
    c.delete_where("Obligation", "caseId", case_id)
    for ob, res in zip(obligations, results):
        c.insert_record("Obligation", {
            "caseId": case_id,
            "text": ob.text,
            "type": ob.type,
            "paramsJson": json.dumps(ob.params, separators=(",", ":")),
            "severity": ob.severity,
            "ownerRole": ob.owner_role,
            "status": res.status,
            "detail": res.detail,
            "touched": json.dumps(res.touched, separators=(",", ":")),
        })


def _write_evidence(c: UiPathClient, case_id: str, verdict: str, score: float,
                    results, scenarios, audit, regression: int) -> None:
    c.delete_where("EvidencePack", "caseId", case_id)
    c.insert_record("EvidencePack", {
        "caseId": case_id,
        "verdict": verdict,
        "readinessScore": score,
        "obligationResults": json.dumps(
            [{"text": r.obligation_text, "severity": r.severity, "status": r.status, "detail": r.detail}
             for r in results], separators=(",", ":"))[:3990],
        "causalChains": json.dumps([s.causal_chain for s in scenarios if s.causal_chain],
                                   separators=(",", ":"))[:3990],
        "auditTrail": json.dumps(audit, separators=(",", ":"))[:3990],
        "chaosFindings": json.dumps(
            [{"desc": s.description, "breaks": s.failed_obligations} for s in scenarios],
            separators=(",", ":"))[:3990],
        "regressionLearned": regression,
    })


def stage_block(c: UiPathClient, alias: str) -> None:
    rec = find_case(c, alias)
    if not rec:
        print(f"Case '{alias}' not found"); return
    case_id = rec["Id"]
    case = df_record_to_case(rec)

    obligations = compile_obligations(case)
    scenarios, audit = chaos_mod.search(case, obligations)
    run = run_test_set(case, obligations)
    score = readiness_score(run)
    failed = [r for r in run.results if r.status == ObligationStatus.FAIL.value]

    _write_obligations(c, case_id, obligations, run.results)
    _write_evidence(c, case_id, "red" if failed else "green", score, run.results, scenarios, audit, 0)

    remedy = propose_remedy(case, failed)
    c.delete_where("HumanDecision", "caseId", case_id)
    c.insert_record("HumanDecision", {
        "caseId": case_id,
        "proposedRemedy": json.dumps(remedy, separators=(",", ":"))[:1990],
        "decision": "Pending",
        "approverAlias": "",
        "note": "Awaiting nurse review in Action Center.",
    })

    new_status = "Blocked" if failed else "Released"
    c.update_record("DischargeCase", case_id, {"status": new_status, "readinessScore": score})
    print(f"[block] {alias}: {len(failed)} failing obligation(s), status -> {new_status}, readiness {score}%")
    for r in failed:
        print(f"    FAIL [{r.severity}] {r.obligation_text}")


def stage_release(c: UiPathClient, alias: str) -> None:
    rec = find_case(c, alias)
    if not rec:
        print(f"Case '{alias}' not found"); return
    case_id = rec["Id"]
    case = df_record_to_case(rec)

    obligations = compile_obligations(case)
    base = run_test_set(case, obligations)
    failed = [r for r in base.results if r.status == ObligationStatus.FAIL.value]
    remedy = propose_remedy(case, failed)
    fixed = apply_remedy(case, remedy)
    run = run_test_set(fixed, obligations)
    score = readiness_score(run)
    passed = run.overall_status == ObligationStatus.PASS.value

    _write_obligations(c, case_id, obligations, run.results)
    scenarios, audit = chaos_mod.search(case, obligations)
    regression = len([s for s in scenarios if s.result == "obligation_failed"]) if passed else 0
    _write_evidence(c, case_id, "green" if passed else "red", score, run.results, scenarios, audit, regression)

    c.delete_where("HumanDecision", "caseId", case_id)
    c.insert_record("HumanDecision", {
        "caseId": case_id,
        "proposedRemedy": json.dumps(remedy, separators=(",", ":"))[:1990],
        "decision": "ApproveRemedy",
        "approverAlias": "nurse Alex (synthetic)",
        "note": "Operational remedy approved; no clinical change.",
    })

    new_status = "Released" if passed else "Blocked"
    c.update_record("DischargeCase", case_id, {"status": new_status, "readinessScore": score})
    print(f"[release] {alias}: status -> {new_status}, readiness {score}%, regression learned {regression}")


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else "block"
    alias = sys.argv[2] if len(sys.argv) > 2 else GOLDEN
    c = UiPathClient()
    if stage == "block":
        stage_block(c, alias)
    elif stage == "release":
        stage_release(c, alias)
    else:
        print("usage: rehearse_case.py [block|release] [patientAlias]")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
