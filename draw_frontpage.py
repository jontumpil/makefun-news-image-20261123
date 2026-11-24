"""Draw the front page for Monday 23 November 2026.

Standard library only. Renders a 1024x1024 newspaper front page
("THE WORLD IN ONE DAY") from the story data below, compositing the
four editorial illustrations in assets/, and writes a PNG.
Deterministic: fixed iteration order, fixed zlib level, no clock,
no randomness.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 234)
INK = (18, 18, 18)
RED = (178, 34, 34)
GREY = (96, 96, 96)
RULE = (60, 60, 60)
CARD_BG = (255, 255, 255)
BOX_BG = (238, 232, 214)

# 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit value,
# bit 4 = leftmost pixel. Written out by hand for this entry.
FONT_UPPER = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
}

FONT_DIGITS = {
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
}

FONT_LOWER = {
    "a": (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    "b": (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x1E),
    "c": (0x00, 0x00, 0x0E, 0x11, 0x10, 0x11, 0x0E),
    "d": (0x01, 0x01, 0x0D, 0x13, 0x11, 0x11, 0x0F),
    "e": (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    "f": (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    "g": (0x00, 0x0E, 0x10, 0x10, 0x13, 0x11, 0x0E),
    "h": (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x11),
    "i": (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    "j": (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    "k": (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    "n": (0x00, 0x00, 0x16, 0x19, 0x11, 0x11, 0x11),
    "o": (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    "p": (0x00, 0x00, 0x1E, 0x11, 0x1E, 0x10, 0x10),
    "q": (0x00, 0x00, 0x0D, 0x13, 0x0F, 0x01, 0x01),
    "r": (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    "s": (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    "t": (0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06),
    "u": (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    "v": (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "w": (0x00, 0x00, 0x11, 0x11, 0x15, 0x15, 0x1B),
    "x": (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    "y": (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "z": (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
}

FONT_PUNCT = {
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
}

FONT = {}
FONT.update(FONT_UPPER)
FONT.update(FONT_DIGITS)
FONT.update(FONT_LOWER)
FONT.update(FONT_PUNCT)

BLANK = (0x00,) * 7


def glyph(ch):
    return FONT.get(ch, BLANK)


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(canvas, x, y, text, color, scale=1):
    """Draw text at (x, y); returns the x position after the text."""
    cx = x
    for ch in text:
        g = glyph(ch)
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    for dy in range(scale):
                        for dx in range(scale):
                            canvas.set(cx + col * scale + dx,
                                       y + row * scale + dy, color)
        cx += 6 * scale
    return cx


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(w * h * 3)
        for i in range(w * h):
            self.pix[i * 3] = bg[0]
            self.pix[i * 3 + 1] = bg[1]
            self.pix[i * 3 + 2] = bg[2]

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i] = color[0]
            self.pix[i + 1] = color[1]
            self.pix[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        for xx in range(x, x + w):
            self.set(xx, y, color)

    def vline(self, x, y, h, color):
        for yy in range(y, y + h):
            self.set(x, yy, color)

    def box(self, x, y, w, h, color):
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)


def _paeth(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def read_png(path):
    """Read an 8-bit non-interlaced RGB or RGBA PNG. Returns (w, h, pixels)."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: " + path)
    pos = 8
    w = h = None
    bitdepth = colortype = interlace = None
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            w, h, bitdepth, colortype, comp, filt, interlace = struct.unpack(
                ">IIBBBBB", chunk)
        elif ctype == b"IDAT":
            idat += chunk
        elif ctype == b"IEND":
            break
        pos += 12 + length
    if bitdepth != 8 or interlace != 0:
        raise ValueError("unsupported PNG (need 8-bit, non-interlaced)")
    if colortype == 2:
        channels = 3
    elif colortype == 6:
        channels = 4
    else:
        raise ValueError("unsupported PNG colour type")
    raw = zlib.decompress(bytes(idat))
    stride = w * channels
    out = bytearray(w * h * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            if f == 1:
                line[i] = (line[i] + a) & 0xFF
            elif f == 2:
                line[i] = (line[i] + b) & 0xFF
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 0xFF
            elif f == 4:
                line[i] = (line[i] + _paeth(a, b, c)) & 0xFF
        for x in range(w):
            o = (y * w + x) * 3
            s = x * channels
            out[o] = line[s]
            out[o + 1] = line[s + 1]
            out[o + 2] = line[s + 2]
        prev = line
    return w, h, out


def blit_cover(canvas, path, x, y, w, h):
    """Draw an image cropped to cover the target box (centre crop)."""
    sw, sh, pix = read_png(path)
    scale = max(w / sw, h / sh)
    cw = int(w / scale)
    ch = int(h / scale)
    ox = (sw - cw) // 2
    oy = (sh - ch) // 2
    for ty in range(h):
        sy = oy + int(ty / scale)
        if sy >= sh:
            sy = sh - 1
        for tx in range(w):
            sx = ox + int(tx / scale)
            if sx >= sw:
                sx = sw - 1
            s = (sy * sw + sx) * 3
            canvas.set(x + tx, y + ty, (pix[s], pix[s + 1], pix[s + 2]))


def write_png(path, canvas):
    def chunk(ctype, payload):
        out = struct.pack(">I", len(payload)) + ctype + payload
        out += struct.pack(">I", zlib.crc32(ctype + payload) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        start = y * canvas.w * 3
        raw += canvas.pix[start:start + canvas.w * 3]
    comp = zlib.compress(bytes(raw), 6)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


# ---- The day's stories, all dated Monday 23 November 2026 ----
# tag: CONFIRMED = the event happened on 23 Nov 2026.
#      REPORTED  = first widely reported on 23 Nov 2026 (event at the
#      weekend, with its 23 Nov development stated in the headline).

TOP = [
    ("assets/nvidia.png", "MARKETS",
     "Huang returns: Nvidia reinstates its chief executive",
     "Eleven days after he resigned, Jensen Huang is back at Nvidia. "
     "Shares jump 33% and Wall Street rallies.",
     "Reuters", "CONFIRMED"),
    ("assets/benghazi.png", "WAR AT SEA",
     "Ukraine drones strike Russian ships off Libya",
     "Zelenskyy says sea drones hit two Russian ships in the port of "
     "Benghazi, taking the war far beyond Europe.",
     "Reuters / Al Jazeera", "CONFIRMED"),
    ("assets/cop31.png", "CLIMATE",
     "COP31 ends in Antalya with no climate deal",
     "The longest UN climate talks in history close without agreement "
     "as countries split over fossil fuels and money.",
     "Reuters / Just Security", "REPORTED"),
    ("assets/sinaloa.png", "MEXICO",
     "Mexico captures fugitive 'El Chapo Isidro'",
     "Special forces seize FBI most-wanted Fausto Isidro Meza Flores "
     "in Sinaloa; 16 suspected cartel gunmen are killed.",
     "Reuters", "CONFIRMED"),
]

# Each story: (region, headline, source, tag)
STORIES = [
    ("NORTH AMERICA",
     "Nvidia reinstates Jensen Huang as CEO; shares leap 33%",
     "Reuters", "CONFIRMED"),
    ("NORTH AMERICA",
     "Wall Street rebounds: S&P 500 up 5%, Nasdaq up 6%",
     "Reuters", "CONFIRMED"),
    ("NORTH AMERICA",
     "Democrats clinch 258 House seats, biggest majority since 1992",
     "AP / CBS", "REPORTED"),
    ("NORTH AMERICA",
     "Trump orders Army to pause Iowa lead azide detonation",
     "Reuters", "CONFIRMED"),
    ("NORTH AMERICA",
     "CrowdStrike to buy rival Zscaler in $43.9bn all-stock deal",
     "Reuters", "CONFIRMED"),
    ("NORTH AMERICA",
     "Pennsylvania measles deaths rise to nine; 1,638 cases",
     "Reuters", "CONFIRMED"),
    ("NORTH AMERICA",
     "Tom Jackson, Broncos star and ESPN voice, dies aged 75",
     "ESPN", "REPORTED"),
    ("LATIN AMERICA",
     "Mexico captures 'El Chapo Isidro' in Sinaloa raid",
     "Reuters", "CONFIRMED"),
    ("LATIN AMERICA",
     "Ex-leaders: Latin America 'doesn't want to be the US domain'",
     "Reports", "REPORTED"),
    ("LATIN AMERICA",
     "Brazil's Bovespa slips 0.95% as Wall Street rallies",
     "One Turn", "REPORTED"),
]

STORIES += [
    ("EUROPE",
     "COP31 climate talks end with no deal after longest session ever",
     "Reuters", "REPORTED"),
    ("EUROPE",
     "EU proposes 22nd package of sanctions against Russia",
     "EU Commission", "CONFIRMED"),
    ("EUROPE",
     "NATO meeting in Berlin warns Russia; space defence pledged",
     "Reports", "REPORTED"),
    ("EUROPE",
     "UK and EU sign historic post-Brexit reconciliation pact",
     "Reports", "REPORTED"),
    ("EUROPE",
     "German parliament passes sweeping post-war intelligence reform",
     "Reports", "REPORTED"),
    ("EUROPE",
     "Spain's right on course for clear majority, polls show",
     "Reports", "REPORTED"),
    ("EUROPE",
     "Finland backs anti-tank barriers on its border with Russia",
     "Reports", "REPORTED"),
    ("EUROPE",
     "Clariant and CD&R in talks to buy US chemicals firm Ashland",
     "Reuters", "CONFIRMED"),
    ("EUROPE",
     "EU Commission confirms data breach after cyberattack",
     "Reports", "REPORTED"),
    ("MIDDLE EAST",
     "Iran vows 'all means' against US blockade; 'downed US drone'",
     "Reports", "CONFIRMED"),
    ("MIDDLE EAST",
     "US sanctions 20+ targets in Iran's shadow banking network",
     "Reports", "CONFIRMED"),
    ("MIDDLE EAST",
     "Iran's president turns off office lights to save power",
     "Reports", "REPORTED"),
    ("MIDDLE EAST",
     "Netanyahu-Eisenkot coalition talks end with no deal",
     "Reports", "REPORTED"),
    ("MIDDLE EAST",
     "UNRWA: one staffer killed, three hurt in Israeli Gaza strike",
     "UNRWA", "REPORTED"),
    ("MIDDLE EAST",
     "Severely injured Gaza children evacuated to Britain",
     "Reports", "REPORTED"),
    ("MIDDLE EAST",
     "Houthi attacks in Yemen's Taiz kill two, injure eight",
     "Reports", "REPORTED"),
]

STORIES += [
    ("AFRICA",
     "Ukraine sea drones hit Russian ships at Benghazi, Libya",
     "Reuters", "CONFIRMED"),
    ("AFRICA",
     "Nigeria boat toll rises to 29; Tinubu approves aid for families",
     "NEMA / BBC", "REPORTED"),
    ("AFRICA",
     "Libya's parliament launches government unification initiative",
     "Reports", "REPORTED"),
    ("AFRICA",
     "Attack on UN building in Khartoum condemned by Saudi Arabia",
     "Reports", "REPORTED"),
    ("ASIA-PACIFIC",
     "Indonesia confirms 24 dead in factory fire; 30 still missing",
     "Reuters", "REPORTED"),
    ("ASIA-PACIFIC",
     "Nikkei falls over 5% as Asian chip stocks slide",
     "Al Jazeera", "CONFIRMED"),
    ("ASIA-PACIFIC",
     "India pledges $1.63bn to rebuild Nepal after glacier flood",
     "Reports", "CONFIRMED"),
    ("ASIA-PACIFIC",
     "China agrees to a new AI dialogue mechanism",
     "Reports", "REPORTED"),
    ("ASIA-PACIFIC",
     "SK Hynix jumps 20% after Huang's return to Nvidia",
     "Reports", "REPORTED"),
    ("ASIA-PACIFIC",
     "Molly Meldrum, Australian music legend, dies aged 83",
     "Reports", "REPORTED"),
    ("GLOBAL",
     "UN chief urges a global AI safety framework within a year",
     "Reports", "REPORTED"),
    ("GLOBAL",
     "Sweden partners on a worldwide AI protection centre",
     "Reports", "REPORTED"),
    ("GLOBAL",
     "700,000+ Russian troops killed by end of September: Meduza",
     "Meduza", "REPORTED"),
    ("GLOBAL",
     "Thousands rally in Istanbul against opposition crackdown",
     "Reports", "REPORTED"),
]

REGIONS = ["NORTH AMERICA", "LATIN AMERICA", "EUROPE", "MIDDLE EAST",
           "AFRICA", "ASIA-PACIFIC", "GLOBAL"]


def wrap_text(text, max_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        if cur == "":
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur = cur + " " + word
        else:
            lines.append(cur)
            cur = word
    if cur != "":
        lines.append(cur)
    return lines


def draw_centered(canvas, y, text, color, scale=1):
    w = text_width(text, scale)
    draw_text(canvas, (W - w) // 2, y, text, color, scale)


def draw_masthead(canvas):
    canvas.rect(0, 0, W, 6, INK)
    draw_centered(canvas, 16, "THE WORLD IN ONE DAY", INK, 5)
    canvas.hline(16, 60, W - 32, RULE)
    draw_centered(canvas, 68, "MONDAY 23 NOVEMBER 2026", RED, 2)
    draw_centered(canvas, 88,
                  "40 dated stories - 7 regions - Full day, morning to night",
                  INK, 1)
    canvas.hline(16, 104, W - 32, INK)
    canvas.hline(16, 107, W - 32, INK)


def draw_cards(canvas, base):
    xs = [16, 266, 516, 766]
    cw = 242
    y0 = 118
    for i, top in enumerate(TOP):
        asset, kicker, head, deck, source, tag = top
        x = xs[i]
        draw_text(canvas, x, y0, kicker, RED, 1)
        blit_cover(canvas, os.path.join(base, asset), x, y0 + 11, cw, 165)
        canvas.box(x, y0 + 11, cw, 165, RULE)
        yy = y0 + 182
        for line in wrap_text(head, 40):
            draw_text(canvas, x, yy, line, INK, 1)
            yy += 9
        yy += 2
        for line in wrap_text(deck, 40):
            draw_text(canvas, x, yy, line, GREY, 1)
            yy += 9
        draw_text(canvas, x, yy + 1, source + " - " + tag, RED, 1)


def draw_region(canvas, x, y, w, region, stories):
    draw_text(canvas, x, y, region, RED, 2)
    y += 18
    canvas.hline(x, y, w, RULE)
    y += 8
    for headline, source, tag in stories:
        line = "- " + headline + " (" + source + ", " + tag + ")"
        for part in wrap_text(line, w // 6):
            draw_text(canvas, x, y, part, INK, 1)
            y += 11
        y += 4
    return y


def draw_list(canvas):
    left = [r for r in REGIONS[:3]]
    right = [r for r in REGIONS[3:]]
    y = 396
    for col_x, col_regions in ((16, left), (516, right)):
        yy = y
        for region in col_regions:
            items = [(h, s, t) for (r, h, s, t) in STORIES if r == region]
            yy = draw_region(canvas, col_x, yy, 492, region, items)
            yy += 6


def draw_datecheck(canvas):
    x, y, w, h = 16, 910, 992, 58
    canvas.rect(x, y, w, h, BOX_BG)
    canvas.box(x, y, w, h, INK)
    draw_text(canvas, x + 10, y + 8,
              "DATE CHECK: Every story above is dated Monday 23 November 2026.",
              INK, 1)
    draw_text(canvas, x + 10, y + 22,
              "CONFIRMED = event happened 23 Nov.  REPORTED = first widely",
              INK, 1)
    draw_text(canvas, x + 10, y + 34,
              "reported 23 Nov.  Sources: Reuters, AP, CBS, Al Jazeera, BBC,",
              INK, 1)
    draw_text(canvas, x + 10, y + 46,
              "UNRWA, NEMA, Meduza, EU Commission.",
              INK, 1)


def build(target):
    base = os.path.dirname(os.path.abspath(__file__))
    canvas = Canvas(W, H, PAPER)
    draw_masthead(canvas)
    draw_cards(canvas, base)
    canvas.hline(16, 388, W - 32, INK)
    draw_list(canvas)
    draw_datecheck(canvas)
    draw_centered(canvas, 984,
                  "THE WORLD IN ONE DAY - a one-page summary of "
                  "Monday 23 November 2026",
                  GREY, 1)
    write_png(target, canvas)
