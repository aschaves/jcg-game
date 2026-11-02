import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
I = sys.argv[1]
src = Image.open(I + '/parallax_sheet.jpg').convert('RGB')
STRIPS = {'sky': (101, 75, 1899, 342), 'city': (101, 425, 1899, 703), 'path_a': (101, 783, 1899, 1071), 'path_b': (101, 1157, 1899, 1451)}

def dechecker(img, small_ymax=10**6):
    a = np.asarray(img).astype(int)
    mx, mn = a.max(-1), a.min(-1); lum = a.mean(-1)
    cand = ((mx - mn) < 14) & (lum > 168)
    lab, n = ndimage.label(cand)
    white = ndimage.sum((lum > 243) & cand, lab, range(1, n + 1))
    grey = ndimage.sum((lum > 172) & (lum < 198) & cand, lab, range(1, n + 1))
    size = ndimage.sum(cand, lab, range(1, n + 1))
    kill_ids = np.where(((white > 0.15 * size) & (grey > 0.15 * size) & (size > 60)) | ((size > 30) & (white + grey > 0.8 * size) & (size < 2000) & False))[0] + 1
    kill = np.isin(lab, kill_ids)
    # also small isolated checker cells (single white or grey square fully enclosed, e.g. between railing bars)
    small_ids = np.where((size > 20) & (size < 900) & ((white > 0.85 * size) | (grey > 0.85 * size)))[0] + 1
    small = np.isin(lab, small_ids); small[small_ymax:] = False
    kill |= small
    kill = ndimage.binary_dilation(kill, iterations=1) & (cand | ((mx - mn) < 22) & (lum > 150))
    alpha = np.where(kill, 0, 255).astype('uint8')
    alpha = np.asarray(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.6)))
    return Image.fromarray(np.dstack([a.astype('uint8'), alpha]), 'RGBA')

for k, box in STRIPS.items():
    im = src.crop(box)
    out = im.convert('RGBA') if k == 'sky' else dechecker(im, 150 if k == 'city' else 10**6)
    out.save(f'{k}_raw.png')

tiles = Image.open(I + '/tiles_sheet.jpg').convert('RGB')
XS = [(50, 644), (704, 1297), (1357, 1950)]; YS = [(58, 650), (722, 1301), (1365, 1946)]
names = 'ABCDEFGHI'; i = 0
for (y0, y1) in YS:
    for (x0, x1) in XS:
        tiles.crop((x0 + 4, y0 + 4, x1 - 4, y1 - 4)).save(f'srctile_{names[i]}.png'); i += 1
print('ok')
