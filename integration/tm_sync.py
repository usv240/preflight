"""Generate Test Manager test cases from a case's compiled obligations.

Demonstrates the Track-3 'turn requirements into test scenarios' step: each outcome obligation becomes a
Test Manager test case in the Preflight project.

    python integration/tm_sync.py [projectName] [patientAlias]
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "integration"))

from engine.compiler import compile_obligations  # noqa: E402
from rehearse_case import GOLDEN, df_record_to_case, find_case  # noqa: E402
from uipath_client import UiPathClient  # noqa: E402


def main() -> int:
    project_name = sys.argv[1] if len(sys.argv) > 1 else "Preflight"
    alias = sys.argv[2] if len(sys.argv) > 2 else GOLDEN
    c = UiPathClient()

    projects = c.tm_projects()
    print("Test Manager projects:", [(p.get("name"), p.get("id") or p.get("key")) for p in projects])
    pid = c.tm_project_id(project_name)
    if not pid:
        print(f"Project '{project_name}' not found. Create it in Test Manager first.")
        return 1
    print("Using project:", project_name, pid)

    rec = find_case(c, alias)
    if not rec:
        print(f"Case '{alias}' not found in Data Fabric"); return 1
    case = df_record_to_case(rec)
    obligations = compile_obligations(case)

    print(f"Creating {len(obligations)} test cases ...")
    for ob in obligations:
        body = {
            "project_id": pid,
            "name": (f"[{ob.severity}] " + ob.text)[:200],
            "description": f"Obligation type: {ob.type}\nOwner: {ob.owner_role}\nParams: {ob.params}",
        }
        st, payload = c.tm_request("POST", "/testcase", body)
        ok = st in (200, 201)
        print(f"  [{st}] {ob.type}" + ("" if ok else f" -> {str(payload)[:160]}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
