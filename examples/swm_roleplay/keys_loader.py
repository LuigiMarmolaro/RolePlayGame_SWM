"""Auto-load a GCP service-account JSON from the ``keys/`` folder so the game
authenticates to Vertex AI (and bills the project's GCP credits) without
making the user paste anything at the setup screen.

Sets these env vars (Google SDKs and SDialog read them automatically):
- GOOGLE_APPLICATION_CREDENTIALS  → absolute path to the JSON file
- GOOGLE_CLOUD_PROJECT            → from the JSON's ``project_id``
- GOOGLE_CLOUD_LOCATION           → defaults to ``global`` if not set
- GOOGLE_GENAI_USE_VERTEXAI       → ``true`` (route through Vertex AI)
- GOOGLE_API_KEY                  → CLEARED, so the SDK doesn't try API-key auth

Idempotent. Safe to call on every Streamlit rerun. Returns a dict describing
the loaded credential (path / project_id / client_email) or None if no service
account JSON was found.

Looks in (in order):
  examples/swm_roleplay/keys/
  <repo root>/keys/
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict

_HERE = Path(__file__).resolve().parent
_CANDIDATES = [_HERE / "keys", _HERE.parents[1] / "keys"]


def keys_dir() -> Optional[Path]:
    for c in _CANDIDATES:
        if c.is_dir():
            return c
    return None


@lru_cache(maxsize=1)
def load_service_account_credentials() -> Optional[Dict[str, str]]:
    """Find the first ``*.json`` service-account file in ``keys/`` and wire it
    into the environment for Google client libraries.

    Returns a small descriptor dict (path, project_id, client_email) on
    success, or None if nothing usable is present.
    """
    root = keys_dir()
    if root is None:
        return None
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict) or data.get("type") != "service_account":
            continue
        # Wire everything Google SDKs (langchain_google_genai, google-genai,
        # google-auth, langchain-google-vertexai) look for:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path.resolve())
        if data.get("project_id"):
            os.environ.setdefault("GOOGLE_CLOUD_PROJECT", data["project_id"])
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
        # API key would conflict with ADC auth — clear it.
        os.environ.pop("GOOGLE_API_KEY", None)
        return {
            "path": str(path),
            "project_id": data.get("project_id", ""),
            "client_email": data.get("client_email", ""),
        }
    return None
