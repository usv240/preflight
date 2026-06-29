"""Probe Orchestrator test-automation API: folders, test sets, test cases, executions."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from uipath_client import UiPathClient  # noqa: E402

c = UiPathClient()
ORCH = "OR.Execution OR.TestSets OR.TestSetExecutions OR.Jobs OR.Folders OR.Robots OR.Monitoring OR.Settings"
base = f"{c.base}/{c.org}/{c.tenant}/orchestrator_"


def get(url, hdr=None):
    try:
        return c.request("GET", url, None, scope=ORCH, extra_headers=hdr)
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e)


# 1) Folders
st, folders = get(f"{base}/odata/Folders")
fl = folders.get("value", []) if isinstance(folders, dict) else []
print(f"[{st}] Folders: {len(fl)}")
for f in fl:
    print(f"    id={f.get('Id')}  name={f.get('FullyQualifiedName') or f.get('DisplayName')}")
if not fl:
    print("  no folders; cannot continue test-automation probe"); raise SystemExit(0)

fid = str(fl[0]["Id"])
hdr = {"X-UIPATH-OrganizationUnitId": fid}
print(f"\nUsing folder id={fid}\n")

# 2) Test automation resources (folder-scoped)
for path in ["/odata/TestSets", "/odata/TestCases", "/odata/TestSetExecutions",
             "/odata/TestCaseExecutions"]:
    st, payload = get(f"{base}{path}", hdr)
    n = payload.get("@odata.count", payload.get("value") and len(payload["value"])) if isinstance(payload, dict) else "?"
    cnt = len(payload.get("value", [])) if isinstance(payload, dict) else "?"
    print(f"[{st}] {path}  -> {cnt} record(s)")

# 3) TestAutomation controller (for external result reporting)
print("\n== TestAutomation controller probes ==")
for path in ["/api/TestAutomation/GetAssignedTestSets",
             "/api/TestAutomation/CreateTestSetForReleaseVersion",
             "/api/TestAutomation/StartTestSetExecution"]:
    st, payload = get(f"{base}{path}", hdr)
    print(f"[{st}] GET {path}  -> {str(payload)[:90]}")
