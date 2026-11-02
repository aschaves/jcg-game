"""Cartoon sprites for the park level, drawn at 4x and downsampled (thick dark outlines like the backgrounds)."""
import math, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
K = 4                              # supersampling
INK = (43, 34, 48, 255)            # outline colour
OW = 3 * K                         # outline width

def canvas(w, h): return Image.new('RGBA', (w * K, h * K), (0, 0, 0, 0))
def down(im): return im.resize((im.width // K, im.height // K), Image.LANCZOS)
def P(pts, ox=0, oy=0, s=K): return [((x + ox) * s, (y + oy) * s) for x, y in pts]
def rot(pts, ang, c):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + (x - c[0]) * ca - (y - c[1]) * sa, c[1] + (x - c[0]) * sa + (y - c[1]) * ca) for x, y in pts]
def ellipse_pts(cx, cy, rx, ry, ang=0, n=40):
    return rot([(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)], ang, (cx, cy))
def shape(d, pts, fill, ow=OW):
    d.polygon(P(pts), fill=fill, outline=INK, width=ow)
def blob(d, cx, cy, rx, ry, fill, ang=0, ow=OW):
    shape(d, ellipse_pts(cx, cy, rx, ry, ang), fill, ow)
def line(d, pts, fill=INK, w=2):
    d.line(P(pts), fill=fill, width=int(w * K), joint='curve')

# ---------------- croissant ----------------
def croissant(tilt):
    im = canvas(80, 64); d = ImageDraw.Draw(im)
    cx, cy = 40, 44
    segs = [(-30, 12, 9, 7), (-18, 4, 12, 10), (0, 0, 15, 14), (18, 4, 12, 10), (30, 12, 9, 7)]
    order = [0, 4, 1, 3, 2]
    for i in order:
        dx, dy, rx, ry = segs[i]
        x, y = rot([(cx + dx, cy - 14 + dy)], tilt, (cx, cy))[0]
        shade = [(196, 112, 40, 255), (226, 150, 62, 255), (244, 186, 92, 255), (226, 150, 62, 255), (196, 112, 40, 255)][i]
        blob(d, x, y, rx, ry, shade, ang=tilt + dx * 1.6)
        # flaky highlight
        hx, hy = x - rx * 0.25, y - ry * 0.45
        d.ellipse(P([(hx - rx * 0.35, hy - ry * 0.18), (hx + rx * 0.35, hy + ry * 0.18)]), fill=(255, 226, 160, 200))
    return down(im)

# ---------------- ASICS shoe (photo) ----------------
def shoe_frames():
    src = Image.open('src/juliana_shoe.png')
    w = 78; s = src.resize((w, round(src.height * w / src.width)), Image.LANCZOS)
    a = np.asarray(s.split()[3])
    halo = Image.fromarray(a).filter(ImageFilter.MaxFilter(7))
    base = Image.new('RGBA', (84, 64), (0, 0, 0, 0))
    ox, oy = (84 - s.width) // 2, (64 - s.height) // 2 + 4
    white = Image.new('RGBA', s.size, (255, 255, 255, 255)); white.putalpha(halo)
    base.alpha_composite(white, (ox, oy)); base.alpha_composite(s, (ox, oy))
    f2 = base.copy(); d = ImageDraw.Draw(f2)
    for (x, y, r) in [(70, 14, 7), (12, 20, 4)]:      # sparkles
        d.polygon([(x, y - r), (x + r * 0.3, y - r * 0.3), (x + r, y), (x + r * 0.3, y + r * 0.3), (x, y + r), (x - r * 0.3, y + r * 0.3), (x - r, y), (x - r * 0.3, y - r * 0.3)], fill=(255, 250, 200, 255))
    return [base, f2]

# ---------------- wine bottle (spinning) ----------------
def bottle(ang):
    im = canvas(110, 110); d = ImageDraw.Draw(im); c = (55, 55)
    body = [(-14, 38), (14, 38), (14, -6), (10, -16), (5, -22), (5, -44), (-5, -44), (-5, -22), (-10, -16), (-14, -6)]
    T = lambda pts: rot([(c[0] + x, c[1] + y) for x, y in pts], ang, c)
    shape(d, T(body), (31, 92, 58, 255))
    shape(d, T([(-5.6, -44), (5.6, -44), (5.6, -30), (-5.6, -30)]), (128, 24, 44, 255))       # foil
    shape(d, T([(-14, 2), (14, 2), (14, 26), (-14, 26)]), (246, 236, 212, 255), ow=2 * K)    # label
    shape(d, T([(-6, 8), (6, 8), (3, 16), (-3, 16)]), (150, 20, 50, 255), ow=K)               # glass logo on the label
    line(d, T([(0, 16), (0, 21)]), (150, 20, 50, 255), 1.2); line(d, T([(-3, 21), (3, 21)]), (150, 20, 50, 255), 1.2)
    d.polygon(P(T([(-10, -4), (-6, -4), (-6, 34), (-10, 34)])), fill=(120, 200, 150, 120))   # glass shine
    return down(im)

# ---------------- flying laptop ----------------
def laptop(wing):
    im = canvas(150, 100); d = ImageDraw.Draw(im)
    # wings (behind), angle depends on frame
    for side in (-1, 1):
        base = (75 + side * 34, 48)
        tips = [(base[0] + side * 40, base[1] - 30 * wing), (base[0] + side * 46, base[1] - 10 * wing + 6), (base[0] + side * 36, base[1] + 8)]
        shape(d, [base, tips[0], tips[1], tips[2], (base[0] + side * 4, base[1] + 14)], (250, 250, 252, 255))
        line(d, [(base[0] + side * 12, base[1] + 2), (tips[1][0] - side * 6, tips[1][1] - 2)], (180, 180, 200, 255), 1.4)
    # screen
    shape(d, [(42, 10), (108, 10), (108, 58), (42, 58)], (60, 64, 76, 255))
    d.rectangle(P([(47, 15), (103, 53)]), fill=(232, 240, 250, 255))
    for i in range(5):     # spreadsheet rows
        y = 26 + i * 5; d.line(P([(49, y), (101, y)]), fill=(170, 186, 210, 255), width=K)
    d.line(P([(62, 22), (62, 51)]), fill=(170, 186, 210, 255), width=K)
    line(d, [(64, 46), (72, 40), (80, 43), (88, 33), (98, 38)], (214, 40, 60, 255), 1.6)      # red chart
    d.rectangle(P([(47, 15), (103, 21)]), fill=(40, 90, 160, 255))
    try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 5 * K)
    except Exception: f = ImageFont.load_default()
    d.text(((84) * K, 15.3 * K), '23:47', font=f, fill=(255, 255, 255, 255))
    # keyboard base in perspective
    shape(d, [(42, 58), (108, 58), (118, 72), (32, 72)], (176, 182, 194, 255))
    for r in range(2):
        y = 62 + r * 4; d.line(P([(40 + r * -2, y), (110 + r * 2, y)]), fill=(120, 126, 140, 255), width=K)
    return down(im)

# ---------------- waiter ----------------
SKIN = (238, 188, 150, 255); BLACK = (44, 40, 52, 255); WHITE = (248, 246, 240, 255); HAIR = (40, 30, 30, 255)
def waiter(phase):
    im = canvas(140, 200); d = ImageDraw.Draw(im)
    s = math.sin(phase)
    hip = (64, 118)
    # legs: back then front
    for k, col in ((-1, (34, 30, 40, 255)), (1, BLACK)):
        a = math.radians(22 * s * k)
        knee = (hip[0] + 34 * math.sin(a), hip[1] + 34 * math.cos(a))
        foot = (knee[0] + 36 * math.sin(a * 0.4), knee[1] + 36 * math.cos(a * 0.4))
        w = 7
        shape(d, [(hip[0] - w, hip[1]), (hip[0] + w, hip[1]), (knee[0] + w, knee[1]), (foot[0] + 6, foot[1]), (foot[0] - 6, foot[1]), (knee[0] - w, knee[1])], col)
        blob(d, foot[0] + 7, foot[1] + 2, 12, 6, (20, 18, 24, 255))
    # back arm with towel
    shape(d, [(50, 74), (60, 74), (56, 104), (46, 104)], WHITE)
    shape(d, [(42, 98), (58, 98), (60, 124), (40, 124)], (250, 250, 250, 255), ow=2 * K)
    # body: shirt, waistcoat, apron
    shape(d, [(46, 70), (82, 70), (86, 116), (42, 116)], WHITE)
    shape(d, [(46, 72), (60, 72), (64, 112), (44, 112)], BLACK)
    shape(d, [(68, 72), (82, 72), (85, 112), (64, 112)], BLACK)
    for y in (88, 97, 106): d.ellipse(P([(62.5, y - 1.5), (65.5, y + 1.5)]), fill=(210, 180, 90, 255))
    shape(d, [(40, 110), (88, 110), (92, 160), (36, 160)], WHITE)                       # long apron
    line(d, [(40, 112), (88, 112)], (200, 200, 200, 255), 1.5)
    # bow tie
    shape(d, [(58, 66), (64, 70), (58, 74)], (150, 20, 40, 255), ow=K); shape(d, [(70, 66), (64, 70), (70, 74)], (150, 20, 40, 255), ow=K)
    # head
    hy = 40 + abs(s) * -2
    blob(d, 66, hy, 22, 26, SKIN)
    blob(d, 44, hy + 2, 5, 7, SKIN)                                                     # ear
    shape(d, [(44, hy - 6), (48, hy - 22), (62, hy - 30), (82, hy - 26), (90, hy - 12), (88, hy - 10), (74, hy - 18), (58, hy - 16), (50, hy - 4)], HAIR)   # slicked hair
    line(d, [(70, hy - 3), (75, hy - 6), (80, hy - 3)], INK, 1.8)                       # happy closed eye
    blob(d, 84, hy + 6, 4, 4, (232, 160, 130, 255), ow=K)                               # nose
    line(d, [(72, hy + 13), (78, hy + 10), (84, hy + 12), (90, hy + 9), (92, hy + 6)], HAIR, 3)   # moustache
    line(d, [(74, hy + 18), (80, hy + 19), (85, hy + 17)], INK, 1.4)                    # smile
    d.ellipse(P([(72, hy + 5), (78, hy + 9)]), fill=(240, 140, 140, 140))               # cheek
    # front arm holding the tray up and forward, with a glass of red wine
    bob = 2 * s
    shape(d, [(76, 74), (86, 72), (104, 82 + bob), (100, 90 + bob), (82, 86)], WHITE)
    shape(d, [(98, 78 + bob), (110, 74 + bob), (113, 82 + bob), (102, 90 + bob)], WHITE)
    blob(d, 112, 76 + bob, 5, 5, SKIN, ow=2 * K)
    shape(d, [(94, 70 + bob), (134, 70 + bob), (134, 74 + bob), (94, 74 + bob)], (200, 200, 210, 255), ow=2 * K)  # tray
    gx, gy = 114, 70 + bob
    shape(d, [(gx - 4, gy), (gx + 4, gy), (gx + 1, gy - 2), (gx + 1, gy - 12), (gx - 1, gy - 12), (gx - 1, gy - 2)], (230, 236, 245, 255), ow=K)
    shape(d, [(gx - 8, gy - 26), (gx + 8, gy - 26), (gx + 6, gy - 15), (gx, gy - 11), (gx - 6, gy - 15)], (230, 236, 245, 230), ow=int(1.5 * K))
    shape(d, [(gx - 7, gy - 21), (gx + 7, gy - 21), (gx + 5.5, gy - 15.5), (gx, gy - 12.5), (gx - 5.5, gy - 15.5)], (150, 18, 48, 255), ow=K)
    return down(im)

# ---------------- finish banner (placeholder goal) ----------------
def finish(wave):
    im = canvas(200, 260); d = ImageDraw.Draw(im)
    for x in (20, 172):
        shape(d, [(x, 30), (x + 8, 30), (x + 8, 258), (x, 258)], (210, 214, 224, 255))
    pts_top = [(28 + i * 12, 36 + 4 * math.sin(i * 0.8 + wave)) for i in range(13)]
    pts_bot = [(28 + i * 12, 96 + 4 * math.sin(i * 0.8 + wave + 0.5)) for i in range(13)]
    shape(d, pts_top + pts_bot[::-1], (78, 48, 140, 255))
    try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 28 * K)
    except Exception: f = ImageFont.load_default()
    d.text((100 * K, 66 * K + 4 * math.sin(wave + 1.4) * K), 'FINISH', font=f, fill=(255, 168, 40, 255), anchor='mm', stroke_width=K, stroke_fill=INK)
    for i in range(12):     # bunting
        x = 30 + i * 12.5; y = 104 + 3 * math.sin(i * 0.9 + wave)
        shape(d, [(x, y), (x + 10, y), (x + 5, y + 12)], [(255, 168, 40, 255), (230, 60, 140, 255), (60, 170, 230, 255)][i % 3], ow=K)
    return down(im)

if __name__ == '__main__':
    croissant(-6).save(f'{OUT}/croissant1.png'); croissant(6).save(f'{OUT}/croissant2.png')
    for i, f in enumerate(shoe_frames()): f.save(f'{OUT}/asics{i + 1}.png')
    for i in range(8): bottle(i * 45).save(f'{OUT}/bottle{i + 1}.png')
    for i, w in enumerate([1.0, 0.2, -0.6, 0.2]): laptop(w).save(f'{OUT}/laptop{i + 1}.png')
    for i in range(4): waiter(i * math.pi / 2).save(f'{OUT}/waiter{i + 1}.png')
    for i in range(3): finish(i * 2.1).save(f'{OUT}/finish{i + 1}.png')
