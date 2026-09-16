# -*- coding: utf-8 -*-
"""Wording tables. Values in, plain sentences out.

Rules these follow, because they are what make the card readable at 7am:
plain word first and the tradition name second, sentences under twelve words,
and a window is always described by what it is FOR, never as dangerous.
"""

# The Tong Shu day officer sets the headline. It is the strongest single
# signal about what a date is shaped for, so it leads.
OFFICER = {
    "Jian":  ("Today is a", "starting day.", "Begin it. Do not perfect it.",
              "Start it.", "a Jian Establish day, for beginnings"),
    "Chu":   ("Today is a", "clearing day.", "Delete before you add.",
              "Clear it out.", "a Chu Remove day, for clearing out"),
    "Man":   ("Today is a", "gathering day.", "Collect. Do not spend.",
              "Gather it in.", "a Man Full day, for gathering"),
    "Ping":  ("Today is a", "steady day.", "Keep the routine. Add nothing.",
              "Hold the routine.", "a Ping Balance day, for steady routine"),
    "Ding":  ("Today is a", "deciding day.", "Choose one. Then stop looking.",
              "Decide it.", "a Ding Settle day, for deciding"),
    "Zhi":   ("Today is a", "signing day.", "Sign what is already agreed.",
              "Sign it.", "a Zhi Grasp day, for holding and signing"),
    "Po":    ("Today is an", "ending day.", "Close it honestly.",
              "End it cleanly.", "a Po Break day, for honest endings"),
    "Wei":   ("Today is a", "careful day.", "Go slow. Rest counts as work.",
              "Handle with care.", "a Wei Delicate day, for care and rest"),
    "Cheng": ("Today is a", "shipping day.", "Finish something. Then send it.",
              "Finish it.", "a Cheng Success day, for completing"),
    "Shou":  ("Today is a", "collecting day.", "Invoice. Follow up. Get paid.",
              "Collect it.", "a Shou Receive day, for getting paid"),
    "Kai":   ("Today is an", "opening day.", "Meet people. Say yes.",
              "Open the door.", "a Kai Open day, for starting and meeting"),
    "Bi":    ("Today is a", "sealing day.", "File it. Store it. Stop.",
              "Seal it.", "a Bi Close day, for sealing and storing"),
}

# Day stem, by element and polarity, gives the manner of working.
STEM = {
    "Jia Yang Wood":  "Push forward.",
    "Yi Yin Wood":    "Bend, do not break.",
    "Bing Yang Fire": "Go loud.",
    "Ding Yin Fire":  "Keep the small flame.",
    "Wu Yang Earth":  "Stand still.",
    "Ji Yin Earth":   "Tend the details.",
    "Geng Yang Metal": "Cut cleanly.",
    "Xin Yin Metal":  "Refine it.",
    "Ren Yang Water": "Move fast.",
    "Gui Yin Water":  "Work quiet.",
}

BRANCH_NOTE = {
    "Rat": "quick and resourceful", "Ox": "slow and sure",
    "Tiger": "bold", "Rabbit": "diplomatic", "Dragon": "expansive",
    "Snake": "sharp focus", "Horse": "restless", "Goat": "forgiving",
    "Monkey": "inventive", "Rooster": "precise", "Dog": "loyal",
    "Pig": "generous",
}

# One command per nakshatra. Kept plain, and never a warning.
NAKSHATRA = {
    "Ashwini": "Move first.", "Bharani": "Carry the weight.",
    "Krittika": "Cut what is dull.", "Rohini": "Grow something.",
    "Mrigashira": "Go looking.", "Ardra": "Let it change.",
    "Punarvasu": "Return and retry.", "Pushya": "Feed the work.",
    "Ashlesha": "Hold your counsel.", "Magha": "Honour the ones before.",
    "Purva Phalguni": "Enjoy the making.", "Uttara Phalguni": "Make the pact.",
    "Hasta": "Use your hands.", "Chitra": "Build it beautiful.",
    "Swati": "Go your own way.", "Vishakha": "Aim at one goal.",
    "Anuradha": "Keep the friendship.", "Jyeshtha": "Take the lead.",
    "Mula": "Get to the root.", "Purva Ashadha": "Keep your nerve.",
    "Uttara Ashadha": "Finish what lasts.", "Shravana": "Listen first.",
    "Dhanishta": "Keep the rhythm.", "Shatabhisha": "Mend it.",
    "Purva Bhadrapada": "Ask the hard question.",
    "Uttara Bhadrapada": "Go still.", "Revati": "See it home.",
}

SEFIRAH = {
    1: "Just be willing.", 2: "Catch the idea.", 3: "Give it shape.",
    4: "Be generous.", 5: "Hold the line.", 6: "Find the middle.",
    7: "Keep going.", 8: "Say thank you.", 9: "Shore up the base.",
    10: "Land it.",
}

# Face the direction opposite the day's Disha Shula. Never phrased as a
# warning, only as where to sit.
OPPOSITE = {"North": "south", "South": "north", "East": "west", "West": "east"}


def headline(field: dict) -> tuple[str, str, str]:
    """Two headline lines and the counterline under them."""
    a, b, counter, _cmd, _why = OFFICER[field["systems"]["officer"]["pinyin"]]
    return a, b, counter


def six(field: dict) -> list[tuple[str, str]]:
    """The six commands, each with the tradition and reason underneath."""
    sysx = field["systems"]
    astro = field["astro"]
    dm = sysx["day_master"]
    gem = sysx["gematria"]
    kab = sysx["kabbalah"]
    shula = sysx["vaastu"]["shula"]

    _a, _b, _c, officer_cmd, officer_why = OFFICER[sysx["officer"]["pinyin"]]

    nak_end = astro["nakshatra"]
    rows = [
        (officer_cmd, f"Chinese almanac. {officer_why[0].upper()}{officer_why[1:]}."),
        (STEM[dm["stem"]],
         f"Chinese day pillar. {dm['stem']} over {dm['branch']}, "
         f"{BRANCH_NOTE[dm['branch']]}."),
        (NAKSHATRA[nak_end],
         f"Vedic sky. Moon in {nak_end}, pada {astro['nakshatra_pada']}."),
        (SEFIRAH[kab["number"]],
         f"Number path. Today reduces to {kab['number']}, {kab['name']}."),
        ("Mark the date.",
         f"Hebrew calendar. {gem['date_str']}"
         + (f", {gem['word'][0]}, {gem['word'][1]}." if gem["word"]
            else f", written {gem['letters']}.")),
        (f"Face {OPPOSITE[shula]}.",
         f"Vaastu. {shula} is Disha Shula today."),
    ]
    return rows


def moon_line(astro: dict) -> tuple[str, str]:
    """Plain English first, technical terms underneath."""
    direction = "growing" if astro["moon_growing"] else "shrinking"
    plain = f"Moon {astro['moon_illumination_percent']} percent lit, {direction}"
    tech = (f"{astro['paksha']} {astro['tithi_name']}, "
            f"{astro['nakshatra']} {astro['nakshatra_pada']}, "
            f"{astro['moon_sign_tropical']}")
    return plain, tech


def one_move(field: dict) -> tuple[str, str]:
    """The single action, and the clock time it hangs on."""
    _a, _b, _c, cmd, _why = OFFICER[field["systems"]["officer"]["pinyin"]]
    if field["abhijit"]:
        when = field["abhijit"]["start"]
    else:
        when = field["longest_clear"]["start"]
    return f"{cmd} Do it after {when}.", when
