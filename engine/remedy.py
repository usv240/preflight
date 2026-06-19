"""Remedy proposer.

Proposes OPERATIONAL remedies for failed obligations — never clinical decisions (no diagnosis, no
medication/dose changes). Offline stand-in for the UiPath **Agent Builder** Remedy Proposer agent. The
proposed remedy is presented to a human in Action Center; only after approval is it applied to the twin
and re-tested.
"""

from __future__ import annotations

from .models import DischargeCase, ObligationResult, ObligationStatus, ObligationType


def propose_remedy(case: DischargeCase, failed: list[ObligationResult]) -> dict:
    """Return {summary, actions[], mutations[]} for the failed obligations. Operational only."""
    actions: list[str] = []
    mutations: list[dict] = []
    seen_types: set[str] = set()

    for r in failed:
        t = r.type
        if t in seen_types:
            continue
        seen_types.add(t)

        if t == ObligationType.MEDICATION_COLLECTABLE.value:
            actions.append("Switch collection to a 24-hour in-network pharmacy so arrival time is no "
                           "longer constrained by closing hours (no change to medication or dose).")
            mutations.append({"scope": "world", "path": "pharmacy.name",
                              "value": "Central 24h In-Network Pharmacy (synthetic)",
                              "description": "Reassign to 24h in-network pharmacy"})
            mutations.append({"scope": "world", "path": "pharmacy.closes_at", "value": "23:59",
                              "description": "24h pharmacy effectively always open at collection time"})

        elif t == ObligationType.MED_IN_STOCK.value:
            med = _med_from(r)
            actions.append(f"Transfer {med} stock from an alternate in-network pharmacy before pickup.")
            if med:
                mutations.append({"scope": "world", "path": f"pharmacy.stock.{med}", "value": True,
                                  "description": f"Stock {med} sourced from alternate in-network pharmacy"})

        elif t == ObligationType.MED_COVERED.value:
            med = _med_from(r)
            actions.append(f"Enroll the patient in a patient-assistance/copay program covering {med}, "
                           f"confirmed by the discharge pharmacist (no change to the prescription).")
            if med:
                mutations.append({"scope": "world", "path": f"insurer.coverage.{med}", "value": True,
                                  "description": f"{med} covered via patient-assistance program"})

        elif t == ObligationType.TRANSPORT_CONFIRMED.value:
            actions.append("Confirm transport booking and add a fallback provider.")
            mutations.append({"scope": "world", "path": "transport.booked", "value": True,
                              "description": "Transport booking confirmed"})
            mutations.append({"scope": "world", "path": "transport.fallback", "value": True,
                              "description": "Fallback transport added"})

        elif t == ObligationType.FOLLOWUP_BOOKED.value:
            actions.append("Book and confirm the follow-up appointment (not merely recommend it).")
            mutations.append({"scope": "world", "path": "scheduling.followup_booked", "value": True,
                              "description": "Follow-up appointment booked and confirmed"})

        elif t == ObligationType.INSTRUCTIONS_ACCESSIBLE.value:
            actions.append("Provide discharge instructions translated into the patient's language and "
                           "an accessible format.")
            mutations.append({"scope": "world", "path": "notification.instructions_language",
                              "value": case.world["notification"]["patient_language"],
                              "description": "Instructions translated to patient's language"})
            mutations.append({"scope": "world", "path": "notification.accessible", "value": True,
                              "description": "Instructions provided in an accessible format"})

        elif t == ObligationType.DEPENDENCY_OWNED.value:
            actions.append("Assign a named owner and escalation path to each orphaned dependency.")
            for dep in ["pharmacy", "transport", "followup", "instructions"]:
                if not case.owners.get(dep):
                    mutations.append({"scope": "owners", "path": dep,
                                      "value": "Assigned Care Coordinator (synthetic)",
                                      "description": f"Owner assigned for {dep}"})

    summary = ("Proposed operational remedy (clinician approval required; no clinical changes): "
               + " ".join(actions)) if actions else "No operational remedy available."
    return {"summary": summary, "actions": actions, "mutations": mutations}


def _med_from(r: ObligationResult) -> str:
    # detail begins with "<med>: ..."
    return r.detail.split(":", 1)[0].strip() if ":" in r.detail else ""


def apply_remedy(case: DischargeCase, remedy: dict) -> DischargeCase:
    """Apply an APPROVED remedy's mutations to a (shadow) case and return it."""
    import copy
    from .chaos import _set_world
    twin = copy.deepcopy(case)
    for m in remedy.get("mutations", []):
        if m["scope"] == "world":
            _set_world(twin.world, m["path"], m["value"])
        elif m["scope"] == "owners":
            twin.owners[m["path"]] = m["value"]
    return twin
