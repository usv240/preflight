"""Synthetic external-system adapters.

Each class is the offline stand-in for a UiPath **API Workflow** (pharmacy / insurer / transport /
scheduling / notification). They read dependency state from the case's ``world`` dict, which is the same
state the chaos agent mutates. Swapping a stub for a real FHIR/pharmacy/insurer API later is an interface
swap, not a rewrite.
"""

from __future__ import annotations

from typing import Any


def parse_hhmm(value: str) -> int:
    """'17:00' -> minutes since midnight."""
    h, m = value.split(":")
    return int(h) * 60 + int(m)


def fmt_minutes(total: int) -> str:
    return f"{total // 60:02d}:{total % 60:02d}"


class _Adapter:
    def __init__(self, world: dict[str, Any]):
        self.world = world


class PharmacyService(_Adapter):
    def name(self) -> str:
        return self.world["pharmacy"]["name"]

    def is_in_network(self) -> bool:
        return bool(self.world["pharmacy"].get("in_network", False))

    def is_in_stock(self, med: str) -> bool:
        return bool(self.world["pharmacy"].get("stock", {}).get(med, False))

    def opens_at(self) -> int:
        return parse_hhmm(self.world["pharmacy"]["opens_at"])

    def closes_at(self) -> int:
        return parse_hhmm(self.world["pharmacy"]["closes_at"])


class InsurerService(_Adapter):
    def is_covered(self, med: str) -> bool:
        return bool(self.world["insurer"].get("coverage", {}).get(med, False))


class TransportService(_Adapter):
    def is_confirmed(self) -> bool:
        return bool(self.world["transport"].get("booked", False))

    def has_fallback(self) -> bool:
        return bool(self.world["transport"].get("fallback", False))

    def pickup_time(self) -> int:
        return parse_hhmm(self.world["transport"]["pickup_time"])

    def travel_minutes(self) -> int:
        return int(self.world["transport"].get("travel_minutes", 0))

    def arrival_at_pharmacy(self) -> int:
        """When the patient actually reaches the pharmacy."""
        return self.pickup_time() + self.travel_minutes()


class SchedulingService(_Adapter):
    def is_followup_booked(self) -> bool:
        return bool(self.world["scheduling"].get("followup_booked", False))

    def followup_when(self) -> str:
        return self.world["scheduling"].get("followup_when", "")


class NotificationService(_Adapter):
    def instructions_accessible(self) -> bool:
        n = self.world["notification"]
        language_match = n.get("patient_language") == n.get("instructions_language")
        return bool(language_match and n.get("accessible", False))

    def patient_language(self) -> str:
        return self.world["notification"].get("patient_language", "")

    def instructions_language(self) -> str:
        return self.world["notification"].get("instructions_language", "")


class Adapters:
    """Bundle of all adapters bound to one case's world."""

    def __init__(self, world: dict[str, Any]):
        self.pharmacy = PharmacyService(world)
        self.insurer = InsurerService(world)
        self.transport = TransportService(world)
        self.scheduling = SchedulingService(world)
        self.notification = NotificationService(world)
