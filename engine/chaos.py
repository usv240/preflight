"""Chaos / red-team agent.

The adversarial core (the "Crucible" engine). It (1) detects latent failures already present in the
plan, and (2) searches realistic dependency mutations — singly and in combination — for cascading
failures a fixed script would miss, emitting a causal chain for each. This is the offline stand-in for
the UiPath **coded agent** (optionally a CrewAI/LangChain agent governed by UiPath).
"""

from __future__ import annotations

import copy

from .adapters import Adapters, fmt_minutes
from .evaluator import run_test_set
from .models import ChaosScenario, DischargeCase, Obligation, ObligationResult, ObligationStatus, ObligationType


def _set_world(world: dict, dotted: str, value) -> None:
    node = world
    parts = dotted.split(".")
    for p in parts[:-1]:
        node = node[p]
    node[parts[-1]] = value


def candidate_mutations(case: DischargeCase) -> list[dict]:
    """Realistic real-world perturbations the chaos agent hypothesizes for THIS case."""
    muts: list[dict] = []
    meds = case.world.get("meds", [])

    # transport gets delayed (traffic / earlier-patient overrun)
    muts.append({"scope": "world", "path": "transport.travel_minutes",
                 "value": case.world["transport"]["travel_minutes"] + 30,
                 "description": "Transport delayed +30 min (traffic)"})
    # pharmacy closes earlier than planned (staffing)
    muts.append({"scope": "world", "path": "pharmacy.closes_at", "value": "16:00",
                 "description": "Pharmacy closes early at 16:00 (staffing)"})
    # transport fallback falls through
    muts.append({"scope": "world", "path": "transport.fallback", "value": False,
                 "description": "Transport fallback unavailable"})
    # follow-up silently not booked
    muts.append({"scope": "world", "path": "scheduling.followup_booked", "value": False,
                 "description": "Follow-up appointment not actually booked"})
    # instructions language mismatch
    muts.append({"scope": "world", "path": "notification.instructions_language", "value": "zz",
                 "description": "Discharge instructions in the wrong language"})
    for med in meds:
        muts.append({"scope": "world", "path": f"pharmacy.stock.{med}", "value": False,
                     "description": f"Medication {med} goes out of stock"})
        muts.append({"scope": "world", "path": f"insurer.coverage.{med}", "value": False,
                     "description": f"Insurer denies coverage for {med}"})
    return muts


def _apply(case: DischargeCase, mutations: list[dict]) -> DischargeCase:
    twin = copy.deepcopy(case)
    for m in mutations:
        if m["scope"] == "world":
            _set_world(twin.world, m["path"], m["value"])
        elif m["scope"] == "owners":
            twin.owners[m["path"]] = m["value"]
    return twin


def build_causal_chain(result: ObligationResult, world: dict) -> list[str]:
    """Trace WHY an obligation failed into a readable dependency chain."""
    ad = Adapters(world)
    t = result.type
    if t == ObligationType.MEDICATION_COLLECTABLE.value:
        arrival = ad.transport.arrival_at_pharmacy()
        close = ad.pharmacy.closes_at()
        return [
            f"Transport pickup {fmt_minutes(ad.transport.pickup_time())} + "
            f"{ad.transport.travel_minutes()}m travel -> arrival {fmt_minutes(arrival)}",
            f"Pharmacy '{ad.pharmacy.name()}' closes {fmt_minutes(close)}",
            f"Arrival {fmt_minutes(arrival)} is AFTER close {fmt_minutes(close)} -> medication not collectable",
            "Required medication unavailable at home -> discharge NOT operationally ready",
        ]
    if t == ObligationType.MED_IN_STOCK.value:
        return [result.detail, "Medication cannot be dispensed at collection",
                "Discharge NOT operationally ready"]
    if t == ObligationType.MED_COVERED.value:
        return [result.detail, "Patient may be unable to obtain medication without a covered alternative",
                "Discharge NOT operationally ready"]
    if t == ObligationType.TRANSPORT_CONFIRMED.value:
        return [result.detail, "Patient may have no reliable way home",
                "Discharge NOT operationally ready"]
    if t == ObligationType.FOLLOWUP_BOOKED.value:
        return [result.detail, "No confirmed continuity of care after discharge",
                "Discharge NOT operationally ready"]
    if t == ObligationType.INSTRUCTIONS_ACCESSIBLE.value:
        return [result.detail, "Patient/caregiver cannot act on discharge instructions",
                "Discharge NOT operationally ready"]
    if t == ObligationType.DEPENDENCY_OWNED.value:
        return [result.detail, "Orphaned dependency with no accountable owner",
                "Discharge NOT operationally ready"]
    return [result.detail, "Discharge NOT operationally ready"]


def _failed(results: list[ObligationResult]) -> list[ObligationResult]:
    return [r for r in results if r.status == ObligationStatus.FAIL.value]


def search(case: DischargeCase, obligations: list[Obligation]) -> tuple[list[ChaosScenario], list[str]]:
    """Return (scenarios, log_lines). Scenarios capture latent + mutation-induced failures."""
    scenarios: list[ChaosScenario] = []
    log: list[str] = []

    # (1) Latent failures already present in the plan (no mutation needed).
    baseline = run_test_set(case, obligations)
    baseline_failed = _failed(baseline.results)
    for r in baseline_failed:
        chain = build_causal_chain(r, case.world)
        scenarios.append(ChaosScenario(
            case_id=case.id,
            description="Latent flaw in the plan (no mutation needed)",
            mutations=[],
            result="obligation_failed",
            failed_obligations=[r.obligation_text],
            causal_chain=chain,
        ))
        log.append(f"[chaos] LATENT FAILURE: {r.obligation_text} | {' -> '.join(chain)}")

    baseline_failed_ids = {r.obligation_id for r in baseline_failed}

    # (2) Single-mutation search: which perturbations NEWLY break the plan?
    for m in candidate_mutations(case):
        twin = _apply(case, [m])
        run = run_test_set(twin, obligations)
        new_fails = [r for r in _failed(run.results) if r.obligation_id not in baseline_failed_ids]
        if new_fails:
            for r in new_fails:
                scenarios.append(ChaosScenario(
                    case_id=case.id,
                    description=f"Mutation: {m['description']}",
                    mutations=[m],
                    result="obligation_failed",
                    failed_obligations=[r.obligation_text],
                    causal_chain=build_causal_chain(r, twin.world),
                ))
            log.append(f"[chaos] mutation breaks plan: {m['description']} -> "
                       f"{len(new_fails)} new failure(s)")
        else:
            log.append(f"[chaos] survived mutation: {m['description']}")

    # (3) One targeted 2-combination to demonstrate cascade search (delay + early close).
    combo = [
        {"scope": "world", "path": "transport.travel_minutes",
         "value": case.world["transport"]["travel_minutes"] + 10,
         "description": "Transport delayed +10 min"},
        {"scope": "world", "path": "pharmacy.closes_at", "value": "16:30",
         "description": "Pharmacy closes 30 min early"},
    ]
    twin = _apply(case, combo)
    run = run_test_set(twin, obligations)
    new_fails = [r for r in _failed(run.results) if r.obligation_id not in baseline_failed_ids]
    if new_fails:
        for r in new_fails:
            scenarios.append(ChaosScenario(
                case_id=case.id,
                description="Combination: minor transport delay + early pharmacy close (cascade)",
                mutations=combo,
                result="obligation_failed",
                failed_obligations=[r.obligation_text],
                causal_chain=build_causal_chain(r, twin.world),
            ))
        log.append("[chaos] COMBINATION cascade found: small delay + early close together break collectability")
    else:
        log.append("[chaos] combination survived: small delay + early close")

    return scenarios, log
