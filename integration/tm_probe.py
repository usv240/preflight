"""Probe the Test Manager API: get a TM-scoped token and locate the projects endpoint."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from uipath_client import UiPathClient  # noqa: E402

c = UiPathClient()
tm_scope = c.env.get("UIPATH_TM_SCOPES", "")

# 1) Get a TM-scoped token and show its scopes.
try:
    tok = c.get_token(tm_scope)
    payload = tok.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload))
    print("TM token OK. scopes:", claims.get("scope"))
    print("aud:", claims.get("aud"))
except Exception as e:  # noqa: BLE001
    print("TM token FAILED:", e)
    raise SystemExit(1)

# 2) Probe candidate Test Manager API base paths for listing projects.
base, org, tenant = c.base, c.org, c.tenant
candidates = [
    f"{base}/{org}/{tenant}/testmanager_/api/v1/projects",
    f"{base}/{org}/{tenant}/testmanager_/api/projects",
    f"{base}/{org}/{tenant}/testmanager_/api/v1/Project",
    f"{base}/{org}/{tenant.lower()}/testmanager_/api/v1/projects",
    f"{base}/{org}/{tenant}/testmanager_/api/swagger/v1/swagger.json",
    f"{base}/{org}/{tenant}/testmanager_/swagger/v1/swagger.json",
]
print("\n== Probe Test Manager endpoints ==")
for url in candidates:
    try:
        status, payload = c.request("GET", url, None, scope=tm_scope)
    except Exception as e:  # noqa: BLE001
        status, payload = "ERR", str(e)
    short = str(payload)[:160].replace("\n", " ")
    print(f"[{status}] {url.replace(base, '')}")
    if status == 200 and short:
        print(f"      -> {short}")
