# -*- coding: utf-8 -*-
"""Frequency Brief, one card, QUIET design system. 1080x1350."""
import math

import os
os.makedirs("out", exist_ok=True)
F = open("fonts-quiet.css").read()

PAPER, SURFACE, INK, MUTED, RULE = "#FBFAF8", "#F4F2EE", "#1C2B29", "#66756F", "#DCDAD3"
ALERT, ALERT_TINT = "#8C3B2E", "#F7EEEB"
CALM, CALM_TINT = "#3C6B60", "#EDF2EF"
COOL, COOL_TINT = "#46587E", "#EDEFF5"

CX, CY, R = 476, 286, 200
SR, SS = 378, 1146
SPAN = SS - SR

# go = calm, coast = muted, rest = cool. Every colour is paired with a word.
SEG = [(378, 474, CALM), (474, 570, MUTED), (570, 666, CALM),
       (666, 762, MUTED), (762, 858, COOL), (858, 1146, CALM)]


def pt(m, rad):
    t = (m - SR) / SPAN * math.pi
    return CX - rad * math.cos(t), CY - rad * math.sin(t)


def arc(a, b, rad):
    x1, y1 = pt(a, rad)
    x2, y2 = pt(b, rad)
    return f"M {x1:.2f} {y1:.2f} A {rad} {rad} 0 0 1 {x2:.2f} {y2:.2f}"


bands = "".join(
    f'<path d="{arc(a + (1.8 if i else 0), b, R)}" stroke="{c}" stroke-width="18" '
    f'fill="none"/>' for i, (a, b, c) in enumerate(SEG))

marks = [(378, "06:18", "sunrise"), (474, "07:54", ""), (570, "09:30", ""),
         (666, "11:06", ""), (762, "12:42", ""), (858, "14:18", ""),
         (1146, "19:06", "sunset")]
ticks, labels = [], []
for m, lab, note in marks:
    x1, y1 = pt(m, R + 12)
    x2, y2 = pt(m, R + 24)
    ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{MUTED}" stroke-width="1.5"/>')
    lx, ly = pt(m, R + 46)
    t = (m - SR) / SPAN
    anc = "end" if t < .28 else ("start" if t > .72 else "middle")
    labels.append(f'<text x="{lx:.1f}" y="{ly + 8:.1f}" text-anchor="{anc}" class="tk">{lab}</text>')
    if note:
        labels.append(f'<text x="{lx:.1f}" y="{ly + 30:.1f}" text-anchor="{anc}" class="tks">{note}</text>')

minor = "".join(
    f'<line x1="{pt(mm, R-10)[0]:.1f}" y1="{pt(mm, R-10)[1]:.1f}" '
    f'x2="{pt(mm, R-19)[0]:.1f}" y2="{pt(mm, R-19)[1]:.1f}" stroke="{RULE}" stroke-width="1.2"/>'
    for mm in range(390, 1146, 30) if mm not in (474, 570, 666, 762, 858))

MR, k = 56, 0.255
rx = MR * abs(1 - 2 * k)
MY = CY - 126
moon = (f'<circle cx="{CX}" cy="{MY}" r="{MR}" fill="{INK}" fill-opacity=".80"/>'
        f'<path d="M {CX} {MY - MR} A {MR} {MR} 0 0 1 {CX} {MY + MR} '
        f'A {rx:.2f} {MR} 0 0 0 {CX} {MY - MR} Z" fill="{SURFACE}"/>'
        f'<circle cx="{CX}" cy="{MY}" r="{MR}" fill="none" stroke="{MUTED}" stroke-width="1.5"/>')

SIX = [("Finish it.", "Chinese almanac. A Cheng Success day, for completing."),
       ("Work quiet.", "Chinese day pillar. Yin Water over Snake."),
       ("Aim at one goal.", "Vedic sky. Moon in Vishakha until 13:52."),
       ("Say thank you.", "Number path. Today reduces to 8, Hod."),
       ("Mark the date.", "Hebrew calendar. 5 Tishrei 5787, letter Hey."),
       ("Face south.", "Vaastu. North is Disha Shula today.")]
cells = "".join(f'<li><b>{a}</b><span class="why">{b}</span></li>' for a, b in SIX)

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>The Frequency Brief</title>
<style>{F}
:root{{--paper:{PAPER};--surface:{SURFACE};--ink:{INK};--muted:{MUTED};--rule:{RULE};
--alert:{ALERT};--alert-tint:{ALERT_TINT};--calm:{CALM};--cool:{COOL};
--font:'Atkinson Hyperlegible','Verdana',sans-serif;
--t-xs:15px;--t-sm:16px;--t-base:18px;--t-md:21px;--t-lg:26px;--t-xl:34px;
--lh-body:1.65;--lh-tight:1.35;--radius:3px;
--s-1:4px;--s-2:8px;--s-3:12px;--s-4:16px;--s-5:24px;--s-6:32px;--s-7:48px}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
#wrap{{width:1080px;height:1350px;overflow:hidden;background:var(--paper);color:var(--ink);
 font-family:var(--font);font-size:var(--t-base);line-height:var(--lh-body);letter-spacing:.005em;
 display:flex;flex-direction:column;padding:48px 48px 40px}}
.head{{flex:none;display:flex;justify-content:space-between;gap:var(--s-4);
 font-size:var(--t-sm);color:var(--muted)}}
.head .r{{flex:1 1 auto;min-width:0;text-align:right}}
hr{{flex:none;height:1px;border:0;background:var(--rule);margin:var(--s-4) 0 var(--s-5)}}
h1{{flex:none;font-size:76px;line-height:var(--lh-tight);letter-spacing:-.02em;font-weight:700}}
.counter{{flex:none;font-size:var(--t-xl);line-height:var(--lh-tight);color:var(--muted);
 margin-top:var(--s-3)}}
.dial{{flex:none;margin-top:var(--s-4)}}
.dial svg{{display:block;width:984px;height:340px}}
.tk{{font-size:22px;font-weight:700;fill:var(--ink);font-variant-numeric:tabular-nums}}
.tks{{font-size:var(--t-xs);fill:var(--muted)}}
.mlab{{font-size:var(--t-md);font-weight:700;fill:var(--ink)}}
.msub{{font-size:var(--t-xs);fill:var(--muted)}}
.key{{flex:none;display:flex;justify-content:center;gap:var(--s-6);font-size:var(--t-sm);
 color:var(--muted);margin-top:var(--s-2)}}
.key i{{display:inline-block;width:14px;height:4px;margin-right:var(--s-2);vertical-align:4px}}
ul{{flex:1;list-style:none;display:grid;grid-template-columns:1fr 1fr;
 column-gap:var(--s-7);align-content:center;margin-top:var(--s-5)}}
li{{padding:var(--s-4) 0;border-top:1px solid var(--rule)}}
li:nth-child(5),li:nth-child(6){{border-bottom:1px solid var(--rule)}}
li b{{display:block;font-size:var(--t-md);line-height:var(--lh-tight);font-weight:700}}
li .why{{display:block;color:var(--muted);font-size:var(--t-sm);margin-top:var(--s-1);line-height:1.45}}
.out{{flex:none;margin-top:var(--s-4);font-size:var(--t-xs);color:var(--muted);
 display:flex;justify-content:space-between;gap:var(--s-5)}}
.out span{{flex:1 1 auto;min-width:0}}
.out b{{color:var(--ink);font-weight:700}}
.alert{{flex:none;background:var(--alert-tint);border-left:5px solid var(--alert);
 border-radius:var(--radius);padding:var(--s-5);margin-top:var(--s-5)}}
.alert h2{{font-size:var(--t-md);line-height:var(--lh-tight);color:var(--alert);font-weight:700}}
.alert p{{font-size:var(--t-xl);line-height:var(--lh-tight);margin-top:var(--s-2)}}
.sig{{flex:none;display:flex;justify-content:space-between;font-size:var(--t-xs);
 color:var(--muted);margin-top:var(--s-4)}}
</style></head><body><div id="wrap">

<div class="head"><span>The Frequency Brief</span>
<span class="r">Wednesday, 16 September 2026, Stockholm</span></div>
<hr>

<h1>Today is a<br>shipping day.</h1>
<p class="counter">Finish something. Then send it.</p>

<div class="dial"><svg viewBox="0 0 984 340">
 {minor}
 {bands}
 {"".join(ticks)}
 {"".join(labels)}
 {moon}
 <text x="{CX}" y="{CY-36}" text-anchor="middle" class="mlab">Moon 25.5 percent lit, growing</text>
 <text x="{CX}" y="{CY-12}" text-anchor="middle" class="msub">Shukla Shashthi, Vishakha 3, Scorpio</text>
</svg></div>

<div class="key">
 <span><i style="background:{CALM}"></i>go</span>
 <span><i style="background:{MUTED}"></i>coast, start nothing new</span>
 <span><i style="background:{COOL}"></i>rest, Rahu Kalam</span>
</div>

<ul>{cells}</ul>

<div class="out">
 <span><b>Kp 4.67 tonight.</b> NOAA</span>
 <span><b>Gemini 3.8 Live ships.</b> AI Weekly</span>
 <span><b>Fed hike odds 90 percent.</b> Yahoo Finance</span>
</div>

<div class="alert"><h2>Your one move</h2>
<p>Finish the one thing. Send it after 14:18.</p></div>

<div class="sig"><span>@shama_thakur77</span><span>Save this</span></div>

</div></body></html>"""

open("out/card.html", "w").write(HTML)
print("ok")
