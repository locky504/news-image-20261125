#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news front page as entry.png (1024x1024).

A fresh, self-contained PIL drawing: no input image, no network. Run it and it
writes entry.png next to this file. Six real stories, all first reported on
Wednesday 25 November 2026, verified against named outlets the same day.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (247, 241, 224)      # warm newsprint
INK = (24, 24, 22)           # near-black
RED = (164, 31, 31)          # kicker red
GREY = (84, 78, 66)          # deck grey
RULE = (24, 24, 22)
FAINT = (190, 182, 164)      # hairline

LIB = "/usr/share/fonts/truetype/liberation"
DEJ = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    """Try Liberation first, fall back to DejaVu, then PIL's built-in."""
    for base in (LIB, DEJ):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


SERIF_B = "LiberationSerif-Bold.ttf"
SERIF = "LiberationSerif-Regular.ttf"
SERIF_I = "LiberationSerif-Italic.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS = "LiberationSans-Regular.ttf"


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_font(draw, text, name, start, max_w):
    """Largest size at or below start that fits max_w."""
    size = start
    while size > 10:
        fnt = font(name, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 2
    return font(name, 10)


def letterspace(draw, text, fnt, cx, y, fill, gap=4):
    """Draw text centred on cx with extra tracking between letters."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + gap * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + gap
    return y + fnt.size


def globe(draw, cx, cy, r):
    """A simple wire globe: circle, meridians, parallels."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    for k in (0.45, 0.8):
        rx = int(r * k)
        draw.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=INK, width=2)
    for k in (-0.5, 0.0, 0.5):
        y = cy + int(r * k)
        half = int((r * r - (r * k) ** 2) ** 0.5)
        draw.line([cx - half, y, cx + half, y], fill=INK, width=2)
    # a small red marker dot for the day's dateline
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 42                      # side margin
    inner = W - 2 * mx           # 940

    # --- frame ------------------------------------------------------------
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=3)
    d.rectangle([16, 16, W - 17, H - 17], outline=FAINT, width=1)

    # --- top strip --------------------------------------------------------
    small = font(SANS_B, 17)
    d.text((mx, 30), "ONE DAY  •  ONE PAGE", font=small, fill=GREY)
    right = "No. 25  •  2026"
    d.text((W - mx - d.textlength(right, font=small), 30), right,
           font=small, fill=GREY)
    d.line([mx, 56, W - mx, 56], fill=RULE, width=1)

    # --- masthead ---------------------------------------------------------
    mast = fit_font(d, "THE WORLD TODAY", SERIF_B, 96, inner)
    tw = d.textlength("THE WORLD TODAY", font=mast)
    d.text(((W - tw) / 2, 66), "THE WORLD TODAY", font=mast, fill=INK)
    date_f = font(SANS_B, 27)
    letterspace(d, "WEDNESDAY, 25 NOVEMBER 2026", date_f, W / 2, 178, RED, gap=5)

    # double rule under the date
    d.line([mx, 222, W - mx, 222], fill=RULE, width=4)
    d.line([mx, 230, W - mx, 230], fill=RULE, width=1)

    # --- lead story: China -----------------------------------------------
    y = 252
    kick = font(SANS_B, 20)
    d.text((mx, y), "CHINA", font=kick, fill=RED)
    d.text((mx + 92, y), "—  THE DAY'S TOP STORY", font=font(SANS, 20), fill=GREY)
    y += 30
    lead_head = font(SERIF_B, 47)
    lines = wrap(d, "Beijing Probes a Politburo Member", lead_head, 620)
    y = draw_lines(d, lines, mx, y, lead_head, INK, 54)
    y += 6
    deck = font(SERIF, 23)
    lines = wrap(d,
                 "Shanghai party chief Chen Jining is under investigation, "
                 "the anti-graft body says — the most senior probe in years.",
                 deck, 620)
    y = draw_lines(d, lines, mx, y, deck, GREY, 30)
    globe(d, 852, 330, 78)
    d.text((852 - 34, 418), "BEIJING", font=font(SANS_B, 15), fill=GREY)

    d.line([mx, 464, W - mx, 464], fill=RULE, width=2)

    # --- four stories in a 2 x 2 grid ------------------------------------
    grid = [
        ("UNITED STATES", "Jury Convicts Huawei of Stealing Trade Secrets",
         "A U.S. jury finds the Chinese tech giant guilty of trade-secret "
         "theft after a federal trial."),
        ("BUSINESS", "Huang in Therapy as Nvidia Rally Fades",
         "The Nvidia chief tells staff he made \u201csome terrible mistakes\u201d "
         "a day after returning as CEO."),
        ("UNITED STATES", "Trump Gives Giuliani the Medal of Freedom",
         "The president awards the highest U.S. civilian honour to his "
         "former lawyer."),
        ("SPACE", "Shenzhou-24 Lifts Off with Pakistan Astronaut",
         "China launches its newest crewed mission, carrying the first "
         "Pakistani ever to fly in space."),
    ]
    col_w = (inner - 36) // 2
    row_y = [484, 710]
    for i, (kicker, head, body) in enumerate(grid):
        x = mx + (i % 2) * (col_w + 36)
        yy = row_y[i // 2]
        d.text((x, yy), kicker, font=kick, fill=RED)
        yy += 28
        hf = font(SERIF_B, 30)
        lines = wrap(d, head, hf, col_w)
        yy = draw_lines(d, lines, x, yy, hf, INK, 36)
        yy += 4
        bf = font(SERIF, 21)
        lines = wrap(d, body, bf, col_w)
        draw_lines(d, lines, x, yy, bf, GREY, 27)
        if i % 2 == 0:
            d.line([x + col_w + 18, row_y[i // 2], x + col_w + 18,
                    row_y[i // 2] + 196], fill=FAINT, width=1)
    d.line([mx, 696, W - mx, 696], fill=FAINT, width=1)

    # --- bottom band: Ukraine --------------------------------------------
    y = 920
    d.line([mx, 908, W - mx, 908], fill=RULE, width=2)
    d.text((mx, y), "UKRAINE", font=kick, fill=RED)
    band_head = font(SERIF_B, 28)
    d.text((mx + 118, y + 1), "Kyiv Region Strikes Kill at Least 14",
           font=band_head, fill=INK)
    y += 38
    bf = font(SERIF, 19)
    d.text((mx, y), "Russian strikes hit the Kyiv region overnight, Ukrainian "
           "officials say.", font=bf, fill=GREY)

    # --- footer -----------------------------------------------------------
    foot = font(SANS, 14)
    d.text((mx, 988), "Reported 25 November 2026  •  The Manila Times  •  "
           "South China Morning Post  •  Arab News",
           font=foot, fill=GREY)

    img.save(OUT, "PNG")
    print(f"wrote {OUT} {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
