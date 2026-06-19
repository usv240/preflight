"""Preflight orchestrator — the offline stand-in for the UiPath **Maestro** process.

Implements the pattern: fork twin -> compile obligations -> chaos search -> prove (Test Cloud) ->
**gate** -> (human in Action Center) -> apply remedy -> re-test loop -> release -> learn.

The ``human_decision_fn`` callback is the Action Center user task: it receives the failed obligations and
the proposed remedy, and returns a decision. Tests pass an auto-approver; the CLI passes a scripted or
interactive one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from . import chaos as chaos_mod
from .compiler import compile_obligations
from .evaluator import readiness_score, run_test_set
from .evidence import build_evidence_pack
from .models import (
    CaseStatus,
    ChaosScenario,
    DischargeCase,
    Decision,
    EvidencePack,
    HumanDecision,
    Obligation,
    ObligationResult,
    ObligationStatus,
    RegressionScenario,
    Severity,
    TestRun,
)
from .remedy import apply_remedy, propose_remedy

# (failed_results, proposed_remedy, attempt) -> {"decision": Decision, "remedy": optional dict, "approver":str, "note":str}
HumanDecisionFn = Callable[[list[ObligationResult], dict, int], dict]


@dataclass
class RehearsalResult:
    case: DischargeCase
    twin: DischargeCase
    obligations: list[Obligation]
    scenarios: list[ChaosScenario]
    runs: list[TestRun]
    evidence: EvidencePack
    decisions: list[HumanDecision]
    regression: list[RegressionScenario]
    status: str
    audit: list[str] = field(default_factory=list)

    @property
    def released(self) -> bool:
        return self.status == CaseStatus.RELEASED.value


def _failed(results: list[ObligationResult]) -> list[ObligationResult]:
    return [r for r in results if r.status == ObligationStatus.FAIL.value]


def _critical_failed(results: list[ObligationResult]) -> list[ObligationResult]:
    return [r for r in _failed(results) if r.severity == Severity.CRITICAL.value]


def rehearse(
    case: DischargeCase,
    human_decision_fn: HumanDecisionFn,
    max_loops: int = 3,
) -> RehearsalResult:
    audit: list[str] = []

    # (1) Fork reality
    twin = case.clone_as_shadow()
    audit.append(f"Forked disposable shadow twin {twin.id} of case {case.id}")

    # (2) Compile obligations (grounded on policy)
    obligations = compile_obligations(twin)
    audit.append(f"Compiled {len(obligations)} outcome obligations from plan + policy")

    # (3) Chaos / red-team search (latent + mutation-induced failures)
    scenarios, chaos_log = chaos_mod.search(twin, obligations)
    audit.extend(chaos_log)

    # (4) Prove via Test Cloud (initial run)
    runs: list[TestRun] = []
    run = run_test_set(twin, obligations)
    runs.append(run)
    audit.append(f"Test run {run.id}: {run.overall_status} "
                 f"(readiness {readiness_score(run)}%, {len(_failed(run.results))} failing)")

    decisions: list[HumanDecision] = []
    regression: list[RegressionScenario] = []

    # (5) Gate + human loop
    attempt = 0
    while run.overall_status == ObligationStatus.FAIL.value and attempt < max_loops:
        attempt += 1
        failed = _failed(run.results)
        crit = _critical_failed(run.results)
        twin.status = CaseStatus.BLOCKED.value if crit else CaseStatus.AWAITING_HUMAN.value
        audit.append(f"GATE: {'BLOCKED (critical failure)' if crit else 'HOLD (non-critical failure)'} "
                     f"-> routing to Action Center (attempt {attempt})")

        proposed = propose_remedy(twin, failed)
        decision_raw = human_decision_fn(failed, proposed, attempt)
        decision = decision_raw.get("decision", Decision.REJECT.value)
        remedy = decision_raw.get("remedy", proposed)
        approver = decision_raw.get("approver", "nurse (synthetic)")
        note = decision_raw.get("note", "")
        decisions.append(HumanDecision(case_id=twin.id, proposed_remedy=remedy,
                                       decision=decision, approver_alias=approver, note=note))
        audit.append(f"Human decision by {approver}: {decision}")

        if decision in (Decision.APPROVE_REMEDY.value, Decision.EDIT_REMEDY.value):
            twin = apply_remedy(twin, remedy)
            twin.status = CaseStatus.REHEARSAL_RUNNING.value
            run = run_test_set(twin, obligations)
            runs.append(run)
            audit.append(f"Re-test {run.id} after remedy: {run.overall_status} "
                         f"(readiness {readiness_score(run)}%)")
        elif decision == Decision.ACCEPT_EXCEPTION.value:
            if _critical_failed(run.results):
                audit.append("Exception REFUSED: critical obligations are not waivable per policy")
                twin.status = CaseStatus.BLOCKED.value
                break
            audit.append("Documented exception accepted for non-critical failure(s)")
            twin.status = CaseStatus.VERIFIED.value
            break
        else:  # REJECT
            audit.append("Remedy rejected; case remains blocked")
            twin.status = CaseStatus.BLOCKED.value
            break

    # (6) Release decision
    if run.overall_status == ObligationStatus.PASS.value:
        twin.status = CaseStatus.RELEASED.value
        case.status = CaseStatus.RELEASED.value
        audit.append("GATE PASSED -> plan released for real execution")
    elif twin.status == CaseStatus.VERIFIED.value:
        case.status = CaseStatus.VERIFIED.value
        audit.append("Released under documented exception with named accountability")
    else:
        case.status = CaseStatus.BLOCKED.value
        audit.append("Case remains BLOCKED; not released")

    case.readiness_score = readiness_score(run)

    # (7) Learn — promote a resolved failure into a reusable regression scenario
    if (twin.status in (CaseStatus.RELEASED.value, CaseStatus.VERIFIED.value)) and len(runs) > 1:
        for s in scenarios:
            if s.result == "obligation_failed":
                regression.append(RegressionScenario(
                    source_case_id=case.id,
                    pattern={"failed_obligations": s.failed_obligations,
                             "mutations": s.mutations,
                             "description": s.description},
                ))
        if regression:
            audit.append(f"Learned {len(regression)} reusable regression scenario(s)")

    evidence = build_evidence_pack(twin, run, scenarios, audit)

    return RehearsalResult(
        case=case, twin=twin, obligations=obligations, scenarios=scenarios, runs=runs,
        evidence=evidence, decisions=decisions, regression=regression, status=twin.status, audit=audit,
    )
