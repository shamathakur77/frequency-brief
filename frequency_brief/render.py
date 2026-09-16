# -*- coding: utf-8 -*-
"""Render one day's card to out/card.html. 1080x1350, QUIET design tokens."""
from __future__ import annotations

import math
import os
import pathlib

from . import copy as words

PAPER, SURFACE, INK, MUTED, RULE = "#FBFAF8", "#F4F2EE", "#1C2B29", "#66756F", "#DCDAD3"
ALERT, ALERT_TINT, CALM, COOL = "#8C3B2E", "#F7EEEB", "#3C6B60", "#46587E"

# go = calm, coast = muted, rest = cool. Colour is never the only signal:
# each band is named in the key, and coast is dashed so the three are still
# distinguishable in greyscale or at a glance.
TOKEN_COLOUR = {"green": CALM, "yellow": MUTED, "red": COOL}
TOKEN_DASH = {"yellow": ' stroke-dasharray="3 7" stroke-linecap="round"'}

CX, CY, R = 476, 286, 200
VIEW_W, VIEW_H = 952, 344


def _mins(hm: str) -> int:
    h, m = hm.split(":")
    return int(h) * 60 + int(m)


def _pt(minute: int, rad: float, sr: int, span: int) -> tuple[float, float]:
    t = (minute - sr) / span * math.pi
    return CX - rad * math.cos(t), CY - rad * math.sin(t)


def _arc(a: int, b: int, rad: float, sr: int, span: int) -> str:
    x1, y1 = _pt(a, rad, sr, span)
    x2, y2 = _pt(b, rad, sr, span)
    return f"M {x1:.2f} {y1:.2f} A {rad} {rad} 0 0 1 {x2:.2f} {y2:.2f}"


def _moon(illum_pct: float, growing: bool, cx: int, cy: int, r: int) -> str:
    """Dark disc with the lit fraction drawn on the correct side."""
    k = max(0.0, min(1.0, illum_pct / 100.0))
    rx = r * abs(1 - 2 * k)
    outer = 1 if growing else 0          # lit limb: right when waxing
    inner = (0 if k < 0.5 else 1) if growing else (1 if k < 0.5 else 0)
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK}" fill-opacity=".80"/>'
        f'<path d="M {cx} {cy - r} A {r} {r} 0 0 {outer} {cx} {cy + r} '
        f'A {rx:.2f} {r} 0 0 {inner} {cx} {cy - r} Z" fill="{SURFACE}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{MUTED}" '
        f'stroke-width="1.5"/>')


def build(field: dict, headlines: list[dict] | None = None,
          kp: dict | None = None, out_dir: str = "out") -> pathlib.Path:
    sr, ss = _mins(field["sunrise"]), _mins(field["sunset"])
    span = ss - sr

    # --- dial -------------------------------------------------------------
    bands, ticks, labels, seen = [], [], [], []
    for i, block in enumerate(field["timeline"]):
        a, b = _mins(block["start"]), _mins(block["end"])
        bands.append(f'<path d="{_arc(a + (1.8 if i else 0), b, R, sr, span)}" '
                     f'stroke="{TOKEN_COLOUR[block["token"]]}" stroke-width="18" '
                     f'fill="none"{TOKEN_DASH.get(block["token"], "")}/>')
        seen.append((a, block["start"]))
    seen.append((ss, field["sunset"]))

    for i, (m, text) in enumerate(seen):
        x1, y1 = _pt(m, R + 12, sr, span)
        x2, y2 = _pt(m, R + 24, sr, span)
        ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                     f'y2="{y2:.1f}" stroke="{MUTED}" stroke-width="1.5"/>')
        lx, ly = _pt(m, R + 46, sr, span)
        t = (m - sr) / span
        anc = "end" if t < .28 else ("start" if t > .72 else "middle")
        labels.append(f'<text x="{lx:.1f}" y="{ly + 8:.1f}" text-anchor="{anc}" '
                      f'class="tk">{text}</text>')
        note = "sunrise" if i == 0 else ("sunset" if m == ss else "")
        if note:
            labels.append(f'<text x="{lx:.1f}" y="{ly + 30:.1f}" '
                          f'text-anchor="{anc}" class="tks">{note}</text>')

    boundaries = {m for m, _ in seen}
    minor = "".join(
        f'<line x1="{_pt(mm, R-10, sr, span)[0]:.1f}" y1="{_pt(mm, R-10, sr, span)[1]:.1f}" '
        f'x2="{_pt(mm, R-19, sr, span)[0]:.1f}" y2="{_pt(mm, R-19, sr, span)[1]:.1f}" '
        f'stroke="{RULE}" stroke-width="1.2"/>'
        for mm in range(sr + 30, ss, 30) if mm not in boundaries)

    # --- words ------------------------------------------------------------
    h1, h2, counter = words.headline(field)
    plain, tech = words.moon_line(field["astro"])
    cells = "".join(f'<li><b>{a}</b><span class="why">{b}</span></li>'
                    for a, b in words.six(field))
    move, _when = words.one_move(field)

    # --- fetched sources, omitted entirely when absent ---------------------
    out_rows = []
    if kp:
        out_rows.append(f'<span><b>{kp["text"]}</b> {kp["source"]}</span>')
    for h in (headlines or []):
        out_rows.append(f'<span><b>{h["text"]}</b> {h["source"]}</span>')
    out_block = (f'<div class="out">{"".join(out_rows)}</div>'
                 if out_rows else "")

    date_label = field["_date_label"]
    fonts = pathlib.Path("fonts-quiet.css").read_text()

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>The Frequency Brief</title><style>{fonts}
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE};
--alert:{ALERT};--alert-tint:{ALERT_TINT};
--font:'Atkinson Hyperlegible','Verdana',sans-serif;
--t-xs:15px;--t-sm:16px;--t-base:18px;--t-md:21px;--t-xl:34px;
--lh-body:1.65;--lh-tight:1.35;--radius:3px;
--s-1:4px;--s-2:8px;--s-3:12px;--s-4:16px;--s-5:24px;--s-6:32px;--s-7:48px}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
#wrap{{width:1080px;height:1350px;overflow:hidden;background:var(--paper);
 color:var(--ink);font-family:var(--font);font-size:var(--t-base);
 line-height:var(--lh-body);letter-spacing:.005em;
 display:flex;flex-direction:column;padding:48px 48px 40px}}
.head{{flex:none;display:flex;justify-content:space-between;gap:var(--s-4);
 font-size:var(--t-sm);color:var(--muted)}}
.head .r{{flex:1 1 auto;min-width:0;text-align:right}}
hr{{flex:none;height:1px;border:0;background:var(--rule);margin:var(--s-4) 0 var(--s-5)}}
h1{{flex:none;font-size:76px;line-height:var(--lh-tight);letter-spacing:-.02em;
 font-weight:700}}
.counter{{flex:none;font-size:var(--t-xl);line-height:var(--lh-tight);
 color:var(--muted);margin-top:var(--s-3)}}
.dial{{flex:none;margin-top:var(--s-4)}}
.dial svg{{display:block;width:984px;height:340px}}
.tk{{font-size:22px;font-weight:700;fill:var(--ink);font-variant-numeric:tabular-nums}}
.tks{{font-size:var(--t-xs);fill:var(--muted)}}
.mlab{{font-size:var(--t-md);font-weight:700;fill:var(--ink)}}
.msub{{font-size:var(--t-xs);fill:var(--muted)}}
.key{{flex:none;display:flex;justify-content:center;gap:var(--s-6);
 font-size:var(--t-sm);color:var(--muted);margin-top:var(--s-2)}}
.key i{{display:inline-block;width:16px;height:4px;margin-right:var(--s-2);
 vertical-align:4px}}
.key i.dash{{background:none !important;border-top:4px dotted {MUTED};height:0}}
ul{{flex:1;list-style:none;display:grid;grid-template-columns:1fr 1fr;
 column-gap:var(--s-7);align-content:center;margin-top:var(--s-5)}}
li{{padding:var(--s-4) 0;border-top:1px solid var(--rule)}}
li:nth-child(5),li:nth-child(6){{border-bottom:1px solid var(--rule)}}
li b{{display:block;font-size:var(--t-md);line-height:var(--lh-tight);font-weight:700}}
li .why{{display:block;color:var(--muted);font-size:var(--t-sm);
 margin-top:var(--s-1);line-height:1.45}}
.out{{flex:none;margin-top:var(--s-4);font-size:var(--t-xs);color:var(--muted);
 display:flex;justify-content:space-between;gap:var(--s-5)}}
.out span{{flex:1 1 auto;min-width:0}}
.out b{{color:var(--ink);font-weight:700}}
.alert{{flex:none;background:var(--alert-tint);border-left:5px solid var(--alert);
 border-radius:var(--radius);padding:var(--s-5);margin-top:var(--s-5)}}
.alert h2{{font-size:var(--t-md);line-height:var(--lh-tight);color:var(--alert);
 font-weight:700}}
.alert p{{font-size:var(--t-xl);line-height:var(--lh-tight);margin-top:var(--s-2)}}
.sig{{flex:none;display:flex;justify-content:space-between;font-size:var(--t-xs);
 color:var(--muted);margin-top:var(--s-4)}}
</style></head><body><div id="wrap">

<div class="head"><span>The Frequency Brief</span>
<span class="r">{date_label}</span></div>
<hr>

<h1>{h1}<br>{h2}</h1>
<p class="counter">{counter}</p>

<div class="dial"><svg viewBox="0 0 {VIEW_W} {VIEW_H}">
 {minor}
 {"".join(bands)}
 {"".join(ticks)}
 {"".join(labels)}
 {_moon(field["astro"]["moon_illumination_percent"],
        field["astro"]["moon_growing"], CX, CY - 126, 56)}
 <text x="{CX}" y="{CY-36}" text-anchor="middle" class="mlab">{plain}</text>
 <text x="{CX}" y="{CY-12}" text-anchor="middle" class="msub">{tech}</text>
</svg></div>

<div class="key">
 <span><i style="background:{CALM}"></i>go</span>
 <span><i class="dash"></i>coast, start nothing new</span>
 <span><i style="background:{COOL}"></i>rest, Rahu Kalam</span>
</div>

<ul>{cells}</ul>
{out_block}
<div class="alert"><h2>Your one move</h2><p>{move}</p></div>
<div class="sig"><span>@shama_thakur77</span><span>Save this</span></div>

</div></body></html>"""

    os.makedirs(out_dir, exist_ok=True)
    path = pathlib.Path(out_dir) / "card.html"
    path.write_text(html)
    return path
