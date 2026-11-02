# Park level art

`src/parallax_sheet.jpg` and `src/tiles_sheet.jpg` are the source art (three parallax strips are used:
sky, Canary Wharf + river, and the lower walkway with the marshals). Run from this folder:

1. `python3 extract.py src` – crops the strips (painted checkerboard keyed out) and the nine tiles.
2. `python3 build_park.py` – scales the layers (sky 420px and city 403px tall, stretched across the
   level; walkway cross-faded to repeat), paints out the "tiling" arrows, and builds the 64px tiles:
   cone/bike-rack-free variants, D re-warped so its kerb meets E's, soil edges, floating platforms.
3. `python3 sprites.py` – draws the croissant, spinning wine bottle, flying laptop, waiter and finish
   banner; the ASICS collectible uses the pink trainer from the runner photo (`src/juliana_shoe.png`).

Outputs go to `out/`; copy them to `game/assets/img/park/`. The map itself is `tools/levels/park.py`.
