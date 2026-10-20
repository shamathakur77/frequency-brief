"""Render The Daily Frequency front page as a PNG for WhatsApp.

Usage:  python render.py <page.html> <out.png> [node_modules_dir]

<page.html> is the artifact page exactly as published (no doctype, no body tag).
Fonts come from the @fontsource packages (npm install @fontsource/newsreader
@fontsource/bodoni-moda @fontsource/archivo-narrow), because the sandbox cannot
reach Google Fonts. Needs: pip install playwright (Chromium is pre-installed).
"""
import asyncio
import base64
import re
import sys
from pathlib import Path

FACES = [
    ("Newsreader", "newsreader", [(400, "normal"), (400, "italic"), (500, "normal"), (500, "italic"), (700, "normal")]),
    ("Bodoni Moda", "bodoni-moda", [(800, "normal"), (900, "normal")]),
    ("Archivo Narrow", "archivo-narrow", [(500, "normal"), (600, "normal"), (700, "normal")]),
]


def font_css(nm: Path) -> str:
    out, missing = [], []
    for family, pkg, variants in FACES:
        for weight, style in variants:
            f = nm / "@fontsource" / pkg / "files" / f"{pkg}-latin-{weight}-{style}.woff2"
            if not f.exists():
                missing.append(f.name)
                continue
            b64 = base64.b64encode(f.read_bytes()).decode()
            out.append(
                f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
            )
    if missing:
        sys.exit("render.py: font files missing, refusing to render with fallback fonts: " + ", ".join(missing))
    return "\n".join(out)


async def main(page_path: str, out_path: str, nm_dir: str) -> None:
    from playwright.async_api import async_playwright

    html = Path(page_path).read_text(encoding="utf-8")
    html = re.sub(r"<link[^>]+fonts\.googleapis\.com[^>]*>", "", html)
    doc = (
        "<!doctype html><html data-shot data-theme='light'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<style>body{margin:0}[hidden]{display:none!important}" + font_css(Path(nm_dir)) + "</style></head><body>"
        + html + "</body></html>"
    )
    tmp = Path(out_path).with_suffix(".shot.html")
    tmp.write_text(doc, encoding="utf-8")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1400}, device_scale_factor=2, color_scheme="light")
        page = await ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto("file://" + str(tmp.resolve()))
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(300)
        await page.screenshot(path=out_path, full_page=True)
        await browser.close()
    if errors:
        sys.exit("render.py: page script errors: " + "; ".join(errors))
    print("rendered", out_path)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "node_modules"))
