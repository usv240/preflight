"""Seed Data Fabric with synthetic cases + help content via the API.

Run after the entity endpoint is confirmed in uipath_client.insert_record().
    python integration/seed_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "integration"))

from engine.loader import list_cases, load_case  # noqa: E402
from uipath_client import UiPathClient  # noqa: E402


def case_record(name: str) -> dict:
    case = load_case(name)
    raw = json.loads((ROOT / "data" / "cases" / f"{name}.json").read_text(encoding="utf-8"))
    plan = [{"type": p.type, "promise_text": p.promise_text, "payload": p.payload} for p in case.plan_items]
    return {
        "patientAlias": case.patient_alias,
        "status": "Draft",
        "readinessScore": 0,
        "isShadow": False,
        "parentCaseId": "",
        "planJson": json.dumps(plan, separators=(",", ":")),
        "worldJson": json.dumps(case.world, separators=(",", ":")),
        "ownersJson": json.dumps(case.owners, separators=(",", ":")),
        "note": raw.get("note", ""),
    }


def help_records() -> list[dict]:
    data = json.loads((ROOT / "data" / "help" / "help_content.json").read_text(encoding="utf-8"))
    out = []
    for s in data["screens"]:
        out.append({
            "screenKey": s["screenKey"],
            "title": s["title"],
            "whatItIs": s["whatItIs"],
            "howToUse": s["howToUse"],
            "nextStep": s["nextStep"],
            "tourSteps": json.dumps(s.get("tourSteps", []), separators=(",", ":")),
        })
    return out


def main() -> int:
    c = UiPathClient()

    print("Seeding DischargeCase ...")
    for name in list_cases():
        rec = case_record(name)
        status, payload = c.insert_record("DischargeCase", rec)
        ok = status in (200, 201)
        print(f"  [{status}] {rec['patientAlias']}" + ("" if ok else f"  -> {str(payload)[:200]}"))

    print("Seeding HelpContent ...")
    for rec in help_records():
        status, payload = c.insert_record("HelpContent", rec)
        ok = status in (200, 201)
        print(f"  [{status}] {rec['screenKey']}" + ("" if ok else f"  -> {str(payload)[:200]}"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
