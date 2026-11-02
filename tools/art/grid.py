import sys
from PIL import Image, ImageDraw
src, out, x0, y0, x1, y1, step = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:8])
im = Image.open(src).convert('RGBA')
bg = Image.new('RGBA', im.size, (127,209,127,255)); bg.alpha_composite(im)
d = ImageDraw.Draw(bg)
for x in range(0, im.size[0], step): d.line([(x,0),(x,im.size[1])], fill=(255,0,0,255)); [d.text((x+3,y+3), str(x), fill=(255,255,0,255)) for y in range(y0, y1, step*2)]
for y in range(0, im.size[1], step): d.line([(0,y),(im.size[0],y)], fill=(0,0,255,255)); [d.text((x+3,y+3), str(y), fill=(0,255,255,255)) for x in range(x0, x1, step*2)]
c = bg.crop((x0,y0,x1,y1)); c.thumbnail((900,900)); c.convert('RGB').save(out, quality=85)
