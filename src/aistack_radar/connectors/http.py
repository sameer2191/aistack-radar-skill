"""Tiny standard-library HTTP helper."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any


class FetchError(RuntimeError):
    pass


def fetch_json(url: str, timeout: float = 8.0) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": os.environ.get("AISTACK_RADAR_USER_AGENT", "aistack-radar-skill/0.1"),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except Exception as exc:  # pragma: no cover - network dependent
        raise FetchError(str(exc)) from exc
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise FetchError(f"invalid JSON from {url}") from exc


def urlencode(params: dict[str, str | int]) -> str:
    return urllib.parse.urlencode(params)

