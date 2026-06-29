"""Generate Data Fabric import CSVs from the synthetic case files.

Produces one CSV per target entity with headers matching the Data Fabric field *Names*.
JSON values are embedded as single cells (csv module handles quote-escaping).

Usage:
    python scripts/make_seed_csv.py
Outputs to: data/seed/*.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.loader import list_cases, load_case  # noqa: E402

OUT = ROOT / "data" / "seed"
OUT.mkdir(parents=True, exist_ok=True)


def plan_items_payload(case) -> list[dict]:
    return [{"type": p.type, "promise_text": p.promise_text, "payload": p.payload} for p in case.plan_items]


def main() -> int:
    rows = []
    for name in list_cases():
        case = load_case(name)
        note = ""
        # recover the note from the raw file (loader drops it)
        raw = json.loads((ROOT / "data" / "cases" / f"{name}.json").read_text(encoding="utf-8"))
        note = raw.get("note", "")
        rows.append({
            "patientAlias": case.patient_alias,
            "status": "Draft",
            "readinessScore": 0,
            "isShadow": "false",
            "parentCaseId": "",
            "planJson": json.dumps(plan_items_payload(case), separators=(",", ":")),
            "worldJson": json.dumps(case.world, separators=(",", ":")),
            "ownersJson": json.dumps(case.owners, separators=(",", ":")),
            "note": note,
        })

    headers = ["patientAlias", "status", "readinessScore", "isShadow",
               "parentCaseId", "planJson", "worldJson", "ownersJson", "note"]
    path = OUT / "DischargeCase_seed.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote {len(rows)} rows -> {path}")
    for r in rows:
        print(f"  - {r['patientAlias']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
