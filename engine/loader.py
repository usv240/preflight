"""Load synthetic cases, policy, and help content from the data directory."""

from __future__ import annotations

import json
from pathlib import Path

from .models import DischargeCase, PlanItem

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_case(name: str) -> DischargeCase:
    """Load a case by file stem (e.g., 'golden_case')."""
    path = DATA_DIR / "cases" / f"{name}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    plan_items = [
        PlanItem(type=pi["type"], payload=pi.get("payload", {}), promise_text=pi.get("promise_text", ""))
        for pi in raw.get("plan_items", [])
    ]
    return DischargeCase(
        patient_alias=raw["patient_alias"],
        plan_items=plan_items,
        world=raw["world"],
        owners=raw.get("owners", {}),
    )


def list_cases() -> list[str]:
    return sorted(p.stem for p in (DATA_DIR / "cases").glob("*.json"))


def load_policy() -> str:
    return (DATA_DIR / "policy" / "discharge_policy.md").read_text(encoding="utf-8")


def load_help() -> dict:
    return json.loads((DATA_DIR / "help" / "help_content.json").read_text(encoding="utf-8"))
