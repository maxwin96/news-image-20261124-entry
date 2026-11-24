#!/usr/bin/env python3
"""WORLD NEWS -- 24 NOVEMBER 2026.

A one-page newspaper poster summarising the day's world news in a
single 1024x1024 PNG image. Written from scratch with the Python
standard library only: the raster canvas, the 5x7 bitmap font, the
geometric panel illustrations and the PNG encoder below are all
hand-written in this file.

Determinism rules for this program:
  * no network access
  * no timestamps anywhere (the PNG carries no time chunk)
  * no randomness, no dict-order dependence, no environment input
Two runs on any machine must therefore produce a byte-identical file.

Usage:
    python3 main.py            # writes /output/entry.png
"""

import math
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024
OUT_PATH = "/output/entry.png"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
INK = (18, 18, 22)
PAPER = (250, 247, 238)
NAVY = (16, 32, 64)
NAVY_DARK = (10, 22, 44)
RED = (178, 34, 34)
GOLD = (212, 175, 55)
GREY = (96, 96, 104)
LIGHT_GREY = (228, 226, 220)
WHITE = (255, 255, 255)
GREEN = (0, 130, 70)
BLUE = (28, 84, 160)
SKY = (127, 178, 217)
SEA = (20, 69, 107)
ORANGE = (232, 116, 28)
YELLOW = (255, 205, 0)
EU_BLUE = (31, 58, 147)

# ---------------------------------------------------------------------------
# 5x7 bitmap font (uppercase, digits and common punctuation).
# Each glyph is 7 rows of 5 characters; "#" is an inked pixel.
# ---------------------------------------------------------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ";": ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale):
    """Pixel width of one line of text at the given scale."""
    return len(text) * 6 * scale - scale


def wrap_text(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if len(trial) <= max_chars:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Raster canvas and drawing primitives
# ---------------------------------------------------------------------------
class Canvas:
    """A plain RGB raster held in one bytearray, row-major."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, background)

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            index = (y * self.width + x) * 3
            self.pixels[index] = color[0]
            self.pixels[index + 1] = color[1]
            self.pixels[index + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                off = base + (xx - x0) * 3
                self.pixels[off] = r
                self.pixels[off + 1] = g
                self.pixels[off + 2] = b

    def draw_rect(self, x, y, w, h, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def draw_line(self, x0, y0, x1, y1, color, thickness=1):
        """Bresenham line with a square brush of the given thickness."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thickness // 2
        while True:
            for oy in range(-half, half + 1):
                for ox in range(-half, half + 1):
                    self.set_pixel(x0 + ox, y0 + oy, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, radius, color):
        for yy in range(cy - radius, cy + radius + 1):
            dy = yy - cy
            half = int((radius * radius - dy * dy) ** 0.5)
            self.fill_rect(cx - half, yy, half * 2 + 1, 1, color)

    def fill_polygon(self, points, color):
        """Scanline fill of a simple polygon (even-odd rule)."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            count = len(points)
            for i in range(count):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % count]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    nodes.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                xa = int(nodes[i])
                xb = int(nodes[i + 1])
                self.fill_rect(xa, y, xb - xa + 1, 1, color)

    def draw_star(self, cx, cy, radius, color):
        """A small four-point sparkle: a plus with diagonal arms."""
        self.fill_rect(cx - radius, cy - 1, radius * 2 + 1, 3, color)
        self.fill_rect(cx - 1, cy - radius, 3, radius * 2 + 1, color)
        self.draw_line(cx - radius, cy - radius, cx + radius, cy + radius,
                       color, 1)
        self.draw_line(cx - radius, cy + radius, cx + radius, cy - radius,
                       color, 1)

    # -- text -------------------------------------------------------------
    def draw_char(self, x, y, char, scale, color):
        glyph = FONT.get(char, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    self.fill_rect(x + col * scale, y + row * scale,
                                   scale, scale, color)

    def draw_text(self, x, y, text, scale, color):
        for i, char in enumerate(text):
            self.draw_char(x + i * 6 * scale, y, char, scale, color)

    def draw_text_centered(self, x, y, width, text, scale, color):
        start = x + (width - text_width(text, scale)) // 2
        self.draw_text(start, y, text, scale, color)

    def draw_block(self, x, y, width, text, scale, color, leading=None):
        """Word-wrapped left-aligned text block; returns lines drawn."""
        if leading is None:
            leading = 8 * scale + scale
        max_chars = max(1, width // (6 * scale))
        lines = wrap_text(text, max_chars)
        for i, line in enumerate(lines):
            self.draw_text(x, y + i * leading, line, scale, color)
        return len(lines)


# ---------------------------------------------------------------------------
# Panel illustrations: simple geometric scenes, one per story.
# Each scene draws inside the box (x, y, w, h).
# ---------------------------------------------------------------------------
def scene_chip(cv, x, y, w, h):
    """Nvidia: a green computer chip and a rising market arrow."""
    cv.fill_rect(x, y, w, h, (14, 59, 46))
    # rising bars
    bars = [26, 40, 34, 52, 66, 84]
    bw = 22
    gap = 14
    bx = x + 24
    base = y + h - 22
    for i, bh in enumerate(bars):
        cv.fill_rect(bx + i * (bw + gap), base - bh, bw, bh, GREEN)
    # the chip, right side
    cx = x + w - 190
    cy = y + 22
    cw = 150
    ch = 84
    for px in range(cx - 12, cx + cw + 12, 24):
        cv.fill_rect(px, cy - 12, 8, 12, GOLD)
        cv.fill_rect(px, cy + ch, 8, 12, GOLD)
    for py in range(cy - 8, cy + ch + 8, 24):
        cv.fill_rect(cx - 12, py, 12, 8, GOLD)
        cv.fill_rect(cx + cw, py, 12, 8, GOLD)
    cv.fill_rect(cx, cy, cw, ch, (10, 10, 14))
    cv.draw_rect(cx, cy, cw, ch, GREEN, 3)
    cv.fill_rect(cx + 34, cy + 26, 82, 32, (10, 10, 14))
    cv.draw_rect(cx + 34, cy + 26, 82, 32, GOLD, 2)
    cv.draw_text(cx + 48, cy + 34, "NVDA", 2, GOLD)
    # rising arrow across the top
    cv.draw_line(x + 20, y + 34, x + 130, y + 26, WHITE, 4)
    cv.draw_line(x + 130, y + 26, x + 250, y + 10, WHITE, 4)
    cv.fill_polygon([(x + 250, y + 10), (x + 222, y + 8),
                     (x + 244, y + 30)], WHITE)


def scene_capitol(cv, x, y, w, h):
    """Democrats: the US Capitol dome and a big 258."""
    cv.fill_rect(x, y, w, h, (29, 58, 110))
    for sx, sy in ((x + 30, y + 18), (x + 430, y + 26), (x + 250, y + 12),
                   (x + 90, y + 46), (x + 380, y + 52)):
        cv.draw_star(sx, sy, 5, WHITE)
    # dome
    dome_cx = x + 150
    dome_cy = y + h - 34
    cv.fill_circle(dome_cx, dome_cy, 62, WHITE)
    cv.fill_rect(dome_cx - 62, dome_cy, 124, 34, WHITE)
    cv.fill_rect(dome_cx - 4, dome_cy - 82, 8, 22, WHITE)
    cv.fill_circle(dome_cx, dome_cy - 84, 6, GOLD)
    # columns
    for i in range(5):
        col_x = dome_cx - 52 + i * 24
        cv.fill_rect(col_x, dome_cy + 6, 12, 28, (29, 58, 110))
    # big seat count
    cv.draw_text(x + w - 205, y + 30, "258", 8, WHITE)
    cv.draw_text(x + w - 205, y + 92, "SEATS", 3, GOLD)


def scene_ship(cv, x, y, w, h):
    """Ukraine: a warship at sea under a drone strike burst."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + 62, w, h - 62, SEA)
    cv.fill_rect(x, y + 62, w, 4, (200, 225, 240))
    # sun
    cv.fill_circle(x + 70, y + 26, 16, YELLOW)
    # ship hull
    hull_y = y + 78
    cv.fill_polygon([(x + 120, hull_y), (x + 330, hull_y),
                     (x + 300, hull_y + 26), (x + 150, hull_y + 26)],
                    (40, 40, 48))
    cv.fill_rect(x + 170, hull_y - 22, 110, 22, (60, 60, 70))
    cv.fill_rect(x + 205, hull_y - 40, 8, 20, (40, 40, 48))
    cv.fill_rect(x + 250, hull_y - 34, 30, 8, RED)
    # explosion burst above the ship
    ex, ey = x + 330, y + 34
    for dx, dy in ((-34, -8), (-24, -26), (0, -34), (24, -24), (34, -6),
                   (30, 18), (6, 30), (-20, 22), (-36, 12)):
        cv.fill_polygon([(ex, ey), (ex + dx, ey + dy),
                         (ex + dx // 2 + 6, ey + dy // 2 - 6)], ORANGE)
    cv.fill_circle(ex, ey, 16, YELLOW)
    cv.fill_circle(ex, ey, 8, WHITE)
    # two sea drones racing in
    for dx in (x + 30, x + 62):
        cv.fill_circle(dx, y + 92, 5, INK)
        cv.draw_line(dx - 10, y + 92, dx + 10, y + 92, INK, 2)


def scene_rocket(cv, x, y, w, h):
    """SpaceX: a rocket beside a courthouse column and a gavel."""
    cv.fill_rect(x, y, w, h, (43, 43, 58))
    # courthouse pediment and columns, left
    cv.fill_polygon([(x + 30, y + 26), (x + 150, y + 26),
                     (x + 90, y + 52)], WHITE)
    for i in range(3):
        cv.fill_rect(x + 44 + i * 36, y + 56, 14, 52, WHITE)
    cv.fill_rect(x + 30, y + 108, 120, 8, WHITE)
    # gavel on the steps
    cv.draw_line(x + 52, y + 96, x + 96, y + 76, (150, 100, 50), 5)
    cv.fill_rect(x + 92, y + 66, 26, 12, (150, 100, 50))
    # rocket, right
    rx = x + w - 150
    ry = y + 14
    cv.fill_polygon([(rx + 20, ry), (rx + 40, ry + 26),
                     (rx, ry + 26)], RED)
    cv.fill_rect(rx, ry + 26, 40, 58, WHITE)
    cv.draw_rect(rx, ry + 26, 40, 58, INK, 2)
    cv.fill_polygon([(rx, ry + 84), (rx - 16, ry + 104),
                     (rx, ry + 96)], RED)
    cv.fill_polygon([(rx + 40, ry + 84), (rx + 56, ry + 104),
                     (rx + 40, ry + 96)], RED)
    cv.fill_polygon([(rx + 12, ry + 84), (rx + 28, ry + 84),
                     (rx + 20, ry + 112)], ORANGE)
    cv.draw_text(rx - 6, y + 44, "X", 4, (200, 200, 210))


def scene_bomb(cv, x, y, w, h):
    """Iowa: a bomb with a lit fuse, crossed by a white pause bar."""
    cv.fill_rect(x, y, w, h, (122, 32, 28))
    # warning stripes along the bottom, under the bomb only
    for i in range(5):
        stripe_x = x + i * 42
        colour = YELLOW if i % 2 == 0 else INK
        cv.fill_polygon([(stripe_x, y + h), (stripe_x + 21, y + h),
                         (stripe_x + 42, y + h - 18),
                         (stripe_x + 21, y + h - 18)], colour)
    # bomb body
    bx, by = x + 150, y + 62
    cv.fill_circle(bx, by, 40, INK)
    cv.fill_rect(bx - 8, by - 50, 16, 12, INK)
    cv.draw_line(bx, by - 50, bx + 34, by - 66, GOLD, 3)
    cv.draw_star(bx + 40, by - 70, 8, YELLOW)
    # pause: two white bars mean "hold"
    cv.fill_rect(x + w - 150, y + 30, 26, 62, WHITE)
    cv.fill_rect(x + w - 106, y + 30, 26, 62, WHITE)
    cv.draw_text(x + w - 168, y + 94, "HOLD", 3, WHITE)


def scene_eu(cv, x, y, w, h):
    """EU: a ring of gold stars around a bank, cut by a red slash."""
    cv.fill_rect(x, y, w, h, EU_BLUE)
    # ring of twelve stars
    cx, cy = x + w // 2, y + h // 2
    for i in range(12):
        angle = i * 30.0 * 3.141592653589793 / 180.0
        sx = int(cx + 150 * math.cos(angle))
        sy = int(cy + 42 * math.sin(angle))
        cv.draw_star(sx, sy, 6, YELLOW)
    # bank building in the middle
    cv.fill_polygon([(cx - 70, cy - 8), (cx + 70, cy - 8),
                     (cx, cy - 34)], WHITE)
    for i in range(4):
        cv.fill_rect(cx - 58 + i * 32, cy - 4, 12, 40, WHITE)
    cv.fill_rect(cx - 72, cy + 38, 144, 8, WHITE)
    # red slash across the whole scene
    cv.draw_line(x + 24, y + h - 18, x + w - 24, y + 18, RED, 7)


# ---------------------------------------------------------------------------
# Stories: kicker, colour, headline, deck, scene.
# Headlines verified on 24 November 2026 against AP / Reuters reporting.
# ---------------------------------------------------------------------------
STORIES = [
    ("TECH", GREEN, scene_chip,
     "NVIDIA BRINGS BACK JENSEN HUANG AS CEO",
     "BOARD VOTES UNANIMOUSLY; SHARES SURGE 33%"),
    ("POLITICS", BLUE, scene_capitol,
     "DEMOCRATS CLINCH HISTORIC HOUSE MAJORITY",
     "258 SEATS, LARGEST SINCE 1992"),
    ("WAR", RED, scene_ship,
     "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
     "SEA DRONES HIT CORVETTE MERKURY IN BENGHAZI"),
    ("COURTS", (90, 60, 140), scene_rocket,
     "TWO STATES SUE SPACEX OVER GROK IMAGES",
     "VIRGINIA AND OREGON ALLEGE CSAM FAILURES"),
    ("WHITE HOUSE", ORANGE, scene_bomb,
     "TRUMP HALTS IOWA BOMB BLAST",
     "ARMY MUST WAIT FOR COURT ON LEAD AZIDE"),
    ("EUROPE", EU_BLUE, scene_eu,
     "EU UNVEILS SWEEPING RUSSIA SANCTIONS",
     "60 BANKS OFF SWIFT; CRYPTO AND SPORTS HIT"),
]


# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------
MARGIN = 24
HEADER_H = 108
FOOTER_H = 42
PANEL_W = 488
PANEL_H = 252
GAP = 16
KICKER_H = 26
ILLUSTRATION_H = 118


def draw_panel(cv, px, py, story):
    kicker, colour, scene, headline, deck = story
    cv.fill_rect(px, py, PANEL_W, PANEL_H, WHITE)
    cv.draw_rect(px, py, PANEL_W, PANEL_H, INK, 2)
    # kicker strip
    cv.fill_rect(px + 2, py + 2, PANEL_W - 4, KICKER_H, colour)
    cv.draw_text(px + 14, py + 8, kicker, 2, WHITE)
    # illustration
    ix = px + 2
    iy = py + 2 + KICKER_H
    scene(cv, ix, iy, PANEL_W - 4, ILLUSTRATION_H)
    cv.fill_rect(ix, iy + ILLUSTRATION_H, PANEL_W - 4, 2, INK)
    # headline and deck
    tx = px + 14
    ty = iy + ILLUSTRATION_H + 12
    cv.draw_block(tx, ty, PANEL_W - 28, headline, 3, INK, leading=26)
    dy = ty + 2 * 26 + 4
    cv.draw_block(tx, dy, PANEL_W - 28, deck, 2, GREY, leading=18)


def draw_masthead(cv):
    cv.fill_rect(0, 0, WIDTH, HEADER_H, NAVY)
    cv.fill_rect(0, HEADER_H - 6, WIDTH, 6, RED)
    cv.draw_text_centered(0, 16, WIDTH, "WORLD NEWS", 8, WHITE)
    cv.draw_text_centered(0, 78, WIDTH,
                          "TUESDAY, 24 NOVEMBER 2026", 2, GOLD)


def draw_footer(cv):
    fy = HEIGHT - FOOTER_H
    cv.fill_rect(0, fy, WIDTH, FOOTER_H, NAVY_DARK)
    cv.draw_text_centered(0, fy + 8, WIDTH,
                          "SOURCES: AP / REUTERS / EUROPEAN COMMISSION",
                          2, WHITE)
    cv.draw_text_centered(0, fy + 26, WIDTH,
                          "DRAWN WITH PYTHON STDLIB ONLY - NO PHOTOS",
                          2, GOLD)


def build_poster():
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    draw_masthead(cv)
    grid_y = HEADER_H + GAP
    for row in range(3):
        for col in range(2):
            index = row * 2 + col
            px = MARGIN + col * (PANEL_W + GAP)
            py = grid_y + row * (PANEL_H + GAP)
            draw_panel(cv, px, py, STORIES[index])
    draw_footer(cv)
    return cv


# ---------------------------------------------------------------------------
# Minimal deterministic PNG encoder (colour type 2, 8-bit RGB).
# zlib output is deterministic for fixed input and level, and the file
# carries no ancillary chunk, so no timestamp can leak in.
# ---------------------------------------------------------------------------
def png_chunk(kind, data):
    out = struct.pack(">I", len(data))
    out += kind
    out += data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    header = struct.pack(">IIBBBBB", cv.width, cv.height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.width * 3
    for y in range(cv.height):
        raw.append(0)
        start = y * stride
        raw += cv.pixels[start:start + stride]
    payload = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", header)
    png += png_chunk(b"IDAT", payload)
    png += png_chunk(b"IEND", b"")
    return png


def main():
    poster = build_poster()
    data = encode_png(poster)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "wb") as handle:
        handle.write(data)
    print("wrote %s (%d bytes)" % (OUT_PATH, len(data)))


if __name__ == "__main__":
    main()
