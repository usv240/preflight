# Safe Discharge Readiness Policy (synthetic)

> Synthetic policy for the Preflight prototype. Not a real clinical guideline. It defines **operational
> readiness** obligations only. Preflight never diagnoses, prescribes, or changes medication.

A discharge plan is **operationally ready** only when every obligation below is provably met for the
specific case. Each obligation maps to an executable check (see `engine/evaluator.py` / UiPath Test Cloud).

## P1 — Medication availability (Critical)
Every prescribed medication must be **in stock** at the collection pharmacy at the planned time.
→ Obligation type: `MED_IN_STOCK` (per medication).

## P2 — Medication coverage (Critical)
Every prescribed medication must be **covered** by the patient's plan, or an affordable covered
alternative must be confirmed before discharge.
→ Obligation type: `MED_COVERED` (per medication).

## P3 — Medication is physically collectable (Critical)
The patient must be able to **physically collect** every required medication. The transport's arrival
time at the pharmacy must be **at or before** the pharmacy's closing time on the day of discharge.
→ Obligation type: `MEDICATION_COLLECTABLE` (cross-system: transport arrival vs pharmacy hours).

## P4 — Transport confirmed with fallback (High)
Transportation home must be **confirmed** and have a **fallback** option.
→ Obligation type: `TRANSPORT_CONFIRMED`.

## P5 — Follow-up actually booked (High)
A follow-up appointment must be **booked and confirmed** — not merely recommended.
→ Obligation type: `FOLLOWUP_BOOKED`.

## P6 — Instructions are accessible (High)
Discharge instructions must be in a **language and format the patient/caregiver can act on**.
→ Obligation type: `INSTRUCTIONS_ACCESSIBLE`.

## P7 — Every dependency has a named owner (Medium)
Every unresolved dependency must have a **named owner** and an escalation path so nothing is orphaned.
→ Obligation type: `DEPENDENCY_OWNED`.

## Gate rule
- Any **Critical** obligation failing ⇒ **block** the discharge; route to a human (Action Center).
- A human may approve an operational remedy, edit it, or **accept a documented exception** with
  named accountability. Clinical decisions are out of scope for Preflight.
