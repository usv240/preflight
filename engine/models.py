"""Domain models for Preflight.

These dataclasses mirror the UiPath Data Service entities described in IMPLEMENTATION_PLAN.md (section 3).
Keeping them as plain dataclasses lets the offline engine run anywhere while staying a faithful blueprint
for the Data Service schema.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CaseStatus(str, Enum):
    DRAFT = "Draft"
    REHEARSAL_RUNNING = "RehearsalRunning"
    BLOCKED = "Blocked"
    AWAITING_HUMAN = "AwaitingHuman"
    VERIFIED = "Verified"
    RELEASED = "Released"
    ERROR = "Error"


class ObligationStatus(str, Enum):
    PENDING = "Pending"
    PASS = "Pass"
    FAIL = "Fail"


class Severity(str, Enum):
    CRITICAL = "Critical"   # under-met => block, never auto-waivable
    HIGH = "High"
    MEDIUM = "Medium"


class Decision(str, Enum):
    APPROVE_REMEDY = "ApproveRemedy"
    EDIT_REMEDY = "EditRemedy"
    ACCEPT_EXCEPTION = "AcceptException"
    REJECT = "Reject"


# Obligation type keys — each maps to an evaluator function (see evaluator.py).
class ObligationType(str, Enum):
    MED_IN_STOCK = "MED_IN_STOCK"
    MED_COVERED = "MED_COVERED"
    MEDICATION_COLLECTABLE = "MEDICATION_COLLECTABLE"  # cross-system: transport arrival vs pharmacy hours
    TRANSPORT_CONFIRMED = "TRANSPORT_CONFIRMED"
    FOLLOWUP_BOOKED = "FOLLOWUP_BOOKED"
    INSTRUCTIONS_ACCESSIBLE = "INSTRUCTIONS_ACCESSIBLE"
    DEPENDENCY_OWNED = "DEPENDENCY_OWNED"


@dataclass
class PlanItem:
    """A promise made in the discharge plan (the raw material the compiler turns into obligations)."""
    type: str                  # med | pharmacy | transport | followup | instructions
    payload: dict[str, Any]
    promise_text: str
    id: str = field(default_factory=lambda: _new_id("plan"))


@dataclass
class Obligation:
    """An executable outcome obligation — the unit Test Cloud proves."""
    text: str
    type: str                  # ObligationType value
    params: dict[str, Any]
    severity: str              # Severity value
    owner_role: str
    case_id: str = ""
    status: str = ObligationStatus.PENDING.value
    detail: str = ""           # human-readable evaluation result
    touched: list[str] = field(default_factory=list)  # world facts this obligation depended on
    id: str = field(default_factory=lambda: _new_id("obl"))


@dataclass
class DischargeCase:
    """A discharge case = patient + plan + the world state its dependencies live in. Fully synthetic."""
    patient_alias: str
    plan_items: list[PlanItem]
    world: dict[str, Any]                 # dependency state: pharmacy hours, med stock, coverage, transport...
    owners: dict[str, str] = field(default_factory=dict)  # dependency -> named owner (operational accountability)
    is_shadow: bool = False
    parent_case_id: str | None = None
    status: str = CaseStatus.DRAFT.value
    readiness_score: float = 0.0
    id: str = field(default_factory=lambda: _new_id("case"))
    created_at: str = field(default_factory=_now_iso)

    def clone_as_shadow(self) -> "DischargeCase":
        """Fork reality: a disposable twin of THIS case (deep-ish copy of plan + world)."""
        import copy
        twin = DischargeCase(
            patient_alias=self.patient_alias,
            plan_items=copy.deepcopy(self.plan_items),
            world=copy.deepcopy(self.world),
            owners=dict(self.owners),
            is_shadow=True,
            parent_case_id=self.id,
            status=CaseStatus.REHEARSAL_RUNNING.value,
        )
        return twin


@dataclass
class ObligationResult:
    obligation_id: str
    obligation_text: str
    type: str
    severity: str
    status: str                # Pass | Fail
    detail: str
    touched: list[str] = field(default_factory=list)


@dataclass
class ChaosScenario:
    """What the chaos/red-team agent tried and the causal chain it surfaced."""
    case_id: str
    description: str
    mutations: list[dict[str, Any]]
    result: str                            # "obligation_failed" | "survived"
    failed_obligations: list[str] = field(default_factory=list)
    causal_chain: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: _new_id("chaos"))


@dataclass
class TestRun:
    case_id: str
    test_set_id: str
    results: list[ObligationResult]
    overall_status: str                    # Pass | Fail
    started_at: str = field(default_factory=_now_iso)
    finished_at: str = field(default_factory=_now_iso)
    id: str = field(default_factory=lambda: _new_id("run"))


@dataclass
class HumanDecision:
    case_id: str
    proposed_remedy: dict[str, Any]
    decision: str                          # Decision value
    approver_alias: str
    note: str = ""
    timestamp: str = field(default_factory=_now_iso)
    id: str = field(default_factory=lambda: _new_id("dec"))


@dataclass
class EvidencePack:
    case_id: str
    verdict: str                           # green | red
    obligation_results: list[ObligationResult]
    causal_chains: list[list[str]]
    audit_trail: list[str]
    readiness_score: float
    id: str = field(default_factory=lambda: _new_id("evid"))
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RegressionScenario:
    """A resolved failure promoted into a reusable standing test (the 'learn' step)."""
    source_case_id: str
    pattern: dict[str, Any]
    id: str = field(default_factory=lambda: _new_id("reg"))
    created_at: str = field(default_factory=_now_iso)
