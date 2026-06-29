"""Link all Preflight Test Manager test cases to the governing policy Requirement.

Creates traceability: policy obligation -> Test Manager Requirement -> 9 test cases.
The Requirement ("Safe Discharge Readiness Policy", key PRF:10) is created manually in
the Test Manager UI; this script fetches its ID and assigns all project test cases to it.

Usage:
    python integration/requirements_sync.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from uipath_client import UiPathClient  # noqa: E402

REQ_NAME = "Safe Discharge Readiness Policy"
PROJECT_NAME = "Preflight"
TM_SCOPE = "TM.Requirements.Read TM.Requirements.Write TM.TestCases.Read"


def main() -> int:
    c = UiPathClient()
    pid = c.tm_project_id(PROJECT_NAME)
    if not pid:
        print(f"ERROR: project '{PROJECT_NAME}' not found in Test Manager")
        return 1

    # Find the requirement by name
    url = f"{c.tm_api()}/requirements?projectid={pid}"
    st, payload = c.request("GET", url, None, scope=TM_SCOPE)
    if st != 200:
        print(f"ERROR fetching requirements: {st} {payload}")
        return 1

    req = next((r for r in payload.get("data", []) if r.get("name") == REQ_NAME), None)
    if not req:
        print(f"ERROR: requirement '{REQ_NAME}' not found — create it in Test Manager UI first")
        return 1
    req_id = req["id"]
    print(f"Requirement: {REQ_NAME}  id={req_id}")

    # Fetch all test cases in project
    tc_url = f"{c.tm_api()}/testcases?projectid={pid}"
    tc_st, tc_payload = c.request("GET", tc_url, None, scope=TM_SCOPE)
    if tc_st != 200:
        print(f"ERROR fetching test cases: {tc_st}")
        return 1
    tc_ids = [tc["id"] for tc in tc_payload.get("data", [])]
    print(f"Test cases to link: {len(tc_ids)}")

    # Assign all test cases to the requirement
    assign_url = f"{c.tm_api()}/requirements/{req_id}/assigntestcases"
    ast, apayload = c.request("POST", assign_url, {"testCaseIds": tc_ids}, scope=TM_SCOPE)
    if ast == 204:
        print(f"OK: {len(tc_ids)} test cases linked to requirement '{REQ_NAME}'")
    else:
        print(f"ERROR: {ast} {apayload}")
        return 1

    # Verify
    ver_url = f"{c.tm_api()}/testcases?projectid={pid}&requirementid={req_id}"
    vst, vpayload = c.request("GET", ver_url, None, scope=TM_SCOPE)
    linked = len(vpayload.get("data", [])) if vst == 200 else "?"
    print(f"Verified: {linked} test cases now linked to requirement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
