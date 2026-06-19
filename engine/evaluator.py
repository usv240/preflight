"""Obligation evaluator — the offline stand-in for UiPath Test Cloud execution.

Each obligation type has a check that queries the adapters and returns an ObligationResult with a
human-readable detail and the world facts it depended on (``touched``), which feed the causal chain.
"""

from __future__ import annotations

from .adapters import Adapters, fmt_minutes
from .models import (
    DischargeCase,
    Obligation,
    ObligationResult,
    ObligationStatus,
    ObligationType,
    TestRun,
)


def _result(ob: Obligation, ok: bool, detail: str, touched: list[str]) -> ObligationResult:
    return ObligationResult(
        obligation_id=ob.id,
        obligation_text=ob.text,
        type=ob.type,
        severity=ob.severity,
        status=ObligationStatus.PASS.value if ok else ObligationStatus.FAIL.value,
        detail=detail,
        touched=touched,
    )


def evaluate_obligation(ob: Obligation, case: DischargeCase, ad: Adapters) -> ObligationResult:
    t = ob.type

    if t == ObligationType.MED_IN_STOCK.value:
        med = ob.params["med"]
        ok = ad.pharmacy.is_in_stock(med)
        return _result(ob, ok,
                       f"{med}: {'in stock' if ok else 'OUT OF STOCK'} at {ad.pharmacy.name()}.",
                       [f"pharmacy.stock.{med}"])

    if t == ObligationType.MED_COVERED.value:
        med = ob.params["med"]
        ok = ad.insurer.is_covered(med)
        return _result(ob, ok,
                       f"{med}: {'covered' if ok else 'NOT COVERED'} by plan.",
                       [f"insurer.coverage.{med}"])

    if t == ObligationType.MEDICATION_COLLECTABLE.value:
        arrival = ad.transport.arrival_at_pharmacy()
        close = ad.pharmacy.closes_at()
        ok = arrival <= close
        detail = (f"transport arrives {fmt_minutes(arrival)} "
                  f"(pickup {fmt_minutes(ad.transport.pickup_time())} + {ad.transport.travel_minutes()}m); "
                  f"pharmacy closes {fmt_minutes(close)} -> "
                  f"{'collectable' if ok else 'ARRIVES AFTER CLOSE: medication cannot be collected'}.")
        return _result(ob, ok, detail,
                       ["transport.pickup_time", "transport.travel_minutes", "pharmacy.closes_at"])

    if t == ObligationType.TRANSPORT_CONFIRMED.value:
        ok = ad.transport.is_confirmed() and ad.transport.has_fallback()
        return _result(ob, ok,
                       f"transport booked={ad.transport.is_confirmed()}, fallback={ad.transport.has_fallback()}.",
                       ["transport.booked", "transport.fallback"])

    if t == ObligationType.FOLLOWUP_BOOKED.value:
        ok = ad.scheduling.is_followup_booked()
        return _result(ob, ok,
                       f"follow-up {'booked ' + ad.scheduling.followup_when() if ok else 'NOT BOOKED'}.",
                       ["scheduling.followup_booked"])

    if t == ObligationType.INSTRUCTIONS_ACCESSIBLE.value:
        ok = ad.notification.instructions_accessible()
        return _result(ob, ok,
                       (f"patient language '{ad.notification.patient_language()}' vs instructions "
                        f"'{ad.notification.instructions_language()}' -> "
                        f"{'accessible' if ok else 'NOT ACCESSIBLE'}."),
                       ["notification.patient_language", "notification.instructions_language",
                        "notification.accessible"])

    if t == ObligationType.DEPENDENCY_OWNED.value:
        deps = ob.params.get("dependencies", [])
        missing = [d for d in deps if not case.owners.get(d)]
        ok = not missing
        return _result(ob, ok,
                       "all dependencies owned." if ok else f"MISSING OWNER for: {', '.join(missing)}.",
                       [f"owners.{d}" for d in deps])

    return _result(ob, False, f"unknown obligation type '{t}'", [])


def run_test_set(case: DischargeCase, obligations: list[Obligation], test_set_id: str = "ts_default") -> TestRun:
    """Execute all obligations against the case's current world (= one Test Cloud test run)."""
    ad = Adapters(case.world)
    results = [evaluate_obligation(ob, case, ad) for ob in obligations]
    overall = (ObligationStatus.PASS.value
               if all(r.status == ObligationStatus.PASS.value for r in results)
               else ObligationStatus.FAIL.value)
    return TestRun(case_id=case.id, test_set_id=test_set_id, results=results, overall_status=overall)


def readiness_score(run: TestRun) -> float:
    """Share of obligations passing, 0..100."""
    if not run.results:
        return 0.0
    passed = sum(1 for r in run.results if r.status == ObligationStatus.PASS.value)
    return round(100.0 * passed / len(run.results), 1)
