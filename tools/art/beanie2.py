import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
W, H = 400, 480
raw = np.asarray(Image.open('head_beanie_raw.png')).astype(float)
# knit sample: solid region of the crown in the aligned runner image
patch = raw[165:200, 110:175]
ok = patch[..., 3] > 200
base = patch[..., :3][ok].mean(0)
tex = patch[..., :3] - patch[..., :3][ok].mean(0)          # zero-mean knit detail
tex[~ok] = 0
# mirror-tile the detail to the whole canvas
t = np.concatenate([tex, tex[:, ::-1]], 1); t = np.concatenate([t, t[::-1]], 0)
reps = (H // t.shape[0] + 1, W // t.shape[1] + 1, 1)
tile = np.tile(t, reps)[:H, :W]

CX, BRIM, SIDE, TOP, RX = 200, int(os.environ.get('BRIM', 196)), 258, 92, 132
yy, xx = np.mgrid[0:H, 0:W].astype(float)
dome = ((xx - CX) / RX) ** 2 + ((yy - (TOP + 118)) / 118) ** 2 <= 1
k = (SIDE - BRIM) / (RX * 0.92) ** 2
brim = yy <= BRIM + k * (xx - CX) ** 2
mask = (dome & brim).astype(float)
# shading: lighter top-left, darker toward the rim, darker band along the brim (fold)
r = np.sqrt(((xx - CX + 30) / RX) ** 2 + ((yy - TOP - 60) / 130) ** 2)
shade = 1.12 - 0.28 * np.clip(r, 0, 1.2)
dist_brim = (BRIM + k * (xx - CX) ** 2) - yy
shade *= np.where(dist_brim < 14, 0.86 + 0.01 * dist_brim, 1)
rng = np.random.default_rng(3)
noise = np.asarray(Image.fromarray((rng.normal(128, 40, (H, W))).clip(0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))).astype(float) - 128
ang = np.arctan2(xx - CX, (TOP + 260) - yy)          # ribs fan out from below, following the dome
ribs = np.sin(ang * 70) * 7
tile = (noise * 0.5 + ribs)[..., None]
rgb = np.clip((base + tile) * shade[..., None], 0, 255)
m = Image.fromarray((mask * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))
b = Image.fromarray(rgb.astype('uint8'), 'RGB').convert('RGBA'); b.putalpha(m)
b.save('beanie.png')
print('base colour', base.round())
for name in ['smile', 'laugh', 'smirk', 'tongue']:
    f = Image.open(f'head_{name}_face.png')
    h = Image.new('RGBA', (W, H), (0, 0, 0, 0)); h.alpha_composite(f); h.alpha_composite(b)
    h.save(f'head_{name}.png')
