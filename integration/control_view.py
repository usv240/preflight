"""Preflight control view — renders a live rehearsal status by reading Data Fabric + Test Manager.

    python integration/control_view.py [patientAlias]

Reads everything live from the UiPath platform, so running it before vs. after the human gate shows
the verdict flip from RED/Blocked to GREEN/Released.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from uipath_client import UiPathClient  # noqa: E402

GOLDEN = "PT-1041 (synthetic)"
W = 78
BAR = "=" * W


def line(s: str = "") -> None:
    print(s)


def hr() -> None:
    print("-" * W)


def main() -> int:
    alias = sys.argv[1] if len(sys.argv) > 1 else GOLDEN
    c = UiPathClient()

    cases = c.query("DischargeCase", "patientAlias", "=", alias)
    if not cases:
        print(f"Case '{alias}' not found"); return 1
    case = cases[0]
    cid = case["Id"]
    obligations = c.query("Obligation", "caseId", "=", cid)
    evidence = c.query("EvidencePack", "caseId", "=", cid)
    decisions = c.query("HumanDecision", "caseId", "=", cid)
    ev = evidence[0] if evidence else {}
    pid = c.tm_project_id("Preflight")
    tc = []
    if pid:
        st, payload = c.tm_request("GET", f"/testcase/project/{pid}/search?pageSize=50")
        tc = payload.get("data", []) if isinstance(payload, dict) else []

    verdict = (ev.get("verdict") or "?").upper()
    status = case.get("status", "?")
    score = case.get("readinessScore", 0)

    line(BAR)
    line("  PREFLIGHT  -  Discharge Readiness Rehearsal (control view)")
    line(f"  Patient: {alias}    |    Source: UiPath Data Fabric + Test Manager (live)")
    line(BAR)
    line(f"  STATUS: {status:<12}  READINESS: {score}%   VERDICT: {verdict}")
    line("  (synthetic data; validates operational readiness only - never diagnoses or prescribes)")
    hr()

    line(f"  OUTCOME OBLIGATIONS  ({len(obligations)} compiled from policy; mirrored as {len(tc)} "
         f"Test Manager test cases)")
    for o in sorted(obligations, key=lambda x: (x.get("severity", ""), x.get("type", ""))):
        mark = "PASS" if o.get("status") == "Pass" else "FAIL"
        flag = " " if mark == "PASS" else "!"
        line(f"   {flag}[{mark}] ({o.get('severity','')[:8]:<8}) {o.get('text','')[:52]}")
        if mark == "FAIL":
            line(f"          why: {o.get('detail','')[:64]}")
    hr()

    chains = json.loads(ev.get("causalChains") or "[]") if ev else []
    if chains and verdict == "RED":
        line("  CAUSAL FAILURE CHAIN (found by the chaos / red-team agent)")
        for step in chains[0]:
            line(f"     -> {step}")
        hr()

    if decisions:
        d = decisions[0]
        line(f"  HUMAN GATE (Action Center): decision = {d.get('decision')}  "
             f"by {d.get('approverAlias') or '(pending)'}")
        try:
            remedy = json.loads(d.get("proposedRemedy") or "{}")
            for a in remedy.get("actions", [])[:2]:
                line(f"     remedy: {a[:66]}")
        except Exception:  # noqa: BLE001
            pass
        hr()

    if verdict == "GREEN":
        line("  GATE: PASSED  ->  plan released for real execution.")
    else:
        line("  GATE: BLOCKED ->  real discharge withheld until obligations pass or a human signs off.")
    line(BAR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
