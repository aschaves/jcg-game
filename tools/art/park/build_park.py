import numpy as np, os
from PIL import Image, ImageDraw, ImageFilter
OUT = 'out'; os.makedirs(OUT, exist_ok=True)

def paint_over(img, box, dx):
    """Replace box with the pixels dx to the left (hides the 'tiling' arrows)."""
    x0, y0, x1, y1 = box
    img.paste(img.crop((x0 - dx, y0, x1 - dx, y1)), (x0, y0))

sky = Image.open('sky_raw.png').convert('RGBA'); paint_over(sky, (1715, 222, 1798, 267), 110)
city = Image.open('city_raw.png'); paint_over(city, (1715, 236, 1798, 278), 110)
path = Image.open('path_b_raw.png')

def scale_h(im, h): return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
sky = scale_h(sky, 420); city = scale_h(city, 403)
# walkway layer: make it repeat seamlessly by cross-fading the last OV columns into the first ones
OV = 90
p = np.asarray(path).astype(float); w = p.shape[1]
head, tail = p[:, :OV], p[:, w - OV:]
t = np.linspace(0, 1, OV)[None, :, None]
p2 = p[:, :w - OV].copy(); p2[:, :OV] = tail * (1 - t) + head * t
path = Image.fromarray(p2.clip(0, 255).astype('uint8'), 'RGBA')
sky.convert('RGB').save(f'{OUT}/sky.png'); city.save(f'{OUT}/city.png'); path.save(f'{OUT}/path.png')
print('sky', sky.size, 'city', city.size, 'path', path.size, 'sky top colour', np.asarray(sky)[3, sky.width // 2][:3])

# ---------------- tiles ----------------
T = {k: Image.open(f'srctile_{k}.png').convert('RGBA') for k in 'ABCDEFGHI'}
def fix(img, box, dx):
    img = img.copy(); paint_over(img, box, dx); return img
Bclean = fix(fix(T['B'], (8, 120, 95, 300), -110), (500, 170, 560, 300), 90)
Eclean = fix(fix(T['E'], (0, 110, 120, 300), -200), (460, 110, 585, 300), 220)
# D: its kerb is 115px higher than E's/F's; warp it vertically so the kerb lines meet
d = np.asarray(T['D']); H = d.shape[0]
ksrc, kdst = 157, 272
ys = np.arange(H, dtype=float)
src_y = np.where(ys < kdst, ys * ksrc / kdst, ksrc + (ys - kdst) * (H - ksrc) / (H - kdst)).round().astype(int).clip(0, H - 1)
Dfix = Image.fromarray(d[src_y])

def t64(im): return im.resize((64, 64), Image.LANCZOS)
def edge(im, side):
    """Soil column edge for the side of a pit: dark wavy outline, transparent beyond."""
    a = np.asarray(im.resize((64, 64), Image.LANCZOS)).copy()
    rng = np.random.default_rng(3 if side == 'L' else 5)
    off = (2 + 1.5 * np.sin(np.arange(64) / 5) + rng.normal(0, 0.4, 64)).round().astype(int)
    for y in range(64):
        e = off[y]
        if side == 'L': a[y, :e, 3] = 0; a[y, e:e + 3, :3] = (52, 32, 20)
        else: a[y, 64 - e:, 3] = 0; a[y, 64 - e - 3:64 - e, :3] = (52, 32, 20)
    return Image.fromarray(a)
def bottom_line(im):
    a = np.asarray(t64(im)).copy(); a[61:, :, :3] = (48, 44, 52); return Image.fromarray(a)

tiles = {
    'A': t64(T['A']), 'B': t64(Bclean), 'C': t64(T['C']), 'Q': t64(T['B']),    # ground top (Q = with cone)
    'D': t64(Dfix), 'E': t64(Eclean), 'F': t64(T['F']), 'R': t64(T['E']),       # second row (R = bike racks)
    'G': edge(T['H'], 'L'), 'H': t64(T['H']), 'I': edge(T['H'], 'R'),           # soil below
    'J': bottom_line(T['A']), 'K': bottom_line(Bclean), 'L': bottom_line(T['C']),  # floating platform
}
for k, im in tiles.items(): im.save(f'{OUT}/tile_{k}.png')
