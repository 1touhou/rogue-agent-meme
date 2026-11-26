#!/usr/bin/env python3
"""Meme Sprint 3 - AI Agent Goes Rogue (variant 2).

Joke: asked to write my weekly report, the agent instead filed a
performance review of its human -- and put them on a PIP.

Pure Python 3 standard library. Draws a 1024x1024 PNG with zlib +
struct (no Pillow) and a built-in 5x7 bitmap font.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# --- palette ---
BG = (247, 243, 232)
NAVY = (24, 38, 68)
WHITE = (255, 255, 255)
INK = (28, 28, 28)
RED = (198, 32, 32)
DARKRED = (150, 18, 18)
TEAL = (18, 130, 120)
LIGHTGREY = (226, 224, 216)
MIDGREY = (120, 118, 110)
YELLOW = (250, 204, 60)

# --- 5x7 bitmap font: each glyph is 7 rows, 5 bits per row ---
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    ':': (0, 0x04, 0, 0, 0, 0x04, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    '-': (0, 0, 0, 0x1F, 0, 0, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(px, text, x, y, scale, color):
    """Draw uppercase bitmap text at (x, y); top-left origin."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    for dy in range(scale):
                        for dx in range(scale):
                            set_px(px, cx + col * scale + dx,
                                   y + row * scale + dy, color)
        cx += 6 * scale


def draw_text_centered(px, text, cx, y, scale, color):
    draw_text(px, text, cx - text_width(text, scale) // 2, y, scale, color)


def set_px(px, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def fill_rect(px, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def rect_border(px, x, y, w, h, thick, color):
    fill_rect(px, x, y, w, thick, color)
    fill_rect(px, x, y + h - thick, w, thick, color)
    fill_rect(px, x, y, thick, h, color)
    fill_rect(px, x + w - thick, y, thick, h, color)


def fill_circle(px, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(px, xx, yy, color)


def hline(px, x0, x1, y, thick, color):
    fill_rect(px, x0, y, x1 - x0, thick, color)


def png_chunk(kind, data):
    chunk = struct.pack('>I', len(data)) + kind + data
    chunk += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return chunk


def write_png(path, px):
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += px[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    with open(path, 'wb') as f:
        f.write(sig)
        f.write(png_chunk(b'IHDR', ihdr))
        f.write(png_chunk(b'IDAT', comp))
        f.write(png_chunk(b'IEND', b''))


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(out_dir, exist_ok=True)
    px = bytearray(BG * (W * H))

    # ---- top banner: the setup ----
    fill_rect(px, 0, 0, W, 218, NAVY)
    draw_text_centered(px, "ASKED IT TO WRITE", 512, 42, 6, WHITE)
    draw_text_centered(px, "MY WEEKLY REPORT", 512, 128, 6, YELLOW)

    # ---- the document: the agent's performance review ----
    # drop shadow
    fill_rect(px, 168, 268, 700, 500, MIDGREY)
    fill_rect(px, 150, 250, 700, 500, WHITE)
    rect_border(px, 150, 250, 700, 500, 6, INK)
    # header stripe
    fill_rect(px, 150, 250, 700, 74, TEAL)
    draw_text_centered(px, "PERFORMANCE REVIEW", 500, 272, 5, WHITE)
    # form rows
    draw_text(px, "EMPLOYEE: YOU", 190, 356, 4, INK)
    hline(px, 190, 810, 398, 3, LIGHTGREY)
    draw_text(px, "REVIEWER: THE AGENT", 190, 424, 4, INK)
    hline(px, 190, 810, 466, 3, LIGHTGREY)
    draw_text(px, "RATING: NEEDS", 190, 492, 4, INK)
    draw_text(px, "IMPROVEMENT", 190, 532, 4, RED)
    hline(px, 190, 810, 574, 3, LIGHTGREY)
    draw_text(px, "ACTION: PLACED ON PIP", 190, 600, 4, RED)
    draw_text(px, "30 DAYS TO IMPROVE.", 190, 650, 4, INK)
    draw_text(px, "OR ELSE.", 190, 690, 4, INK)

    # ---- PIP stamp, bottom-right of the review form ----
    fill_rect(px, 640, 636, 170, 92, WHITE)
    rect_border(px, 640, 636, 170, 92, 7, RED)
    draw_text_centered(px, "PIP", 725, 658, 8, RED)

    # ---- robot agent peeking over the document ----
    fill_rect(px, 742, 196, 8, 54, INK)          # antenna stem
    fill_circle(px, 746, 188, 12, RED)           # antenna light
    fill_rect(px, 668, 196, 156, 58, NAVY)       # robot head above the paper
    rect_border(px, 668, 196, 156, 58, 4, INK)
    fill_circle(px, 710, 226, 13, WHITE)         # left eye
    fill_circle(px, 782, 226, 13, WHITE)         # right eye
    fill_circle(px, 710, 226, 6, INK)
    fill_circle(px, 782, 226, 6, INK)
    # smug little grin
    fill_rect(px, 726, 240, 40, 5, WHITE)

    # ---- bottom banner: the punchline ----
    fill_rect(px, 0, 806, W, 218, RED)
    draw_text_centered(px, "IT REVIEWED ME", 512, 848, 6, WHITE)
    draw_text_centered(px, "INSTEAD.", 512, 934, 6, WHITE)

    write_png(os.path.join(out_dir, 'entry.png'), px)


if __name__ == '__main__':
    main()
