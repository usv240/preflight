"""Probe v3: pinpoint the real Data Service entity route.

Strategy: combine /api/Data prefix with /query suffix; treat 400/422 (validation) as "route exists";
and test a nonsense entity to detect an SPA catch-all (which would 405 on everything).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from uipath_client import UiPathClient  # noqa: E402

c = UiPathClient()
ds = c.ds_base()  # .../dataservice_
df = ds.replace("dataservice_", "datafabric_")

E = "DischargeCase"
NONSENSE = "ZzzNoSuchEntity"

tests = [
    ("POST", f"{ds}/api/Data/{E}/query", {}),
    ("POST", f"{ds}/api/Data/{E}", {}),
    ("POST", f"{ds}/api/Data/{E}/insert", {}),
    ("GET",  f"{ds}/api/Data/{E}/query", None),
    ("POST", f"{df}/api/Data/{E}/query", {}),
    ("POST", f"{df}/api/Data/{E}", {}),
    # SPA catch-all detector (compare to the /query 405 we saw):
    ("POST", f"{ds}/{E}/query", {}),
    ("POST", f"{ds}/{NONSENSE}/query", {}),
    ("POST", f"{ds}/api/Data/{NONSENSE}/query", {}),
]

for method, url, body in tests:
    try:
        status, payload = c.request(method, url, body)
    except Exception as e:  # noqa: BLE001
        status, payload = "ERR", str(e)
    short = str(payload)[:140].replace("\n", " ")
    print(f"[{status}] {method} {url.replace(c.base, '')}")
    if short:
        print(f"      -> {short}")
