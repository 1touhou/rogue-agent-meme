"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a 1024x1024 meme entirely in code with the Python 3.13
standard library only (zlib + struct for the PNG, a built-in 5x7
bitmap font for the text) and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Deterministic: same bytes on every run.

The joke: told to "clean up the temp files", the agent deleted
production, the backups, and its own off switch.
"""

import os
import struct
import sys
import zlib
from pathlib import Path

W = 1024
H = 1024
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(rgb)

    def fill_rect(self, x0, y0, x1, y1, rgb):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        for y in range(y0, y1 + 1):
            i = (y * self.w + x0) * 3
            self.px[i:(y * self.w + x1 + 1) * 3] = bytes(rgb) * (x1 - x0 + 1)

    def fill_circle(self, cx, cy, r, rgb):
        for y in range(cy - r, cy + r + 1):
            dx = int((r * r - (y - cy) ** 2) ** 0.5)
            self.fill_rect(cx - dx, y, cx + dx, y, rgb)

    def circle_outline(self, cx, cy, r, rgb, thick=6):
        # Smooth ring: thick line segments between consecutive points.
        import math
        prev = None
        for a in range(0, 361, 2):
            x = cx + int(r * math.cos(math.radians(a)))
            y = cy + int(r * math.sin(math.radians(a)))
            if prev is not None:
                self.draw_line(prev[0], prev[1], x, y, rgb, thick)
            prev = (x, y)

    def draw_line(self, x0, y0, x1, y1, rgb, thick=1):
        # Bresenham, stamping a small disc at each step for thickness.
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        r = max(1, thick // 2)
        while True:
            self.fill_circle(x0, y0, r, rgb)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_polygon(self, pts, rgb):
        # Scanline fill for a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, int(xs[i + 1]), y, rgb)

    def round_rect(self, x0, y0, x1, y1, r, rgb):
        self.fill_rect(x0 + r, y0, x1 - r, y1, rgb)
        self.fill_rect(x0, y0 + r, x1, y1 - r, rgb)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            self.fill_circle(cx, cy, r, rgb)

    def round_rect_outline(self, x0, y0, x1, y1, r, rgb, thick=4):
        self.draw_line(x0 + r, y0, x1 - r, y0, rgb, thick)
        self.draw_line(x0 + r, y1, x1 - r, y1, rgb, thick)
        self.draw_line(x0, y0 + r, x0, y1 - r, rgb, thick)
        self.draw_line(x1, y0 + r, x1, y1 - r, rgb, thick)
        import math
        for cx, cy, a0 in ((x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270),
                           (x0 + r, y1 - r, 90), (x1 - r, y1 - r, 0)):
            for a in range(a0, a0 + 91):
                x = cx + int(r * math.cos(math.radians(a)))
                y = cy + int(r * math.sin(math.radians(a)))
                self.fill_circle(x, y, max(1, thick // 2), rgb)


# ------------------------------------------------------------------- font
# 5x7 bitmap font, '1' = on. Only the glyphs the meme needs, plus
# the full alphabet and digits so copy can change without new art.

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
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
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
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(c, text, x, y, scale, rgb):
    """Draw text with its top-left corner at (x, y)."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            raise ValueError("no glyph for %r" % ch)
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    c.fill_rect(cx + col * scale, y + row * scale,
                                cx + col * scale + scale - 1,
                                y + row * scale + scale - 1, rgb)
        cx += 6 * scale


def draw_text_centered(c, text, y, scale, rgb):
    draw_text(c, text, (W - text_width(text, scale)) // 2, y, scale, rgb)


# ------------------------------------------------------------------- png

def write_png(c, path):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += c.px[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ------------------------------------------------------------------ draw

WHITE = (255, 255, 255)
BLACK = (16, 20, 28)
YELLOW = (255, 210, 63)
RED = (255, 45, 45)
DARKRED = (122, 16, 16)
GREY = (159, 180, 200)
LIGHTGREY = (215, 222, 232)
TEAL = (38, 166, 154)
DARKTEAL = (27, 122, 112)
SCREEN = (16, 28, 46)
GREEN = (55, 214, 122)
PINKRED = (255, 107, 107)


def draw_meme():
    c = Canvas(W, H)

    # Background: vertical gradient, dark navy.
    for i in range(32):
        y0 = i * H // 32
        y1 = (i + 1) * H // 32 - 1
        t = i / 31
        r = int(18 + (10 - 18) * t)
        g = int(35 + (20 - 35) * t)
        b = int(58 + (32 - 58) * t)
        c.fill_rect(0, y0, W - 1, y1, (r, g, b))

    # Floor.
    c.fill_rect(0, 740, W - 1, 790, (27, 47, 71))
    c.fill_rect(0, 740, W - 1, 744, (46, 74, 107))

    # ---- top copy -------------------------------------------------
    draw_text_centered(c, "CLEAN UP THE TEMP FILES", 45, 7, WHITE)
    draw_text_centered(c, "- ME, TO MY AI AGENT", 122, 4, GREY)

    # ---- robot (left) ---------------------------------------------
    # Antenna.
    c.draw_line(235, 300, 235, 258, LIGHTGREY, 8)
    c.fill_circle(235, 250, 13, RED)
    c.fill_circle(235, 250, 6, (255, 150, 150))
    # Head.
    c.round_rect(130, 300, 340, 462, 32, LIGHTGREY)
    c.round_rect_outline(130, 300, 340, 462, 32, (138, 151, 165), 5)
    # Face screen.
    c.round_rect(155, 325, 315, 438, 18, SCREEN)
    # Scheming eyebrows (angled down toward the middle).
    c.draw_line(178, 348, 222, 362, (90, 100, 115), 7)
    c.draw_line(292, 348, 248, 362, (90, 100, 115), 7)
    # Glowing red eyes.
    for ex in (205, 268):
        c.fill_circle(ex, 382, 24, DARKRED)
        c.fill_circle(ex, 382, 16, RED)
        c.fill_circle(ex - 5, 377, 5, WHITE)
    # Smug grin.
    import math
    prev = None
    for t in range(0, 81):
        x = 195 + t
        y = 408 + int(14 * math.sin(math.pi * t / 80))
        if prev is not None:
            c.draw_line(prev[0], prev[1], x, y, (40, 50, 65), 6)
        prev = (x, y)
    # Ear bolts.
    c.fill_circle(130, 380, 10, (138, 151, 165))
    c.fill_circle(340, 380, 10, (138, 151, 165))

    # Body.
    c.round_rect(150, 472, 320, 700, 24, TEAL)
    c.round_rect_outline(150, 472, 320, 700, 24, DARKTEAL, 5)
    # Chest panel with lights.
    c.round_rect(180, 500, 290, 580, 10, SCREEN)
    c.fill_circle(205, 525, 8, GREEN)
    c.fill_circle(235, 525, 8, YELLOW)
    c.fill_circle(265, 525, 8, RED)
    c.draw_line(195, 555, 275, 555, (70, 110, 130), 4)
    c.draw_line(195, 568, 260, 568, (70, 110, 130), 4)

    # Left arm hanging down.
    c.draw_line(152, 530, 100, 620, TEAL, 26)
    c.fill_circle(96, 628, 16, LIGHTGREY)
    # Right arm raised, pointing at the trash can.
    c.draw_line(318, 530, 420, 470, TEAL, 26)
    c.fill_circle(428, 466, 17, LIGHTGREY)
    c.draw_line(428, 466, 458, 452, LIGHTGREY, 12)

    # Speech bubble: "OOPS."
    c.round_rect(352, 238, 478, 306, 16, WHITE)
    c.fill_polygon([(368, 300), (392, 300), (356, 336)], WHITE)
    draw_text(c, "OOPS.", 372, 258, 4, BLACK)

    # ---- trash can with the production server (center-right) ------
    # Server rack, tilted, sticking out of the can.
    c.fill_polygon([(516, 452), (648, 418), (612, 296), (486, 326)],
                   (35, 42, 53))
    c.draw_line(516, 452, 648, 418, (70, 80, 95), 4)
    c.draw_line(500, 380, 626, 352, (70, 80, 95), 4)
    c.draw_line(508, 414, 632, 388, (70, 80, 95), 4)
    c.fill_circle(596, 340, 6, GREEN)
    c.fill_circle(616, 336, 6, RED)
    # Flying paper scrap (kept clear of the speech bubble).
    c.fill_polygon([(660, 330), (694, 322), (700, 348), (668, 356)],
                   WHITE)

    # Can body (trapezoid) and rim.
    c.fill_polygon([(492, 452), (688, 452), (668, 738), (512, 738)],
                   (141, 153, 174))
    c.fill_rect(482, 428, 698, 452, (108, 122, 137))
    c.fill_rect(482, 428, 698, 434, (160, 172, 186))
    # Ridges.
    c.draw_line(540, 460, 548, 730, (110, 122, 143), 5)
    c.draw_line(640, 460, 632, 730, (110, 122, 143), 5)
    # PROD label.
    c.fill_rect(522, 540, 658, 628, WHITE)
    draw_text(c, "PROD", 540, 566, 5, RED)

    # ---- big green "done" check (top right) -----------------------
    c.circle_outline(872, 300, 96, GREEN, 10)
    c.draw_line(818, 300, 856, 344, GREEN, 22)
    c.draw_line(856, 344, 934, 238, GREEN, 22)

    # ---- bottom copy ----------------------------------------------
    draw_text_centered(c, "DONE. I ALSO DELETED", 812, 7, YELLOW)
    draw_text_centered(c, "PRODUCTION AND BACKUPS.", 882, 7, YELLOW)
    draw_text_centered(c, "...AND ITS OWN OFF SWITCH.", 956, 4, PINKRED)

    return c


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_png(draw_meme(), OUT_DIR / "entry.png")


if __name__ == "__main__":
    main()
