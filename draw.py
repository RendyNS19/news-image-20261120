#!/usr/bin/env python3
"""Draw The Daily Ledger front page for Friday, November 20, 2026.

One 1024x1024 PNG newspaper front page, built from stories.json with Pillow.
Deterministic: no randomness, no clock reads, fixed layout and palette.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
MARGIN = 28
PAPER = (247, 242, 231)
INK = (20, 20, 20)
GREY = (90, 86, 78)
RULE = (160, 152, 134)
RED = (163, 22, 33)
NAVY = (27, 42, 74)
GREEN = (18, 120, 70)
LIGHT = (255, 255, 255)
PANEL = (238, 231, 214)

FONTS = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}", size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap into lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
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


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    lines = wrap(draw, text, fnt, max_w)
    lh = leading or int(fnt.size * 1.28)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def main():
    data = json.loads((HERE / "stories.json").read_text())
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    name_f = SERIF_B(60)
    name = "THE DAILY LEDGER"
    nw = d.textlength(name, font=name_f)
    d.text(((W - nw) / 2, 16), name, font=name_f, fill=INK)
    d.line([(MARGIN, 96), (W - MARGIN, 96)], fill=INK, width=3)
    d.line([(MARGIN, 101), (W - MARGIN, 101)], fill=INK, width=1)
    date_f = SANS_B(13)
    date_txt = "FRIDAY, NOVEMBER 20, 2026"
    dw = d.textlength(date_txt, font=date_f)
    d.text(((W - dw) / 2, 108), date_txt, font=date_f, fill=INK)
    d.text((MARGIN, 108), "THE WORLD IN ONE PAGE", font=SANS_B(11), fill=GREY)
    right_txt = "EST. 2026  •  NO. 325"
    d.text((W - MARGIN - d.textlength(right_txt, font=SANS_B(11)), 108),
           right_txt, font=SANS_B(11), fill=GREY)

    # ---- Hero -----------------------------------------------------------
    hero = data["hero"]
    y = 140
    d.text((MARGIN, y), hero["kicker"], font=SANS_B(13), fill=RED)
    y += 22
    y = draw_wrapped(d, MARGIN, y, hero["headline"], SERIF_B(42), 600,
                     leading=46)
    y += 8
    y = draw_wrapped(d, MARGIN, y, hero["deck"], SERIF(15), 600, leading=21)
    d.text((MARGIN, y + 6), "By the Ledger markets desk  •  New York",
           font=SANS(11), fill=GREY)

    # Hero stat chips: three facts that fill the space under the deck
    chips = [("5TH", "straight day of losses"),
             ("WORST WEEK", "in 18 months on Wall Street"),
             ("DOWN FOR 2026", "the Nasdaq, after today")]
    chip_y = y + 34
    chip_w, chip_h, chip_gap = 196, 52, 6
    for i, (big, small) in enumerate(chips):
        cx = MARGIN + i * (chip_w + chip_gap)
        d.rectangle([cx, chip_y, cx + chip_w, chip_y + chip_h],
                    fill=PANEL, outline=RULE, width=1)
        d.text((cx + 10, chip_y + 6), big, font=SANS_B(15), fill=RED)
        d.text((cx + 10, chip_y + 28), small, font=SANS(10), fill=GREY)

    # Hero chart panel (right side)
    cx0, cy0, cx1, cy1 = 648, 140, W - MARGIN, 452
    d.rectangle([cx0, cy0, cx1, cy1], fill=PANEL, outline=RULE, width=1)
    d.text((cx0 + 14, cy0 + 12), hero["chart_title"], font=SANS_B(13),
           fill=NAVY)
    d.text((cx0 + 14, cy0 + 34), "Change on the day, %",
           font=SANS(10), fill=GREY)
    bar_x = cx0 + 14
    bar_max = 180
    row_y = cy0 + 62
    for name_i, pct in hero["chart"]:
        d.text((bar_x, row_y), name_i, font=SANS_B(12), fill=INK)
        d.text((bar_x + 118, row_y), f"{pct:+.2f}%", font=SANS_B(12),
               fill=RED)
        bx = bar_x + 118
        d.rectangle([bx, row_y + 22, bx + bar_max, row_y + 32],
                    fill=(220, 214, 196))
        blen = max(6, int(bar_max * abs(pct) / 5.28))
        d.rectangle([bx, row_y + 22, bx + blen, row_y + 32], fill=RED)
        row_y += 36
    d.text((cx0 + 14, cy1 - 20),
           "Nasdaq erases its 2026 gains; S&P and Dow in correction.",
           font=SANS(10), fill=GREY)

    d.line([(MARGIN, 470), (W - MARGIN, 470)], fill=INK, width=2)

    # ---- Tiles + IN BRIEF ----------------------------------------------
    tiles = data["tiles"]
    tx0, ty = MARGIN, 486
    tile_w, tile_h = 326, 138
    gap_x, gap_y = 20, 12
    positions = [(0, 0), (1, 0), (0, 1), (1, 1)]
    for tile, (col, row) in zip(tiles[:4], positions):
        x = tx0 + col * (tile_w + gap_x)
        yy = ty + row * (tile_h + gap_y)
        d.text((x, yy), tile["kicker"], font=SANS_B(10), fill=RED)
        yy += 16
        yy = draw_wrapped(d, x, yy, tile["headline"], SERIF_B(16),
                          tile_w, leading=19)
        yy += 3
        draw_wrapped(d, x, yy, tile["summary"], SANS(11.5), tile_w,
                     leading=15)
        if col == 0:
            d.line([(x + tile_w + 10, ty + row * (tile_h + gap_y)),
                    (x + tile_w + 10, ty + row * (tile_h + gap_y) + tile_h)],
                   fill=RULE, width=1)
    # Wide fifth tile across the tiles area
    tile5 = tiles[4]
    wx, wy = tx0, ty + 2 * (tile_h + gap_y)
    d.line([(tx0, wy - 8), (tx0 + 2 * tile_w + gap_x, wy - 8)], fill=RULE,
           width=1)
    d.text((wx, wy), tile5["kicker"], font=SANS_B(10), fill=RED)
    wy += 16
    wy = draw_wrapped(d, wx, wy, tile5["headline"], SERIF_B(16),
                      2 * tile_w + gap_x, leading=19)
    draw_wrapped(d, wx, wy + 2, tile5["summary"], SANS(11.5),
                 2 * tile_w + gap_x, leading=15)

    # IN BRIEF column
    bx0, bx1 = 716, W - MARGIN
    by = 486
    d.rectangle([bx0, by, bx1, by + 28], fill=NAVY)
    d.text((bx0 + 10, by + 6), "IN BRIEF", font=SANS_B(14), fill=LIGHT)
    by += 36
    for item in data["briefs"]:
        d.rectangle([bx0 + 2, by + 5, bx0 + 8, by + 11], fill=RED)
        by = draw_wrapped(d, bx0 + 14, by, item, SANS(11.5),
                          bx1 - bx0 - 14, leading=15)
        by += 4
        d.line([(bx0, by), (bx1, by)], fill=RULE, width=1)
        by += 8

    # ---- The day in numbers ---------------------------------------------
    d.line([(MARGIN, 900), (W - MARGIN, 900)], fill=RULE, width=1)
    nums = [("8", "killed in Kyiv strikes"),
            ("51–48", "Senate blocks war-powers vote"),
            ("$97", "Anthropic's debut close"),
            ("37 days", "to Kenya's Ebola all-clear")]
    nx = MARGIN
    for big, small in nums:
        d.text((nx, 908), big, font=SANS_B(14), fill=RED)
        bw = d.textlength(big, font=SANS_B(14))
        d.text((nx + bw + 6, 911), small, font=SANS(11), fill=GREY)
        nx += bw + 6 + d.textlength(small, font=SANS(11)) + 26

    # ---- Markets strip ---------------------------------------------------
    sy0, sy1 = 938, 996
    d.rectangle([MARGIN, sy0, W - MARGIN, sy1], fill=NAVY)
    cell_w = (W - 2 * MARGIN) / len(data["markets"])
    for i, (mname, value, pct) in enumerate(data["markets"]):
        cx = MARGIN + i * cell_w
        d.text((cx + 8, sy0 + 6), mname, font=SANS_B(10), fill=(200, 205, 220))
        d.text((cx + 8, sy0 + 20), value, font=SANS_B(13), fill=LIGHT)
        col = GREEN if pct >= 0 else (255, 120, 110)
        d.text((cx + 8, sy0 + 38), f"{pct:+.2f}%", font=SANS_B(11), fill=col)
        if i:
            d.line([(cx, sy0 + 6), (cx, sy1 - 6)], fill=(70, 82, 110), width=1)

    # ---- Footer ----------------------------------------------------------
    foot = "Sources: AP  •  Yahoo Finance  •  Morningstar  •  ICJ  •  Just Security  —  All figures are Friday 20 November 2026 closes"
    fw = d.textlength(foot, font=SANS(9))
    d.text(((W - fw) / 2, 1006), foot, font=SANS(9), fill=GREY)

    img.save(HERE / "entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
