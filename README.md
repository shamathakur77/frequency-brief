# The Frequency Brief

**A daily card that tells you when to do the hard thing.**

One card a day. Every number on it is worked out, not guessed.

![The card](docs/card.png)

---

## The problem

I wanted one answer each morning: when is the good stretch to do focused work,
and when should I leave things alone.

Getting that answer meant opening four different apps. A sunrise app. A moon
phase site. A panchang page. A calendar. Two of them disagreed with each other.
One was clearly making numbers up, because it gave me a different answer on a
refresh.

Asking an AI made it worse. It produced times that looked right and were wrong,
and there was no way to tell which.

## Why I built it

I do this for a living. My day job is data quality and compliance monitoring,
where a number that looks plausible but is unverified is the worst kind of
number, because people act on it.

So I built the morning answer the way I would build anything at work: compute
it, prove it, and make it fail loudly when it cannot.

## What it solves

- **One place instead of four.** All six systems on a single card.
- **No invented numbers.** Every figure is either calculated on my own machine
  or printed next to the source it came from.
- **It admits when it doesn't know.** A missing window is printed as missing. A
  dead data feed prints `no data today`.
- **Readable at 7am.** Built to a low-stimulation design system so it can be
  understood in a glance, not studied.

![How it works](docs/explainer.png)

## What you get

Two outputs from one scheduled run:

1. A private HTML email with the full day, sent before you wake up.
2. A public PNG card, plus alt text and caption, ready to post.

Times are computed for Stockholm. Any city works, you change one setting.

## How to use it

```bash
git clone <this repo>
cd frequency-brief

pip install -r requirements.txt
npm install

# inline the webfont as base64 so rendering never waits on a network call
python3 tools/build_fonts.py

python3 frequency_brief/build_card_quiet.py
node frequency_brief/screenshot_card.js
```

The card lands at `out/card.png` at exactly 1080 x 1350. Run it on a schedule
(cron, GitHub Actions, any task runner) and it produces a fresh card each day.

---

## How it works

![Pipeline](docs/pipeline.png)

**Six systems, all computed locally**

| System | Library | What it gives |
| --- | --- | --- |
| Astronomy | `pyswisseph` (Swiss Ephemeris) | Sunrise, sunset, tithi, nakshatra, lunar illumination, Human Design sun gate |
| Vedic day windows | plain arithmetic | Rahu Kalam, Yamaganda, Gulika, Abhijit, each a fixed fraction of that date's own daylight |
| Chinese calendar | `sxtwl` | Day stem and branch, month branch, Tong Shu day officer |
| Hebrew calendar | `pyluach` | Civil date rendered in letters, reordered so the divine name is never spelled |
| Number path | plain arithmetic | Date digits reduced to one figure |
| Vaastu | lookup by weekday | Disha Shula, expressed as a direction to face |

Because the Vedic windows are fractions of daylight, their length changes with
the season. Rahu Kalam runs about 46 minutes in December and about 140 in June
at 59°N. That is the geometry, not a bug.

**Two fetched sources, both attributed on the card**

- NOAA Space Weather Prediction Center, 3 day planetary Kp forecast.
- Three headlines: one world, one AI, one markets. The outlet is printed beside
  each headline.

**Four guards that gate the render**

| Guard | Behaviour |
| --- | --- |
| Anchor assertion | `2000-01-01` must resolve to a Wu Horse day pillar, or the run raises and nothing renders |
| Null handling | The Abhijit window does not exist on Wednesdays. The card falls back to the longest clear stretch and relabels it |
| Source failure | A dead feed prints `no data today` rather than a plausible substitute |
| No repetition | Rendered text is diffed before send, so no time or figure appears twice |

**Render**

Playwright drives headless Chromium and screenshots the page at exactly
1080 x 1350. Layout is asserted, not eyeballed: `scrollHeight` must equal
`clientHeight`, so any overflow fails the build instead of clipping silently.

## Design

Built on a low-stimulation design system for AuDHD readers, which turns out to
read better for anyone at 7am:

- One typeface. Atkinson Hyperlegible, drawn by the Braille Institute so no two
  letterforms can be confused.
- Text contrast at 13:1, well past WCAG AAA.
- No colour-only encoding. Every band on the day dial carries a written label.
- No gradients, no shadows. Hairlines and vertical rhythm carry the structure.
- One accent colour, used once, on the single action for the day.

## Tech stack

`Python 3` · `pyswisseph` · `sxtwl` · `pyluach` · `Playwright` ·
`headless Chromium` · `Gmail API` · `HTML` · `CSS` · `SVG`

## Skills this exercises

Deterministic data pipelines · third-party API integration · data validation and
assertion design · graceful degradation and null handling · scheduled and
unattended jobs · SVG data visualisation · accessible design systems and WCAG
contrast · HTML email that survives real clients · technical writing

## Repo layout

```
frequency_brief/
  frameworks.py            five calendar systems, all deterministic
  build_card_quiet.py      the card
  build_arch.py            the pipeline diagram
  build_explain.py         the explainer card
  screenshot_card.js       Playwright render, 1080x1350
  screenshot_pipeline.js   Playwright render, 1200x1500
tools/
  build_fonts.py           inline the webfont as base64
docs/                      rendered images used in this README
```

## Not included

The Vedic timing module (`cosmic_timing.py`) came from elsewhere and is not
redistributed here. `frameworks.py` runs standalone.

## A note on what this is

The card reads six traditions that were built independently of each other, in
different centuries, on different continents. When several of them land on the
same instruction for a given date, that is a coincidence worth noticing. It is
not evidence of anything, and the card never claims it is.

Astrology is the dataset here. It is not the claim.

## Licence

MIT.
