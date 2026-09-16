# -*- coding: utf-8 -*-
"""python -m frequency_brief [--date YYYY-MM-DD] [--location stockholm]"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from . import day, render, sources


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="frequency_brief")
    ap.add_argument("--date", help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--location", default="stockholm",
                    choices=sorted(day.LOCATIONS))
    ap.add_argument("--offline", action="store_true",
                    help="skip the two fetched sources")
    ap.add_argument("--json", action="store_true",
                    help="print the computed day and exit")
    a = ap.parse_args(argv)

    date = dt.date.fromisoformat(a.date) if a.date else None
    field = day.compute_day(date, a.location)

    parsed = dt.date.fromisoformat(field["date"])
    field["_date_label"] = (f"{parsed.strftime('%A')}, "
                            f"{parsed.day} {parsed.strftime('%B %Y')}, "
                            f"{field['location']}")

    if a.json:
        for b in field["timeline"]:
            b.pop("_span", None)
        print(json.dumps(field, indent=1, ensure_ascii=False))
        return 0

    kp = None if a.offline else sources.planetary_kp()
    news = [] if a.offline else sources.headlines()

    path = render.build(field, headlines=news, kp=kp)
    print(f"wrote {path}")
    if kp is None and not a.offline:
        print("no Kp data today, row omitted", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
