"""Inline Atkinson Hyperlegible as base64 data URIs.

The render environment has no access to Google Fonts, and a headless
screenshot cannot wait on a webfont that never arrives. Embedding the
font makes the render deterministic.
"""
import base64
import pathlib

SRC = "node_modules/@fontsource/atkinson-hyperlegible/files/atkinson-hyperlegible-latin-{w}-normal.woff2"
FACE = ("@font-face{{font-family:'Atkinson Hyperlegible';font-style:normal;"
        "font-weight:{w};font-display:block;"
        "src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


def main(out="fonts-quiet.css"):
    css = "".join(
        FACE.format(w=w, b64=base64.b64encode(pathlib.Path(SRC.format(w=w)).read_bytes()).decode())
        for w in ("400", "700"))
    pathlib.Path(out).write_text(css)
    print(f"wrote {out} ({len(css)} bytes)")


if __name__ == "__main__":
    main()
