"""Tiny standard-library HTTP helper."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.parse
import urllib.request
from typing import Any


class FetchError(RuntimeError):
    pass


def _user_agent() -> str:
    return os.environ.get("AISTACK_RADAR_USER_AGENT", "aistack-radar-skill/0.1")


def _fetch_text_with_urllib(url: str, timeout: float, accept: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": _user_agent(),
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def _fetch_text_with_curl(url: str, timeout: float, accept: str) -> str:
    curl = shutil.which("curl")
    if not curl:
        raise FetchError("urllib failed and curl is not available")
    completed = subprocess.run(
        [
            curl,
            "-fsSL",
            "--max-time",
            str(max(1.0, timeout)),
            "-A",
            _user_agent(),
            "-H",
            f"Accept: {accept}",
            url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or f"curl exited with status {completed.returncode}"
        raise FetchError(message)
    return completed.stdout


def fetch_text(url: str, timeout: float = 8.0, accept: str = "*/*") -> str:
    try:
        return _fetch_text_with_urllib(url, timeout, accept)
    except Exception as urllib_exc:  # pragma: no cover - network dependent
        try:
            return _fetch_text_with_curl(url, timeout, accept)
        except Exception as curl_exc:
            raise FetchError(f"urllib failed: {urllib_exc}; curl failed: {curl_exc}") from curl_exc


def fetch_json(url: str, timeout: float = 8.0) -> Any:
    payload = fetch_text(url, timeout=timeout, accept="application/json")
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise FetchError(f"invalid JSON from {url}") from exc


def urlencode(params: dict[str, str | int]) -> str:
    return urllib.parse.urlencode(params)
