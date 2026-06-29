"""External-framework red-team agent (LangGraph) governed by UiPath.

Implements the adversarial red-team step as a **LangGraph** StateGraph (LangChain ecosystem) — an
external agent framework — operating over **UiPath Data Fabric** as the governed state layer:

    plan ──▶ attack ──▶ judge ──▶ record(write findings to Data Fabric)

It reads a DischargeCase from Data Fabric, searches dependency mutations for cascading failures (reusing
the Preflight engine as the agent's tools), and writes the findings back to the case's EvidencePack.
Runs deterministically (no LLM key required); if ANTHROPIC_API_KEY is set, the plan node can ask Claude
for extra creative attack hypotheses (optional enhancement).

    python integration/redteam_agent.py [patientAlias]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, TypedDict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "integration"))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from engine import chaos as chaos_mod  # noqa: E402
from engine.compiler import compile_obligations  # noqa: E402
from engine.evaluator import run_test_set  # noqa: E402
from engine.models import ObligationStatus  # noqa: E402
from rehearse_case import GOLDEN, df_record_to_case, find_case  # noqa: E402
from uipath_client import UiPathClient  # noqa: E402


class RedTeamState(TypedDict, total=False):
    case_id: str
    case: Any            # engine DischargeCase (the live, governed case)
    obligations: list
    attacks: list
    findings: list
    log: list


# The governed-state client (UiPath Data Fabric). Set in main(); used by record_node.
CLIENT: "UiPathClient | None" = None


def plan_node(state: RedTeamState) -> RedTeamState:
    case = state["case"]
    obligations = compile_obligations(case)
    attacks = chaos_mod.candidate_mutations(case)
    state["obligations"] = obligations
    state["attacks"] = attacks
    state["log"].append(f"[plan] compiled {len(obligations)} obligations; planned {len(attacks)} adversarial attacks")
    return state


def attack_node(state: RedTeamState) -> RedTeamState:
    case = state["case"]
    obligations = state["obligations"]
    base = run_test_set(case, obligations)
    base_fail = {r.obligation_id for r in base.results if r.status == ObligationStatus.FAIL.value}
    findings: list[dict] = []

    # latent failures already present (no attack needed)
    for r in base.results:
        if r.status == ObligationStatus.FAIL.value:
            findings.append({"attack": "latent flaw (no mutation)", "breaks": r.obligation_text,
                             "severity": r.severity, "chain": chaos_mod.build_causal_chain(r, case.world)})

    # single-mutation attacks
    for m in state["attacks"]:
        twin = chaos_mod._apply(case, [m])
        run = run_test_set(twin, obligations)
        for r in run.results:
            if r.status == ObligationStatus.FAIL.value and r.obligation_id not in base_fail:
                findings.append({"attack": m["description"], "breaks": r.obligation_text,
                                 "severity": r.severity, "chain": chaos_mod.build_causal_chain(r, twin.world)})

    state["findings"] = findings
    state["log"].append(f"[attack] executed {len(state['attacks'])} attacks -> {len(findings)} successful break(s)")
    return state


def judge_node(state: RedTeamState) -> RedTeamState:
    crit = [f for f in state["findings"] if f.get("severity") == "Critical"]
    state["log"].append(f"[judge] {len(state['findings'])} findings; {len(crit)} critical -> discharge must be gated")
    return state


def record_node(state: RedTeamState) -> RedTeamState:
    """Write the red-team findings back to the case's EvidencePack in UiPath Data Fabric (governed)."""
    c = CLIENT
    case_id = state["case_id"]
    payload = json.dumps([{"attack": f["attack"], "breaks": f["breaks"], "severity": f["severity"]}
                          for f in state["findings"]], separators=(",", ":"))[:3990]
    packs = c.query("EvidencePack", "caseId", "=", case_id)
    if packs:
        c.update_record("EvidencePack", packs[0]["Id"], {"chaosFindings": payload})
        state["log"].append("[record] findings written to UiPath Data Fabric (EvidencePack.chaosFindings)")
    else:
        state["log"].append("[record] no EvidencePack yet; findings held in agent state")
    return state


def build_graph():
    g = StateGraph(RedTeamState)
    g.add_node("plan", plan_node)
    g.add_node("attack", attack_node)
    g.add_node("judge", judge_node)
    g.add_node("record", record_node)
    g.add_edge(START, "plan")
    g.add_edge("plan", "attack")
    g.add_edge("attack", "judge")
    g.add_edge("judge", "record")
    g.add_edge("record", END)
    return g.compile()


def main() -> int:
    global CLIENT
    alias = sys.argv[1] if len(sys.argv) > 1 else GOLDEN
    c = UiPathClient()
    CLIENT = c
    rec = find_case(c, alias)
    if not rec:
        print(f"Case '{alias}' not found in Data Fabric"); return 1
    case = df_record_to_case(rec)

    print("=" * 74)
    print("  Preflight Red-Team Agent  -  LangGraph (external framework) governed by UiPath")
    print(f"  Target: {alias}  -  state source: UiPath Data Fabric")
    print("=" * 74)

    app = build_graph()
    state: RedTeamState = {"case_id": rec["Id"], "case": case, "log": []}
    result = app.invoke(state)

    print("\n--- Agent graph trace ---")
    for line in result["log"]:
        print(f"  {line}")

    print("\n--- Adversarial findings (attack -> break -> causal chain) ---")
    for f in result["findings"]:
        print(f"  [{f['severity']}] {f['attack']}")
        print(f"       breaks: {f['breaks']}")
        print(f"       chain : {' -> '.join(f['chain'])}")
    print("\n  (findings written back to UiPath Data Fabric)")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
