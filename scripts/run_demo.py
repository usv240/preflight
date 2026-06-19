"""Preflight demo runner.

Runs the full rehearsal for a synthetic case and prints a narrated trace that mirrors the 5-minute
demo: fork -> compile -> chaos -> prove -> GATE/BLOCK -> human remedy -> re-test -> release -> evidence.

Usage:
    python scripts/run_demo.py [case_name]
    (default case_name = golden_case)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make the package importable when run as a script.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.loader import load_case  # noqa: E402
from engine.models import Decision, ObligationStatus  # noqa: E402
from engine.orchestrator import rehearse  # noqa: E402

LINE = "=" * 78


def scripted_nurse(failed, proposed, attempt):
    """Action Center stand-in: a nurse approves the proposed operational remedy on the first attempt."""
    print(f"\n  [Action Center] Nurse review (attempt {attempt})")
    print(f"    Failed obligations ({len(failed)}):")
    for r in failed:
        print(f"      - [{r.severity}] {r.obligation_text}")
        print(f"          why: {r.detail}")
    print("    Proposed operational remedy:")
    for a in proposed["actions"]:
        print(f"      * {a}")
    print("    Decision: APPROVE_REMEDY")
    return {"decision": Decision.APPROVE_REMEDY.value, "approver": "nurse Alex (synthetic)",
            "note": "Operational remedy approved; no clinical change."}


def main() -> int:
    case_name = sys.argv[1] if len(sys.argv) > 1 else "golden_case"
    case = load_case(case_name)

    print(LINE)
    print(f"PREFLIGHT - rehearsing case '{case_name}'  |  patient {case.patient_alias}")
    print("Synthetic data. Preflight validates operational readiness only; it does not diagnose or prescribe.")
    print(LINE)

    result = rehearse(case, scripted_nurse)

    print("\n--- Rehearsal trace ---")
    for line in result.audit:
        print(f"  {line}")

    print("\n--- Chaos / red-team findings ---")
    if not result.scenarios:
        print("  (no failures found)")
    for s in result.scenarios:
        print(f"  * {s.description}")
        print(f"      breaks: {', '.join(s.failed_obligations)}")
        print(f"      chain : {' -> '.join(s.causal_chain)}")

    print("\n--- Final obligation results ---")
    for r in result.runs[-1].results:
        mark = "PASS" if r.status == ObligationStatus.PASS.value else "FAIL"
        print(f"  [{mark}] ({r.severity}) {r.obligation_text}")

    print("\n--- Verdict ---")
    print(f"  Status         : {result.status}")
    print(f"  Readiness score: {result.case.readiness_score}%")
    print(f"  Evidence verdict: {result.evidence.verdict.upper()}")
    print(f"  Re-tests run   : {len(result.runs)}")
    print(f"  Regression learned: {len(result.regression)}")

    # Write the evidence pack (auditable proof).
    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{case_name}.evidence.json"
    out_path.write_text(json.dumps(result.evidence.to_dict(), indent=2), encoding="utf-8")
    print(f"\n  Evidence pack written: {out_path.relative_to(ROOT)}")
    print(LINE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
