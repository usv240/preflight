"""Minimal UiPath Automation Cloud API client (pure standard library).

Handles OAuth client-credentials auth against UiPath Identity and provides helpers to call
Data Service (Data Fabric) entity endpoints. No third-party dependencies.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"

# Cloudflare (in front of UiPath Cloud) blocks the default urllib User-Agent (error 1010),
# so present a normal browser UA.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def load_env(path: Path = ENV_PATH) -> dict[str, str]:
    """Tiny .env loader (KEY=VALUE lines, ignores blanks/comments)."""
    env: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    # allow real environment to override
    for k in ("UIPATH_BASE_URL", "UIPATH_ORG", "UIPATH_TENANT",
              "UIPATH_APP_ID", "UIPATH_APP_SECRET", "UIPATH_SCOPES"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


class UiPathClient:
    def __init__(self, env: dict[str, str] | None = None):
        self.env = env or load_env()
        self.base = self.env["UIPATH_BASE_URL"].rstrip("/")
        self.org = self.env["UIPATH_ORG"]
        self.tenant = self.env["UIPATH_TENANT"]
        self._token: str | None = None

    # ---- auth ----
    def get_token(self) -> str:
        if self._token:
            return self._token
        url = f"{self.base}/identity_/connect/token"
        data = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": self.env["UIPATH_APP_ID"],
            "client_secret": self.env["UIPATH_APP_SECRET"],
            "scope": self.env.get("UIPATH_SCOPES", ""),
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("User-Agent", USER_AGENT)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                payload = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Token request failed {e.code}: {e.read().decode()}") from e
        self._token = payload["access_token"]
        return self._token

    # ---- low-level request ----
    def request(self, method: str, url: str, body: dict | list | None = None) -> tuple[int, object]:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.get_token()}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", USER_AGENT)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode()
                return r.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try:
                parsed = json.loads(raw)
            except Exception:  # noqa: BLE001
                parsed = raw
            return e.code, parsed

    # ---- Data Service helpers (paths confirmed from the entity OpenAPI spec) ----
    def ds_api(self) -> str:
        # The OpenAPI 'servers' URL uses a lowercase tenant segment.
        return f"{self.base}/{self.org}/{self.tenant.lower()}/dataservice_/api"

    def insert_record(self, entity: str, record: dict) -> tuple[int, object]:
        url = f"{self.ds_api()}/EntityService/{entity}/insert"
        return self.request("POST", url, record)

    def insert_batch(self, entity: str, records: list[dict]) -> tuple[int, object]:
        url = f"{self.ds_api()}/EntityService/{entity}/insert-batch"
        return self.request("POST", url, records)

    def read_records(self, entity: str) -> tuple[int, object]:
        url = f"{self.ds_api()}/EntityService/{entity}/read"
        return self.request("GET", url, None)

    # backward-compatible alias
    def ds_base(self) -> str:
        return self.ds_api()


if __name__ == "__main__":
    c = UiPathClient()
    tok = c.get_token()
    print("OK: got access token, length", len(tok))
    print("Token prefix:", tok[:24], "...")
