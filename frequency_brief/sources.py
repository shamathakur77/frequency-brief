# -*- coding: utf-8 -*-
"""The two fetched inputs. Both fail to None rather than to a guess."""
from __future__ import annotations

import json
import pathlib
import re
import urllib.error
import urllib.request

SWPC = "https://services.swpc.noaa.gov/text/3-day-forecast.txt"
KP_ROW = re.compile(r"^(\d{2}-\d{2}UT)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)")


def planetary_kp(timeout: float = 10.0, column: int = 0) -> dict | None:
    """Highest forecast Kp for one of the three days, or None.

    `column` is 0 for the first forecast day. Returns None on any failure,
    which the card renders as an omitted row rather than a plausible number.
    """
    try:
        with urllib.request.urlopen(SWPC, timeout=timeout) as r:
            text = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return None

    values = []
    for line in text.splitlines():
        m = KP_ROW.match(line.strip())
        if m:
            try:
                values.append(float(m.group(2 + column)))
            except (ValueError, IndexError):
                continue
    if not values:
        return None

    peak = max(values)
    level = "quiet" if peak < 4 else ("unsettled" if peak < 5 else "storm level")
    return {"peak": peak,
            "text": f"Kp {peak:g} today, {level}.",
            "source": "NOAA SWPC"}


def headlines(path: str = "headlines.json") -> list[dict]:
    """Optional local file: [{"text": "...", "source": "Outlet"}, ...].

    There is no default news provider, because a headline the card cannot
    attribute is a headline the card should not print. Absent file, no row.
    """
    p = pathlib.Path(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError:
        return []
    return [h for h in data
            if isinstance(h, dict) and h.get("text") and h.get("source")][:3]
