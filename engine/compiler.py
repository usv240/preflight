"""The case-to-test compiler.

Turns one case's messy facts + the discharge policy into a parameterized set of executable outcome
obligations. This is the offline stand-in for the UiPath **Agent Builder** compiler agent (which uses
Context Grounding on the policy doc so it cannot invent rules). The logic is deterministic here for a
reproducible demo; the UiPath version swaps in the grounded agent behind the same contract.
"""

from __future__ import annotations

from .models import DischargeCase, Obligation, ObligationType, Severity


def compile_obligations(case: DischargeCase) -> list[Obligation]:
    """Derive obligations from the plan + world, grounded on the discharge policy (P1..P7)."""
    obligations: list[Obligation] = []
    meds: list[str] = case.world.get("meds", [])

    # P1 — every med in stock (Critical), one obligation per medication
    for med in meds:
        obligations.append(Obligation(
            text=f"Medication '{med}' is in stock at the collection pharmacy.",
            type=ObligationType.MED_IN_STOCK.value,
            params={"med": med},
            severity=Severity.CRITICAL.value,
            owner_role="Discharge Pharmacist",
            case_id=case.id,
        ))

    # P2 — every med covered (Critical)
    for med in meds:
        obligations.append(Obligation(
            text=f"Medication '{med}' is covered by the patient's plan.",
            type=ObligationType.MED_COVERED.value,
            params={"med": med},
            severity=Severity.CRITICAL.value,
            owner_role="Discharge Pharmacist",
            case_id=case.id,
        ))

    # P3 — medication physically collectable (Critical, cross-system)
    obligations.append(Obligation(
        text="The patient can physically collect medication: transport arrives before the pharmacy closes.",
        type=ObligationType.MEDICATION_COLLECTABLE.value,
        params={},
        severity=Severity.CRITICAL.value,
        owner_role="Care Coordinator",
        case_id=case.id,
    ))

    # P4 — transport confirmed + fallback (High)
    obligations.append(Obligation(
        text="Transportation home is confirmed and has a fallback option.",
        type=ObligationType.TRANSPORT_CONFIRMED.value,
        params={},
        severity=Severity.HIGH.value,
        owner_role="Care Coordinator",
        case_id=case.id,
    ))

    # P5 — follow-up actually booked (High)
    obligations.append(Obligation(
        text="A follow-up appointment is booked and confirmed (not merely recommended).",
        type=ObligationType.FOLLOWUP_BOOKED.value,
        params={},
        severity=Severity.HIGH.value,
        owner_role="Scheduler",
        case_id=case.id,
    ))

    # P6 — instructions accessible (High)
    obligations.append(Obligation(
        text="Discharge instructions are in a language and format the patient/caregiver can act on.",
        type=ObligationType.INSTRUCTIONS_ACCESSIBLE.value,
        params={},
        severity=Severity.HIGH.value,
        owner_role="Discharge Nurse",
        case_id=case.id,
    ))

    # P7 — every dependency owned (Medium)
    obligations.append(Obligation(
        text="Every unresolved dependency has a named owner and escalation path.",
        type=ObligationType.DEPENDENCY_OWNED.value,
        params={"dependencies": ["pharmacy", "transport", "followup", "instructions"]},
        severity=Severity.MEDIUM.value,
        owner_role="Discharge Nurse",
        case_id=case.id,
    ))

    return obligations
