"""Front-page renderer for THE WORLD IN ONE DAY - Monday 23 November 2026.

Standard library only: struct, zlib, os. No Pillow, no third-party code.
Owns a 5x7 bitmap font, a tiny RGB canvas, a PNG reader (for the
illustrated assets) and a PNG writer. Deterministic: no clock, no random,
fixed iteration order, fixed zlib level.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- font 5x7
# Each glyph is 7 rows of 5 bits, written as strings of 0/1.
_FONT = {
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
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

# Pre-convert glyph rows to integer bitmasks, once, in fixed order.
_GLYPHS = {}
for _ch, _rows in _FONT.items():
    _GLYPHS[_ch] = tuple(int(r, 2) for r in _rows)
_BLANK = (0, 0, 0, 0, 0, 0, 0)


def _glyph(ch):
    return _GLYPHS.get(ch.upper(), _BLANK)


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px per char cell)."""
    return len(text) * 6 * scale - scale


# ------------------------------------------------------------------- canvas
class Page(object):
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def set(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = rgb[0]
            self.px[i + 1] = rgb[1]
            self.px[i + 2] = rgb[2]

    def rect(self, x, y, w, h, rgb):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(rgb) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, rgb, thick=1):
        self.rect(x, y, w, thick, rgb)

    def text(self, x, y, s, scale, rgb):
        cx = x
        for ch in s:
            g = _glyph(ch)
            for r in range(7):
                bits = g[r]
                if not bits:
                    continue
                for c in range(5):
                    if bits >> (4 - c) & 1:
                        self.rect(cx + c * scale, y + r * scale,
                                  scale, scale, rgb)
            cx += 6 * scale
        return cx

    def text_centred(self, y, s, scale, rgb):
        w = text_width(s, scale)
        self.text((self.w - w) // 2, y, s, scale, rgb)

    def wrap(self, s, scale, maxw):
        """Greedy word wrap; returns a list of lines."""
        lines = []
        cur = ""
        for word in s.split(" "):
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def blit(self, img, dx, dy, dw, dh, sy0=0, sh=None):
        """Paste RGB image (w, h, bytes) scaled to dw x dh, optionally
        cropping source rows sy0..sy0+sh first (nearest neighbour)."""
        sw, sh_src, data = img
        if sh is None:
            sh = sh_src - sy0
        for y in range(dh):
            sy = sy0 + (y * sh) // dh
            if sy >= sh_src:
                sy = sh_src - 1
            srow = sy * sw * 3
            drow = (dy + y) * self.w + dx
            for x in range(dw):
                sx = (x * sw) // dw
                si = srow + sx * 3
                di = (drow + x) * 3
                self.px[di] = data[si]
                self.px[di + 1] = data[si + 1]
                self.px[di + 2] = data[si + 2]


# ------------------------------------------------------------- PNG read/write
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
    """Decode a PNG (8-bit, colour types 0/2/3/4/6) to (w, h, rgb bytes)."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: " + path)
    pos = 8
    w = h = None
    bitdepth = ctype = None
    palette = None
    idat = bytearray()
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            w, h, bitdepth, ctype, _, _, _ = struct.unpack(">IIBBBBB", chunk)
        elif typ == b"PLTE":
            palette = chunk
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"IEND":
            break
    if w is None:
        raise ValueError("no IHDR in " + path)
    raw = zlib.decompress(bytes(idat))
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    if bitdepth == 16:
        bpp = channels * 2
    elif bitdepth == 8:
        bpp = channels
    else:
        bpp = 1  # sub-byte: one byte per pixel after unpacking below
    stride = (w * bitdepth * channels + 7) // 8
    out = bytearray(w * h * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ftype = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if ftype == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif ftype == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif ftype == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + _paeth(a, b, c)) & 255
        prev = line
        # Convert one scanline to RGB.
        base = y * w * 3
        if ctype == 2 and bitdepth == 8:
            out[base:base + w * 3] = line[:w * 3]
        elif ctype == 6 and bitdepth == 8:
            for x in range(w):
                s = x * 4
                d = base + x * 3
                out[d] = line[s]
                out[d + 1] = line[s + 1]
                out[d + 2] = line[s + 2]
        elif ctype == 0 and bitdepth == 8:
            for x in range(w):
                v = line[x]
                d = base + x * 3
                out[d] = v
                out[d + 1] = v
                out[d + 2] = v
        elif ctype == 3:
            for x in range(w):
                idx = line[x] * 3
                d = base + x * 3
                out[d] = palette[idx]
                out[d + 1] = palette[idx + 1]
                out[d + 2] = palette[idx + 2]
        elif ctype == 4 and bitdepth == 8:
            for x in range(w):
                v = line[x * 2]
                d = base + x * 3
                out[d] = v
                out[d + 1] = v
                out[d + 2] = v
        elif bitdepth == 16 and ctype in (0, 2, 6):
            step = channels * 2
            for x in range(w):
                s = x * step
                d = base + x * 3
                if ctype == 0:
                    out[d] = out[d + 1] = out[d + 2] = line[s]
                else:
                    out[d] = line[s]
                    out[d + 1] = line[s + 2]
                    out[d + 2] = line[s + 4]
        else:
            # Sub-byte greyscale / palette: expand bit by bit.
            nbits = bitdepth
            mask = (1 << nbits) - 1
            for x in range(w):
                bitpos = x * nbits
                byte = line[bitpos // 8]
                shift = 8 - nbits - (bitpos % 8)
                v = (byte >> shift) & mask
                if ctype == 3:
                    idx = v * 3
                    d = base + x * 3
                    out[d] = palette[idx]
                    out[d + 1] = palette[idx + 1]
                    out[d + 2] = palette[idx + 2]
                else:
                    g = v * 255 // mask
                    d = base + x * 3
                    out[d] = g
                    out[d + 1] = g
                    out[d + 2] = g
    return (w, h, bytes(out))


def _chunk(typ, payload):
    out = struct.pack(">I", len(payload)) + typ + payload
    out += struct.pack(">I", zlib.crc32(typ + payload) & 0xFFFFFFFF)
    return out


def write_png(path, w, h, rgb):
    """Encode RGB bytes as a PNG with filter 0 on every row."""
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

# ------------------------------------------------------------------ content
PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (178, 34, 34)
BLUE = (28, 68, 118)
GREY = (96, 92, 84)
RULEC = (140, 130, 112)

# (region, headline) - every headline carries its report date.
REGIONS = [
    ("NORTH AMERICA", [
        "GUNFIRE AT CALIFORNIA CONCERT WOUNDS 9, ONE CRITICAL - 23 NOV",
        "TRUMP STILL TRYING TO REACH KIM; KIM HAS 'GHOSTED' HIM - 23 NOV",
        "MELAT KIROS, 29, FIRST GEN Z WOMAN ELECTED TO US CONGRESS - 23 NOV",
        "VERSTAPPEN WINS LAS VEGAS GP, 3RD WIN IN 4 YEARS - 22 NOV",
        "NVIDIA ROW: HUANG TIED TO SECRET AI-CHIP NETWORK TO CHINA - 23 NOV",
    ]),
    ("LATIN AMERICA", [
        "MEXICO CAPTURES FBI MOST-WANTED 'EL CHAPO ISIDRO' - 22 NOV",
        "PERU QUAKE M6.7: 1 DEAD, 16 HURT, 853 LEFT HOMELESS - 22 NOV",
        "BRAZIL EX-LEADER BOLSONARO 'STABLE' IN INTENSIVE CARE - 22 NOV",
        "PAREDES COLLAPSES IN TV INTERVIEW AFTER BOCA WIN - 22 NOV",
        "CONMEBOL BACKS INFANTINO FOR ANOTHER FIFA TERM - 21 NOV",
    ]),
    ("EUROPE", [
        "COP31 COLLAPSES IN ANTALYA AS EU REJECTS FOSSIL-FREE PACT - 22 NOV",
        "RUSSIAN DRONE TEARS THROUGH KYIV FLATS; 14 MISSING - 22 NOV",
        "RUSSIAN CARGO SHIP STILL ON FIRE OFF FINLAND - 23 NOV",
        "POLAND: RUSSIAN MISSILES AND DRONE CROSSED BORDER - 21 NOV",
        "UK AND EU REACH BREXIT RESET DEAL DESPITE FEES ROW - 20 NOV",
        "UN NATIONS AGREE TO KEEP TALKING ON LETHAL AI WEAPONS - 23 NOV",
    ]),
    ("MIDDLE EAST", [
        "IRAN CLAIMS MISSILE STRIKES ON US BASES IN BAHRAIN - 22 NOV",
        "HORMUZ CONFLICT ENTERS CRUCIAL STAGE, WAR SPREADS - 23 NOV",
        "SAUDI-LED COALITION INTERCEPTS HOUTHI MISSILE - 22 NOV",
        "NETANYAHU, EISENKOT END TALKS WITH NO GOVT DEAL - 22 NOV",
        "EISENKOT CALLS SETTLER VIOLENCE 'JEWISH TERRORISM' - 23 NOV",
        "SWIMMER CROSSES HORMUZ TO FLAG IRAN HARM TO ANIMALS - 23 NOV",
    ]),
    ("AFRICA", [
        "RUSSIAN SHIP HIT IN SUSPECTED DRONE ATTACK AT BENGHAZI - 22 NOV",
        "SOUTH SUDAN: 24 CIVILIANS KILLED IN FRESH VIOLENCE - 22 NOV",
        "DRONE STRIKES KILL 5 CHILDREN IN KHARTOUM, OMDURMAN - 22 NOV",
        "NIGERIA: 35 FULANIS KILLED IN REVENGE ATTACKS - 22 NOV",
        "NIGERIA BOAT ACCIDENT DEATH TOLL RISES TO 29 - 22 NOV",
        "WHO CHIEF PLEADS FOR PEACE IN EBOLA-HIT DR CONGO - 22 NOV",
    ]),
    ("ASIA", [
        "INDONESIA CANDY FACTORY FIRE: 7 DEAD, 50 MISSING - 22 NOV",
        "SOUTH KOREA EDUCATION MINISTER QUITS OVER AI CHEATING - 23 NOV",
        "NEPAL PM SHAH HOLDS TALKS WITH MODI IN NEW DELHI - 23 NOV",
        "MYANMAR JUNTA CALLS ASEAN DECISION 'UNFAIR' - 22 NOV",
        "RESTORED OKINAWA CASTLE TO REOPEN WITH FIRE SAFETY - 23 NOV",
        "HELLO KITTY OWNER SANRIO BETS ON GAMES FOR GROWTH - 23 NOV",
    ]),
    ("OCEANIA", [
        "ALBANESE: COP31 FAILURE SIGN OF DIFFICULT TIMES - 23 NOV",
        "INDIA DECLARE RECORD 720/9 IN WELLINGTON TEST - 22 NOV",
        "BLACK CAPS BAT ON AS WELLINGTON TEST NEARS END - 23 NOV",
        "CALL TO DROP RELIGION FROM TERROR LAW 'MAKES NO SENSE' - 23 NOV",
    ]),
]

LEFT_COLUMN = ["NORTH AMERICA", "LATIN AMERICA", "EUROPE", "MIDDLE EAST"]
RIGHT_COLUMN = ["AFRICA", "ASIA", "OCEANIA"]

CARDS = [
    ("bahrain.png", "THE GULF - STRAIT OF HORMUZ",
     "IRAN STRIKES US BASES IN BAHRAIN"),
    ("ukraine.png", "UKRAINE - KYIV REGION",
     "DRONE TEARS THROUGH KYIV FLATS; 14 MISSING"),
    ("indonesia.png", "INDONESIA - SERANG, BANTEN",
     "FACTORY FIRE: 7 DEAD, 50 MISSING"),
]

LEAD_DECK = ("EU AND ALLIES REJECT A PACT WITH NO MENTION OF FOSSIL FUELS. "
             "THE LONGEST COP EVER ENDS WITH NO DEAL.")


def _region_map():
    return {name: items for name, items in REGIONS}


def _draw_column(pg, x, names, y):
    by_name = _region_map()
    for name in names:
        pg.rect(x, y + 2, 10, 10, RED)
        pg.text(x + 16, y, name, 2, INK)
        y += 22
        for story in by_name[name]:
            pg.rect(x + 2, y + 2, 3, 3, INK)
            pg.text(x + 10, y, story, 1, INK)
            y += 12
        y += 8
    return y


def build(out_path):
    base = os.path.dirname(os.path.abspath(__file__))
    pg = Page(1024, 1024, PAPER)

    # Masthead.
    pg.text_centred(8, "THE WORLD IN ONE DAY", 8, INK)
    pg.text_centred(70, "MONDAY 23 NOVEMBER 2026  -  38 DATED STORIES  -  7 REGIONS",
                    2, INK)
    pg.hline(16, 92, 992, INK, 2)

    # Lead story: COP31 illustration + headline.
    cop31 = read_png(os.path.join(base, "assets", "cop31.png"))
    pg.blit(cop31, 16, 102, 330, 150, sy0=34, sh=145)
    pg.text(362, 106, "CLIMATE SUMMIT - ANTALYA, TURKIYE", 2, RED)
    pg.text(362, 132, "COP31 COLLAPSES", 4, INK)
    pg.text(362, 164, "IN ANTALYA", 4, INK)
    y = 198
    for line in pg.wrap(LEAD_DECK, 2, 646):
        pg.text(362, y, line, 2, INK)
        y += 15
    pg.text(362, 236, "ANTALYA, TURKIYE - 22 NOVEMBER 2026 - 194 NATIONS, NO DEAL",
            1, GREY)
    pg.hline(16, 262, 992, RULEC, 1)

    # Three illustrated cards.
    for i, (fname, kicker, headline) in enumerate(CARDS):
        cx = 16 + i * 336
        img = read_png(os.path.join(base, "assets", fname))
        pg.blit(img, cx, 272, 320, 150, sy0=31, sh=150)
        pg.text(cx, 428, kicker, 1, RED)
        yy = 440
        for line in pg.wrap(headline, 2, 320):
            pg.text(cx, yy, line, 2, INK)
            yy += 15
    pg.hline(16, 486, 992, INK, 2)

    # Story lists, two columns.
    _draw_column(pg, 16, LEFT_COLUMN, 496)
    _draw_column(pg, 524, RIGHT_COLUMN, 496)

    # Footer.
    pg.hline(16, 992, 992, RULEC, 1)
    pg.text_centred(1002, "COMPILED FROM WIRE REPORTS FILED 22-23 NOVEMBER 2026 - "
                    "THE WORLD IN ONE DAY - MAKE.FUN NEWS-IMAGE-20261123",
                    1, GREY)

    write_png(out_path, 1024, 1024, bytes(pg.px))


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build(target)
