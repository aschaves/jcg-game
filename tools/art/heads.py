import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
C = 'cut/'
W, H = 400, 480                     # canonical head canvas
EL, ER = (150, 250), (250, 250)     # canonical eye centres (D = 100)

def align(img, el, er, scale_mult=1.0, out=(W, H)):
    """Similarity transform putting photo eyes el/er onto canonical eyes."""
    (x1, y1), (x2, y2) = el, er
    d = math.hypot(x2 - x1, y2 - y1); ang = math.atan2(y2 - y1, x2 - x1)
    s = 100 / d * scale_mult
    # canonical -> source (inverse map for PIL affine)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    ca, sa = math.cos(ang) / s, math.sin(ang) / s
    # source = R(ang)/s * (p - c_can) + c_src
    ccx, ccy = (EL[0] + ER[0]) / 2, (EL[1] + ER[1]) / 2
    a, b = ca, -sa; d_, e = sa, ca
    c = cx - a * ccx - b * ccy; f = cy - d_ * ccx - e * ccy
    return img.transform(out, Image.AFFINE, (a, b, c, d_, e, f), resample=Image.BICUBIC)

FACES = {  # name: (file, left eye, right eye)
    'smile':  ('5', (500, 882), (878, 900)),
    'laugh':  ('3', (403, 563), (577, 535)),
    'tongue': ('1', (381, 568), (630, 568)),
    'smirk':  ('2', (390, 419), (592, 419)),
}

def face_mask():
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).ellipse((200 - 118, 290 - 160, 200 + 118, 290 + 165), fill=255)
    return m.filter(ImageFilter.GaussianBlur(3))

def skin_stats(a, alpha):
    # central face patch (cheeks/forehead) in canonical coords
    patch = a[255:340, 140:260][alpha[255:340, 140:260] > 200]
    return patch.mean(0), patch.std(0)

ref = None
out = {}
for name, (f, el, er) in FACES.items():
    im = Image.open(f'{C}{f}_isnet-general-use.png').convert('RGBA')
    al = align(im, el, er)
    arr = np.asarray(al).astype(float)
    rgb, alpha = arr[..., :3], arr[..., 3]
    m, s = skin_stats(rgb, alpha)
    if ref is None and name == 'smile':
        pass
    out[name] = (al, m, s)
# colour target: average of the warm, natural-light faces (laugh, smirk)
tm = (out['laugh'][1] + out['smirk'][1]) / 2; ts = (out['laugh'][2] + out['smirk'][2]) / 2
fm = face_mask()
for name, (al, m, s) in out.items():
    arr = np.asarray(al).astype(float)
    rgb = (arr[..., :3] - m) / s * ts + tm
    k = 0.85 if name == 'smile' else 0.5          # how strongly to correct (photo 5 has a purple cast)
    rgb = arr[..., :3] * (1 - k) + rgb * k
    a = np.minimum(arr[..., 3], np.asarray(fm).astype(float))
    res = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a]).astype('uint8'), 'RGBA')
    res.save(f'head_{name}_face.png')

# Beanie from the runner photo: low-saturation light pixels above the sunglasses.
im4 = Image.open(f'{C}4_isnet-general-use.png').convert('RGBA')
# runner eyes behind sunglasses (lens centres); head is slightly turned so scale by face width instead
b = align(im4, (815, 200), (900, 205), scale_mult=float(__import__('os').environ.get('BS', '0.82')))
arr = np.asarray(b).astype(float)
r, g, bl, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
mx, mn = np.maximum(np.maximum(r, g), bl), np.minimum(np.minimum(r, g), bl)
sat = (mx - mn) / np.maximum(mx, 1)
yy, xx = np.mgrid[0:H, 0:W]
beanie = (sat < 0.22) & (mx > 95) & (a > 128) & (yy < 300)
bm = Image.fromarray((beanie * 255).astype('uint8')).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
bimg = b.copy(); bimg.putalpha(bm)
bimg.save('head_beanie_raw.png')
