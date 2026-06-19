"""Evidence pack builder — the auditable proof of a rehearsal."""

from __future__ import annotations

from .evaluator import readiness_score
from .models import ChaosScenario, DischargeCase, EvidencePack, ObligationStatus, TestRun


def build_evidence_pack(
    case: DischargeCase,
    final_run: TestRun,
    scenarios: list[ChaosScenario],
    audit_trail: list[str],
) -> EvidencePack:
    verdict = "green" if final_run.overall_status == ObligationStatus.PASS.value else "red"
    causal_chains = [s.causal_chain for s in scenarios if s.causal_chain]
    return EvidencePack(
        case_id=case.id,
        verdict=verdict,
        obligation_results=final_run.results,
        causal_chains=causal_chains,
        audit_trail=audit_trail,
        readiness_score=readiness_score(final_run),
    )
