"""Hair pulled back + grey knit headband on every face, and the ponytail cut from photo 6."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
W, H = 400, 480
rng = np.random.default_rng(7)
src6 = np.asarray(Image.open('6_src.png').convert('RGB')).astype(float)

# --- hair colour from photo 6 (top of the head, pulled-back hair) ---
patch = src6[420:560, 260:420].reshape(-1, 3); L = patch @ [.3, .59, .11]
HAIR = np.percentile(patch[(L > 35) & (L < 120)], 55, axis=0); HAIR = HAIR * [1.18, 1.0, 0.82]; HAIR_HI = np.percentile(patch[L > 100], 50, axis=0)
KNIT = np.array([173., 181., 183.])
yy, xx = np.mgrid[0:H, 0:W].astype(float)
CX = 200

def blur(a, r): return np.asarray(Image.fromarray(a.astype('uint8')).filter(ImageFilter.GaussianBlur(r))).astype(float)

# --- head silhouette hair (behind the face): crown + back of head down to the nape on the left ---
back = (((xx - CX) / 124) ** 2 + ((yy - 250) / 148) ** 2 <= 1) & (yy < 330)
back |= (((xx - 118) / 52) ** 2 + ((yy - 330) / 70) ** 2 <= 1)            # gathered hair toward the nape (left = back)
# --- strands: curves sweeping from the hairline back toward the nape (ponytail side) ---
strands = np.zeros((H, W)); img = Image.fromarray(np.zeros((H, W), 'uint8')); d = ImageDraw.Draw(img)
for i in range(260):
    x0 = rng.uniform(70, 330); y0 = rng.uniform(95, 200)
    pts = []
    for t in np.linspace(0, 1, 12):
        pts.append((x0 + (110 - x0) * t ** 1.3 + rng.normal(0, 1.5), y0 + (360 - y0) * t ** 1.8))
    d.line(pts, fill=int(rng.uniform(40, 255)), width=1)
strands = blur(np.asarray(img), 0.5) / 255
grey = np.zeros((H, W)); gi = Image.fromarray(np.zeros((H, W), 'uint8')); gd = ImageDraw.Draw(gi)
for i in range(40):     # a few grey/silver strands like in her hair
    x0 = rng.uniform(80, 320); y0 = rng.uniform(100, 190)
    gd.line([(x0 + (110 - x0) * t ** 1.3, y0 + (360 - y0) * t ** 1.8) for t in np.linspace(0, 1, 12)], fill=255, width=1)
grey = blur(np.asarray(gi), 0.4) / 255
shade = 1.15 - 0.35 * np.clip(np.hypot((xx - 230) / 140, (yy - 120) / 200), 0, 1.3)
hair_rgb = (HAIR * (0.8 + 0.35 * strands[..., None]) * shade[..., None]) * (1 - 0.3 * grey[..., None]) + HAIR_HI * 0.3 * grey[..., None]
hair_rgb = np.clip(hair_rgb, 0, 255)

def layer(rgb, mask, r=1.0):
    m = Image.fromarray((mask * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(r))
    im = Image.fromarray(rgb.astype('uint8'), 'RGB').convert('RGBA'); im.putalpha(m); return im

# --- headband: arc across the hairline, wrapping over the ears ---
BAND_C, BAND_S, THICK = 186, 238, 30          # bottom edge at centre / at the sides; thickness
k = (BAND_S - BAND_C) / 118 ** 2
bottom = BAND_C + k * (xx - CX) ** 2
inside_head = ((xx - CX) / 127) ** 2 + ((yy - 250) / 150) ** 2 <= 1
band = (yy <= bottom) & (yy >= bottom - THICK) & inside_head
ribs = np.sin(np.arctan2(xx - CX, 520 - yy) * 140) * 9
noise = rng.normal(0, 9, (H, W))
bshade = (1.08 - 0.25 * np.abs(xx - CX) / 127) * np.where(bottom - yy < 6, 0.85, 1) * np.where(bottom - yy > THICK - 6, 0.9, 1)
band_rgb = np.clip((KNIT + (ribs + noise)[..., None]) * bshade[..., None], 0, 255)
# hair on top of the face only above the band (keeps each photo's own forehead below it)
top_hair = back & (yy < bottom - THICK + 4)

for name in ['smile', 'laugh', 'smirk', 'tongue']:
    f = Image.open(f'head_{name}_face.png')
    h = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    h.alpha_composite(layer(hair_rgb, back.astype(float), 1.2))
    h.alpha_composite(f)
    h.alpha_composite(layer(hair_rgb, top_hair.astype(float), 1.5))
    h.alpha_composite(layer(band_rgb, band.astype(float), 0.9))
    h.save(f'head_{name}.png')

# --- ponytail from photo 6: hair tie at ~(232, 925), tail down to ~1170, lanyard avoided on the right ---
src = Image.open('6_src.png').convert('RGBA')
poly = [(214, 912), (250, 912), (262, 950), (290, 995), (262, 1040), (258, 1100), (250, 1150), (225, 1172),
        (170, 1175), (125, 1165), (138, 1100), (160, 1050), (190, 1000), (205, 950)]
m = Image.new('L', src.size, 0); ImageDraw.Draw(m).polygon(poly, fill=255); m = m.filter(ImageFilter.GaussianBlur(3))
a = np.asarray(src).astype(float); rgb = a[..., :3]
mx, mn = rgb.max(-1), rgb.min(-1); sat = (mx - mn) / np.maximum(mx, 1); lum = rgb @ [.3, .59, .11]
keep = np.clip((0.42 - sat) / 0.12, 0, 1) * np.clip((205 - lum) / 30, 0, 1)      # drop the coloured / bright background
alpha = np.asarray(m).astype(float)
inner = rgb[(np.asarray(m) > 250) & (keep > 0.9)]; hm = inner.mean(0)
rgb = rgb * keep[..., None] + (hm * (0.85 + 0.3 * rng.random((rgb.shape[0], rgb.shape[1], 1)))) * (1 - keep[..., None])
p = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha]).astype('uint8'), 'RGBA').crop((110, 900, 300, 1180))
p.save('ponytail.png')
print('hair', HAIR.round(), 'ponytail', p.size)
