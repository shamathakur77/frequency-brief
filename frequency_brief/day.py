# -*- coding: utf-8 -*-
"""Everything the card needs for one date and place, computed locally.

No network. No lookups. Swiss Ephemeris positions plus the traditional
day-division tables, which are arithmetic on that date's own daylight.
"""
from __future__ import annotations

import datetime as dt
import math
from zoneinfo import ZoneInfo

import swisseph as swe

from . import frameworks

# ---------------------------------------------------------------- locations

LOCATIONS = {
    "stockholm": ("Stockholm", 59.3293, 18.0686, "Europe/Stockholm"),
    "nashik": ("Nashik", 19.9975, 73.7898, "Asia/Kolkata"),
    "pune": ("Pune", 18.5204, 73.8567, "Asia/Kolkata"),
}

# ------------------------------------------------------------ vedic windows
# The day from sunrise to sunset is cut into eight equal parts. Each tradition
# claims a numbered part, and which number depends on the weekday. Monday = 0.

RAHU = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
YAMA = {0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6, 6: 5}
GULIKA = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}

NAKSHATRA = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]

TITHI = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima",
]

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Human Design wheel, starting at Gate 41 which begins at 302 degrees tropical.
HD_WHEEL = [41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3, 27,
            24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56, 31, 33,
            7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50, 28, 44, 1, 43,
            14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60]
HD_START = 302.0
HD_ARC = 360.0 / 64.0  # 5.625


def _jd(moment: dt.datetime) -> float:
    u = moment.astimezone(dt.timezone.utc)
    return swe.julday(u.year, u.month, u.day,
                      u.hour + u.minute / 60 + u.second / 3600)


def _rise(jd_start: float, lat: float, lon: float, rsmi: int) -> float:
    # rsmi carries ONLY the rise/set bits. FLG_SWIEPH shares a value with
    # CALC_SET, so folding it in here silently turns every rise into a set.
    res = swe.rise_trans(jd_start, swe.SUN, rsmi, (lon, lat, 0.0),
                         flags=swe.FLG_SWIEPH)
    tret = res[1]
    return tret[0] if isinstance(tret, (list, tuple)) else tret


def _local(jd: float, tz: ZoneInfo) -> dt.datetime:
    y, m, d, h = swe.revjul(jd)
    base = dt.datetime(y, m, d, tzinfo=dt.timezone.utc)
    return (base + dt.timedelta(hours=h)).astimezone(tz)


def _hm(moment: dt.datetime) -> str:
    return moment.strftime("%H:%M")


def _round_min(moment: dt.datetime) -> dt.datetime:
    """Nearest whole minute. Every printed time derives from these, so the
    segment boundaries always add up to the sunrise and sunset on the card."""
    m = moment.replace(second=0, microsecond=0)
    return m + dt.timedelta(minutes=1) if moment.second >= 30 else m


def compute_day(date: dt.date | None = None, location: str = "stockholm") -> dict:
    """Return every value the card renders, for one date and place."""
    name, lat, lon, tzname = LOCATIONS[location]
    tz = ZoneInfo(tzname)
    date = date or dt.datetime.now(tz).date()

    midnight = dt.datetime(date.year, date.month, date.day, tzinfo=tz)
    jd0 = _jd(midnight)

    jd_rise = _rise(jd0, lat, lon, swe.CALC_RISE)
    sunrise = _round_min(_local(jd_rise, tz))
    sunset = _round_min(_local(_rise(jd0, lat, lon, swe.CALC_SET), tz))
    if sunset <= sunrise:                       # set belongs to the next day
        sunset = _round_min(_local(_rise(jd0 + 0.5, lat, lon, swe.CALC_SET), tz))

    daylight = (sunset - sunrise).total_seconds() / 60.0
    part = daylight / 8.0
    weekday = date.weekday()                    # Monday = 0

    def segment(n: int) -> tuple[dt.datetime, dt.datetime]:
        return (sunrise + dt.timedelta(minutes=part * (n - 1)),
                sunrise + dt.timedelta(minutes=part * n))

    windows = {
        "rahu": segment(RAHU[weekday]),
        "yamaganda": segment(YAMA[weekday]),
        "gulika": segment(GULIKA[weekday]),
    }

    # Abhijit: one fifteenth of the daylight, centred on solar noon. It is not
    # observed on Wednesdays, and it is dropped if it sits inside Rahu Kalam.
    noon = sunrise + dt.timedelta(minutes=daylight / 2)
    half = daylight / 30.0
    abhijit = None
    if weekday != 2:
        a, b = (noon - dt.timedelta(minutes=half), noon + dt.timedelta(minutes=half))
        r0, r1 = windows["rahu"]
        if not (a >= r0 and b <= r1):
            abhijit = (a, b)

    timeline = _timeline(sunrise, sunset, windows)

    # ---- sky ------------------------------------------------------------
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    sun_lon = swe.calc_ut(jd_rise, swe.SUN)[0][0]
    moon_lon = swe.calc_ut(jd_rise, swe.MOON)[0][0]
    ayan = swe.get_ayanamsa_ut(jd_rise)

    elong = (moon_lon - sun_lon) % 360.0
    tithi_n = int(elong // 12) + 1
    paksha = "Shukla" if tithi_n <= 15 else "Krishna"
    tithi_name = ("Amavasya" if tithi_n == 30 else
                  TITHI[(tithi_n - 1) % 15])

    sid_moon = (moon_lon - ayan) % 360.0
    nak_i = int(sid_moon // (360 / 27))
    pada = int(((sid_moon % (360 / 27)) / (360 / 27)) * 4) + 1

    illum = swe.pheno_ut(jd_rise, swe.MOON)[1] * 100.0

    gate_i = int(((sun_lon - HD_START) % 360.0) / HD_ARC)
    gate_start = (HD_START + gate_i * HD_ARC) % 360.0
    line = int((((sun_lon - gate_start) % 360.0) / HD_ARC) * 6) + 1

    # ---- the other five systems -----------------------------------------
    fw = frameworks.compute(date.year, date.month, date.day,
                            date.strftime("%A"))

    return {
        "date": date.isoformat(),
        "weekday": date.strftime("%A"),
        "location": name,
        "timezone": tzname,
        "sunrise": _hm(sunrise),
        "sunset": _hm(sunset),
        "daylight_minutes": round(daylight, 1),
        "timeline": timeline,
        "abhijit": None if abhijit is None else
                   {"start": _hm(abhijit[0]), "end": _hm(abhijit[1]),
                    "minutes": round((abhijit[1] - abhijit[0]).total_seconds() / 60)},
        "longest_clear": _longest_clear(timeline),
        "astro": {
            "tithi_number": tithi_n,
            "tithi_name": tithi_name,
            "paksha": paksha,
            "nakshatra": NAKSHATRA[nak_i],
            "nakshatra_pada": pada,
            "moon_sign_tropical": SIGNS[int(moon_lon // 30)],
            "moon_illumination_percent": round(illum, 1),
            "moon_growing": elong < 180.0,
            "human_design_sun": {"gate": HD_WHEEL[gate_i], "line": line},
        },
        "systems": fw,
    }


def _timeline(sunrise, sunset, windows) -> list[dict]:
    """Ordered, gapless list of coloured blocks from sunrise to sunset."""
    marked = sorted(
        [(windows["rahu"][0], windows["rahu"][1], "rest", "Rahu Kalam", "red"),
         (windows["yamaganda"][0], windows["yamaganda"][1], "coast", "Yamaganda", "yellow"),
         (windows["gulika"][0], windows["gulika"][1], "coast", "Gulika", "yellow")],
        key=lambda w: w[0])

    out, cursor = [], sunrise
    for start, end, key, label, token in marked:
        if start > cursor:
            out.append({"start": _hm(cursor), "end": _hm(start), "key": "go",
                        "label": "Open", "token": "green",
                        "_span": (cursor, start)})
        out.append({"start": _hm(start), "end": _hm(end), "key": key,
                    "label": label, "token": token, "_span": (start, end)})
        cursor = end
    if cursor < sunset:
        out.append({"start": _hm(cursor), "end": _hm(sunset), "key": "go",
                    "label": "Open", "token": "green", "_span": (cursor, sunset)})
    return out


def _longest_clear(timeline) -> dict:
    best = max((b for b in timeline if b["token"] == "green"),
               key=lambda b: (b["_span"][1] - b["_span"][0]))
    span = best["_span"][1] - best["_span"][0]
    return {"start": best["start"], "end": best["end"],
            "minutes": round(span.total_seconds() / 60)}


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--location", default="stockholm")
    a = ap.parse_args()
    d = dt.date.fromisoformat(a.date) if a.date else None
    out = compute_day(d, a.location)
    for b in out["timeline"]:
        b.pop("_span", None)
    print(json.dumps(out, indent=1, ensure_ascii=False))
