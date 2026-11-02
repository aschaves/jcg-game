"""Generates the parkrun map (game/js/data/maps.js entry `park`). Run: python3 tools/levels/park.py
Rows 0-11 (12 rows, 64px). Ground: row 9 top (A B C, Q = cone), row 10 (D E F, R = bike racks), row 11 soil (G H I).
Floating platforms: J K L. Juliana is ~2.6 tiles tall and jumps ~3.5 tiles, so a platform 3 rows above the
surface she stands on is a step up (and blocks walking underneath).
Entities: o croissant, ! ASICS, 1 waiter, 2 wine bottle, 3 laptop, - finish."""
COLS, ROWS = 152, 12
g = [[' '] * COLS for _ in range(ROWS)]
def put(r, c, ch): g[r][c] = ch

ground = [(0, 29), (33, 52), (56, 75), (79, 100), (104, 124), (128, 151)]
for a, b in ground:
    for c in range(a, b + 1):
        left, right = c == a and a > 0, c == b and b < COLS - 1
        put(9, c, 'A' if left else 'C' if right else ('Q' if c % 11 == 5 else 'B'))
        put(10, c, 'D' if left else 'F' if right else ('R' if c % 13 in (6, 7) else 'E'))
        put(11, c, 'G' if left else 'I' if right else 'H')

platforms = [(6, 13, 16), (6, 39, 41), (3, 44, 47), (6, 62, 64), (3, 67, 70), (6, 87, 89), (3, 92, 95),
             (6, 110, 112), (3, 115, 118), (6, 133, 135)]
# A jump off the end E of a high (row 3) platform lands about 11-12 columns later; each one ends 13 columns
# before the far side of the next pit, so jumping off clears the pit and simply running off lands before it.
for r, a, b in platforms:
    for c in range(a, b + 1): put(r, c, 'J' if c == a else 'L' if c == b else 'K')

items = (
    # warm-up straight
    [(8, c, 'o') for c in (7, 9, 11)] + [(5, c, 'o') for c in (14, 15)] +
    # first waiter, then the first pit with an arc of croissants
    [(8, 24, '1')] + [(6, 30, 'o'), (5, 31, 'o'), (6, 32, 'o')] +
    # steps up to a high platform with an ASICS; a wine bottle on the straight
    [(5, 40, 'o'), (2, 45, 'o'), (2, 46, '!'), (8, 50, '2')] +
    [(6, 53, 'o'), (5, 54, 'o'), (6, 55, 'o')] +
    # laptop alley
    [(8, 58, '1'), (5, 63, 'o'), (5, 66, '3'), (2, 68, 'o'), (2, 69, 'o'), (8, 74, '2'), (6, 77, 'o')] +
    [(8, 82, '3'), (5, 88, 'o'), (2, 93, '!'), (2, 94, 'o'), (8, 98, '1')] +
    [(6, 101, 'o'), (5, 102, 'o'), (5, 106, '2'), (5, 111, 'o'), (2, 116, 'o'), (2, 117, 'o'), (8, 121, '3')] +
    [(6, 125, 'o'), (5, 126, 'o'), (6, 127, 'o')] +
    # home straight: a last waiter, a last ASICS, then the finish
    [(8, 131, '1'), (5, 134, '!'), (8, 138, 'o'), (8, 140, 'o'), (8, 146, '-')]
)
for r, c, ch in items: put(r, c, ch)

rows = [''.join(r) for r in g]
js = '  park: [\n' + ''.join(f'    "{r}",\n' for r in rows) + '  ],\n'
import pathlib, re
p = pathlib.Path(__file__).resolve().parents[2] / 'game/js/data/maps.js'
src = p.read_text()
if '  park: [' in src:
    src = re.sub(r'  park: \[\n(?:    ".*",\n)+  \],\n', js, src)
else:
    src = src.replace('const MAPS = {\n', 'const MAPS = {\n' + js)
p.write_text(src)
print('\n'.join(rows))
