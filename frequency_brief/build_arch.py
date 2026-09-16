# -*- coding: utf-8 -*-
"""Pipeline diagram for LinkedIn. 1200x1500. QUIET design system."""
import os
os.makedirs("out", exist_ok=True)
F = open("fonts-quiet.css").read()

PAPER, SURFACE, INK, MUTED, RULE = "#FBFAF8", "#F4F2EE", "#1C2B29", "#66756F", "#DCDAD3"
ALERT, ALERT_TINT, CALM, COOL = "#8C3B2E", "#F7EEEB", "#3C6B60", "#46587E"

STAGES = [
    ("Compute", CALM, "Deterministic. Local. No network.", [
        ("pyswisseph", "Swiss Ephemeris. Sunrise, sunset, tithi, nakshatra, moon illumination, Human Design gate."),
        ("pure math", "Rahu Kalam, Yamaganda, Gulika, Abhijit as fractions of the day's own daylight."),
        ("sxtwl", "Chinese sexagenary calendar. Day stem and branch, month branch, Tong Shu day officer."),
        ("pyluach", "Hebrew civil date, rendered in letters, reordered so the divine name is never spelled."),
    ]),
    ("Fetch", COOL, "Two sources. Both attributed on the card.", [
        ("NOAA SWPC", "Planetary Kp forecast, read from the published 3 day text product."),
        ("news", "One world, one AI, one money headline. The outlet is printed next to each."),
    ]),
    ("Guard", ALERT, "The constraint the whole thing is built around.", [
        ("anchor assert", "2000-01-01 must resolve to Wu Horse. If it does not, the run stops. Nothing renders."),
        ("null handling", "Abhijit is absent on Wednesdays. The card falls back to the longest clear window."),
        ("source failure", "A dead feed prints “no data today”. It never prints a plausible number."),
        ("no repetition", "Rendered text is scanned before send. No time or figure appears twice."),
    ]),
    ("Render", CALM, "One canvas. Verified, not eyeballed.", [
        ("design tokens", "Atkinson Hyperlegible, 13:1 text contrast, colour always paired with a written label."),
        ("Playwright", "Headless Chromium draws the page and screenshots it at exactly 1080 by 1350."),
        ("layout assert", "scrollHeight must equal clientHeight. Any overflow fails the build."),
    ]),
    ("Deliver", COOL, "Two outputs from one run.", [
        ("Gmail API", "Private HTML brief, inline CSS, 620px table layout."),
        ("card and caption", "Public PNG plus alt text, search keywords and a posting note."),
    ]),
]

blocks = []
for name, colour, lead, rows in STAGES:
    r = "".join(
        f'<div class="row"><div class="rl">{a}</div><div class="rd">{b}</div></div>'
        for a, b in rows)
    blocks.append(
        f'<section><div class="sh"><span class="node" style="background:{colour}"></span>'
        f'<h2 style="color:{colour}">{name}</h2><p class="lead">{lead}</p></div>{r}</section>')

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Pipeline</title><style>{F}
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE};
--font:'Atkinson Hyperlegible','Verdana',sans-serif;--lh-tight:1.35;
--s-1:4px;--s-2:8px;--s-3:12px;--s-4:16px;--s-5:24px;--s-6:32px;--s-7:48px}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1200px;height:1500px;overflow:hidden}}
#wrap{{width:1200px;height:1500px;overflow:hidden;background:var(--paper);color:var(--ink);
 font-family:var(--font);line-height:1.6;letter-spacing:.005em;
 display:flex;flex-direction:column;padding:56px 64px 48px}}
.head{{flex:none;display:flex;justify-content:space-between;font-size:17px;color:var(--muted)}}
.head .r{{flex:1 1 auto;min-width:0;text-align:right}}
hr{{flex:none;height:1px;border:0;background:var(--rule);margin:var(--s-4) 0 var(--s-5)}}
h1{{flex:none;font-size:62px;line-height:var(--lh-tight);letter-spacing:-.02em;font-weight:700}}
.sub{{flex:none;font-size:26px;line-height:var(--lh-tight);color:var(--muted);margin-top:var(--s-3)}}
main{{flex:1;display:flex;flex-direction:column;justify-content:space-between;
 margin-top:var(--s-6);padding-left:26px;border-left:1px solid var(--rule);position:relative}}
section{{position:relative}}
.sh{{display:flex;align-items:baseline;gap:var(--s-3);padding-bottom:var(--s-2)}}
.node{{position:absolute;left:-33px;top:12px;width:13px;height:13px;border-radius:50%}}
h2{{font-size:27px;line-height:var(--lh-tight);font-weight:700}}
.lead{{font-size:18px;color:var(--muted);flex:1 1 auto;min-width:0}}
.row{{display:flex;gap:var(--s-5);padding:11px 0;border-top:1px solid var(--rule)}}
.rl{{flex:0 0 210px;font-size:19px;font-weight:700;line-height:1.45}}
.rd{{flex:1 1 auto;min-width:0;font-size:18px;color:var(--muted);line-height:1.5}}
.foot{{flex:none;font-size:17px;color:var(--muted);margin-top:var(--s-5);
 display:flex;justify-content:space-between;gap:var(--s-5)}}
.foot b{{color:var(--ink);font-weight:700}}
</style></head><body><div id="wrap">
<div class="head"><span>The Frequency Brief</span><span class="r">Daily pipeline, Stockholm</span></div>
<hr>
<h1>How the card is built.</h1>
<p class="sub">One scheduled run. Nothing scraped, nothing generated, every figure traceable.</p>
<main>{"".join(blocks)}</main>
<div class="foot"><span>Python, Playwright, headless Chromium</span>
<span><b>Astrology is the dataset here, not the claim.</b></span></div>
</div></body></html>"""

open("out/pipeline.html", "w").write(HTML)
print("ok")
