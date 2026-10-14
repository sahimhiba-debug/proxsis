"""Public AI key lookup. The key is never written to a file, a log or a result.

Order: environment variable ``PUBLICAI_API_KEY``, then (macOS only) the login
keychain, service :data:`KEYCHAIN_SERVICE`. To store it once in the keychain::

    security add-generic-password -a "$USER" -s proxsis-publicai -w

(``-w`` without a value prompts for it, so it never reaches the shell history.)
"""

from __future__ import annotations

import os
import subprocess
import sys

KEYCHAIN_SERVICE = "proxsis-publicai"


def publicai_api_key() -> str | None:
    key = os.environ.get("PUBLICAI_API_KEY")
    if key:
        return key
    if sys.platform != "darwin":
        return None
    try:
        res = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
                             capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = (res.stdout or "").strip()
    return value if res.returncode == 0 and value else None
