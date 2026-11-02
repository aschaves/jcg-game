"""Paper-cut-out rig for Juliana: photo parts from the runner photo + photo heads, posed per frame."""
import math, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = Image.open('cut/4_isnet-general-use.png').convert('RGBA')
BS = 0.29            # body scale (photo px -> work px)
SLIM = 0.86          # horizontal slimming of torso / arms
HS = 0.54            # head scale (canonical head px -> work px)
WW, WH = 450, 570    # work canvas; final = work / 3
GROUND = 566

def poly_cut(img, poly, box):
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).polygon(poly, fill=255)
    a = np.minimum(np.asarray(img)[..., 3], np.asarray(m))
    out = img.copy(); out.putalpha(Image.fromarray(a)); return out.crop(box)

def lum(a): return 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]

def scaled(part, sx, sy):
    return part.resize((max(1, round(part.width * sx)), max(1, round(part.height * sy))), Image.LANCZOS)

# ---- parts (orig photo coordinates) ----
# torso: jacket + headphones, arms cut away
TB = (640, 280, 1010, 1025)
torso = poly_cut(SRC, [(700, 280), (960, 280), (968, 370), (1004, 412), (1004, 1025), (652, 1025), (665, 760), (686, 470), (700, 380)], TB)
t = np.asarray(torso).copy(); yy = np.arange(t.shape[0])[:, None] + TB[1]
skin = (t[..., 0].astype(int) > t[..., 1].astype(int) + 22) & (t[..., 0] > 110) & (yy < 372)
t[..., 3][skin] = 0
torso = Image.fromarray(t)
torso = scaled(torso, BS * SLIM, BS)
# hanging arm, split at the elbow
def arm_part(y0, y1):
    p = poly_cut(SRC, [(556, 430), (692, 445), (700, 520), (692, 940), (660, 1036), (522, 1036), (522, 920), (540, 600)], (515, y0, 705, y1))
    a = np.asarray(p).copy()
    if y1 > 980:   # paint the leash handle in the glove with glove grey
        L = lum(a.astype(float)); rows = np.arange(a.shape[0])[:, None] + y0
        glove = (rows > 945) & (L > 120) & (a[..., 3] > 200)
        g = a[..., :3][glove].mean(0)
        dark = (rows > 975) & (L < 95) & (a[..., 3] > 0)
        a[..., :3][dark] = g.astype('uint8')
    return scaled(Image.fromarray(a), BS * SLIM, BS)
upper = arm_part(430, 742)     # shoulder pivot at (628, 475), elbow at (605, 728)
fore = arm_part(712, 1036)     # elbow pivot at (605, 728)
UPPER_PIV = ((628 - 515) * BS * SLIM, (475 - 430) * BS); UPPER_LEN = (728 - 475) * BS
FORE_PIV = ((605 - 515) * BS * SLIM, (728 - 712) * BS)
# hand-on-hip arm (idle only), pivot at the shoulder
akimbo = poly_cut(SRC, [(1004, 405), (1090, 425), (1225, 520), (1225, 610), (1110, 700), (1080, 805), (985, 805), (985, 690), (1004, 560)], (980, 400, 1230, 810))
akimbo = scaled(akimbo, BS * SLIM, BS); AKIMBO_PIV = ((1004 - 980) * BS * SLIM, (440 - 400) * BS)
# shoe: left shoe is a side profile standing on its toe; rotate so the toe points right
shoe = SRC.crop((616, 1436, 770, 1726)); s = np.asarray(shoe).copy()
s[..., 3][lum(s.astype(float)) < 105] = 0
shoe = Image.fromarray(s).rotate(90, expand=True)
shoe = scaled(shoe, BS * 0.95, BS * 0.95)
SHOE_ANK = (shoe.width * 0.30, shoe.height * 0.22)      # where the ankle enters the shoe
LEG = np.asarray(SRC)[1100:1250, 820:900][..., :3].reshape(-1, 3).mean(0)   # leggings colour

def head(name):
    h = Image.open(f'head_{name}.png'); return scaled(h, HS, HS)

def put(canvas, part, piv, pos, ang=0.0, sx=1.0, sy=1.0, dark=1.0):
    """Draw part so its pivot lands on pos, rotated by ang degrees (positive = clockwise on screen, i.e. a
    downward limb swings its end toward -x... we use: positive moves the far end toward +x for a downward limb)."""
    a = math.radians(-ang)
    ca, sa = math.cos(a), math.sin(a)
    # forward: q = pos + R(a) * S * (p - piv); inverse: p = piv + S^-1 R(-a) (q - pos)
    A = ca / sx; B = sa / sx; D = -sa / sy; E = ca / sy
    C = piv[0] - A * pos[0] - B * pos[1]; F = piv[1] - D * pos[0] - E * pos[1]
    layer = part.transform(canvas.size, Image.AFFINE, (A, B, C, D, E, F), resample=Image.BICUBIC)
    if dark != 1.0:
        arr = np.asarray(layer).astype(float); arr[..., :3] *= dark; layer = Image.fromarray(arr.astype('uint8'))
    canvas.alpha_composite(layer)

def limb_pts(base, ang, length):
    a = math.radians(ang); return (base[0] + length * math.sin(a), base[1] + length * math.cos(a))

def capsule(d, p0, p1, w0, w1, col):
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); nx, ny = -math.sin(ang), math.cos(ang)
    d.polygon([(p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2), (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2),
               (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2), (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2)], fill=col)
    for p, w in ((p0, w0), (p1, w1)): d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=col)

THIGH, SHIN = 54, 52
def leg(canvas, hip, thigh_ang, bend, dark=1.0, foot_ang=None):
    knee = limb_pts(hip, thigh_ang, THIGH); shin_ang = thigh_ang - bend; ank = limb_pts(knee, shin_ang, SHIN)
    # shoe first so the legging covers the collar
    fa = foot_ang if foot_ang is not None else shin_ang * 0.7
    put(canvas, shoe, SHOE_ANK, ank, -fa, dark=dark)
    lay = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    base = tuple(int(c * dark) for c in LEG) + (255,)
    hi = tuple(int(min(255, c * dark * 1.35 + 10)) for c in LEG) + (255,)
    capsule(d, hip, knee, 40, 28, base); capsule(d, knee, ank, 28, 18, base)
    # soft highlight on the front of the leg for some volume
    off = lambda p, k: (p[0] + k, p[1])
    capsule(d, off(hip, 8), off(knee, 6), 8, 6, hi); capsule(d, off(knee, 6), off(ank, 3), 6, 4, hi)
    lay = lay.filter(ImageFilter.GaussianBlur(0.6))
    canvas.alpha_composite(lay)
    return ank

def arm(canvas, shoulder, up_ang, elbow_bend, mirror=False, dark=1.0):
    up = upper.transpose(Image.FLIP_LEFT_RIGHT) if mirror else upper
    fo = fore.transpose(Image.FLIP_LEFT_RIGHT) if mirror else fore
    upiv = (up.width - UPPER_PIV[0], UPPER_PIV[1]) if mirror else UPPER_PIV
    fpiv = (fo.width - FORE_PIV[0], FORE_PIV[1]) if mirror else FORE_PIV
    elbow = limb_pts(shoulder, up_ang, UPPER_LEN)
    put(canvas, fo, fpiv, elbow, up_ang + elbow_bend, dark=dark)
    put(canvas, up, upiv, shoulder, up_ang, dark=dark)

def frame(pose):
    c = Image.new('RGBA', (WW, WH), (0, 0, 0, 0))
    bob = pose.get('bob', 0)
    hem_y = GROUND - pose.get('leg_h', THIGH + SHIN + shoe.height * 0.55) + bob
    cx = WW / 2 + pose.get('dx', 0)
    tx = cx - torso.width / 2; ty = hem_y - torso.height
    hipL, hipR = (cx - 20, hem_y - 10), (cx + 20, hem_y - 10)
    shL = (tx + (686 - 640) * BS * SLIM - 4, ty + (480 - 280) * BS)
    shR = (tx + torso.width - (1010 - 1004) * BS * SLIM - 8, ty + (470 - 280) * BS)
    # back limbs (darker), head, torso, front limbs
    arm(c, shR, *pose['armR'], mirror=True, dark=0.82) if pose.get('armR') else None
    leg(c, hipR, *pose['legR'], dark=0.78)
    h = head(pose['face']); hcx, hcy = cx + pose.get('hdx', 0), ty + 22 + bob * 0.3
    put(c, h, (200 * HS, 430 * HS), (hcx, hcy), pose.get('tilt', 0))
    leg(c, hipL, *pose['legL'])
    put(c, torso, (torso.width / 2, torso.height), (cx, hem_y), pose.get('lean', 0))
    if pose.get('akimbo'): put(c, akimbo, AKIMBO_PIV, shR, 0)
    arm(c, shL, *pose['armL'])
    return c

def poses():
    P = {}
    for i in range(6):
        ph = 2 * math.pi * i / 6; s, co = math.sin(ph), math.cos(ph)
        bendL = 18 + 70 * max(0, co); bendR = 18 + 70 * max(0, -co)
        P[f'run{i+1}'] = dict(face='smile', legL=(34 * s + 6, bendL), legR=(-34 * s + 6, bendR),
                               armL=(38 * s, 75), armR=(-38 * s, 75), bob=-7 * abs(s), lean=4, tilt=2 * s, dx=-6)
    P['idle1'] = dict(face='smile', legL=(-3, 0), legR=(4, 0), armL=(4, -8), akimbo=True)
    P['idle2'] = dict(face='smile', legL=(-3, 0), legR=(4, 0), armL=(6, -12), akimbo=True, bob=1.5, tilt=-2)
    P['idle3'] = dict(face='smirk', legL=(-3, 0), legR=(4, 0), armL=(4, -8), akimbo=True, tilt=3)
    P['jump1'] = dict(face='laugh', legL=(55, 85), legR=(-22, 25), armL=(-150, -15), armR=(150, 15), bob=-4)
    P['hurt1'] = dict(face='tongue', legL=(18, 5), legR=(-18, 5), armL=(-58, -30), armR=(58, 30))
    return P

if __name__ == '__main__':
    os.makedirs('juliana', exist_ok=True)
    for name, pose in poses().items():
        f = frame(pose)
        f = f.resize((WW // 3, WH // 3), Image.LANCZOS)
        f.save(f'juliana/{name}.png')
    print('leg colour', LEG.round(), 'shoe', shoe.size, 'torso', torso.size, 'head', head('smile').size)
