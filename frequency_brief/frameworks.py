"""Five deterministic day-systems: Chinese Day Master, Tong Shu Day Officer,
Gematria, Kabbalah number, Vaastu Disha Shula."""
import sxtwl
from pyluach import dates

STEMS = ["Jia Yang Wood", "Yi Yin Wood", "Bing Yang Fire", "Ding Yin Fire",
         "Wu Yang Earth", "Ji Yin Earth", "Geng Yang Metal", "Xin Yin Metal",
         "Ren Yang Water", "Gui Yin Water"]
BRANCHES = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
            "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]

OFFICERS = [
    ("Jian", "Establish", "for beginnings"),
    ("Chu", "Remove", "for clearing out"),
    ("Man", "Full", "for gathering"),
    ("Ping", "Balance", "for steady routine"),
    ("Ding", "Settle", "for deciding"),
    ("Zhi", "Grasp", "for holding and signing what is already agreed"),
    ("Po", "Break", "for honest endings"),
    ("Wei", "Delicate", "for care and rest"),
    ("Cheng", "Success", "for completing and launching"),
    ("Shou", "Receive", "for collecting and getting paid"),
    ("Kai", "Open", "for starting and meeting people"),
    ("Bi", "Close", "for sealing and storing"),
]

HEB_LETTERS = [(400, "ת"), (300, "ש"), (200, "ר"), (100, "ק"),
               (90, "צ"), (80, "פ"), (70, "ע"), (60, "ס"),
               (50, "נ"), (40, "מ"), (30, "ל"), (20, "כ"),
               (10, "י"), (9, "ט"), (8, "ח"), (7, "ז"),
               (6, "ו"), (5, "ה"), (4, "ד"), (3, "ג"),
               (2, "ב"), (1, "א")]

GEMATRIA_WORDS = {
    10: ("Yod", "the smallest starting point"),
    13: ("Echad / Ahava", "one, and love"),
    15: ("Yah", "a name of God"),
    17: ("Tov", "good"),
    18: ("Chai", "life"),
    26: ("the divine name", "the divine name"),
}

SEFIROT = {
    1: ("Keter", "pure willingness"),
    2: ("Chokhmah", "the flash of an idea"),
    3: ("Binah", "giving it shape"),
    4: ("Chesed", "loving kindness"),
    5: ("Gevurah", "boundaries"),
    6: ("Tiferet", "the balanced heart"),
    7: ("Netzach", "endurance"),
    8: ("Hod", "gratitude"),
    9: ("Yesod", "the foundation"),
    10: ("Malkhut", "where it lands"),
}

DISHA_SHULA = {
    "Monday": "East", "Saturday": "East",
    "Tuesday": "North", "Wednesday": "North",
    "Thursday": "South",
    "Friday": "West", "Sunday": "West",
}
ALL_DIRS = ["North", "East", "South", "West"]


def hebrew_number(n):
    out = ""
    rem = n
    for val, ch in HEB_LETTERS:
        while rem >= val:
            out += ch
            rem -= val
    out = out.replace("יה", "טו").replace("יו", "טז")
    return out


def verify_anchor():
    d = sxtwl.fromSolar(2000, 1, 1)
    gz = d.getDayGZ()
    return STEMS[gz.tg], BRANCHES[gz.dz]


def compute(y, m, d, weekday):
    res = {}
    stem_name, branch_name = verify_anchor()
    assert stem_name == "Wu Yang Earth" and branch_name == "Horse", \
        f"ANCHOR FAILED: 2000-01-01 came out {stem_name} {branch_name}"

    day = sxtwl.fromSolar(y, m, d)
    dgz = day.getDayGZ()
    mgz = day.getMonthGZ()
    res["day_master"] = {
        "stem": STEMS[dgz.tg],
        "branch": BRANCHES[dgz.dz],
        "stem_idx": dgz.tg,
        "branch_idx": dgz.dz,
    }
    idx = (dgz.dz - mgz.dz) % 12
    p, e, reason = OFFICERS[idx]
    res["officer"] = {"index": idx, "pinyin": p, "english": e, "reason": reason}

    heb = dates.GregorianDate(y, m, d).to_heb()
    res["gematria"] = {
        "heb_day": heb.day,
        "heb_month": heb.month_name(),
        "heb_year": heb.year,
        "letters": hebrew_number(heb.day),
        "word": GEMATRIA_WORDS.get(heb.day),
        "date_str": f"{heb.day} {heb.month_name()} {heb.year}",
    }

    digits = sum(int(c) for c in f"{y:04d}{m:02d}{d:02d}")
    reduced = digits
    while reduced > 9:
        reduced = sum(int(c) for c in str(reduced))
    res["kabbalah"] = {"raw": digits, "number": reduced,
                       "name": SEFIROT[reduced][0], "meaning": SEFIROT[reduced][1]}

    shula = DISHA_SHULA[weekday]
    res["vaastu"] = {"shula": shula,
                     "face": [x for x in ALL_DIRS if x != shula]}
    return res


if __name__ == "__main__":
    import json, sys
    y, m, d = 2026, 9, 16
    print(json.dumps(compute(y, m, d, "Wednesday"), indent=1, ensure_ascii=False))
