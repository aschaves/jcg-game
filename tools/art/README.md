# Character art pipeline (Juliana)

The player sprites in `game/assets/img/juliana/` are generated from photos by these scripts. The
photos themselves are not in the repo (privacy); put them in a working folder as `1.webp`, `2.jpg`,
`3.jpg`, `4.jpg`, `5.jpg` (1 = tongue out, 2 = smirk, 3 = laughing, 4 = runner outfit, 5 = smiling).

Run everything from that working folder (`pip install "rembg[cpu]"` first):

1. `python3 rb.py <photos dir> cut` – background removal (rembg, isnet-general-use) into `cut/`.
2. `python3 heads.py` – aligns each face on its eyes into a 400×480 canonical head, evens out the skin
   colour between photos, masks it to an oval.
3. `python3 beanie2.py` – draws the grey beanie (colour sampled from the runner photo) on every head.
4. `python3 rig.py` – cuts torso, arms and shoe out of the runner photo, draws the leggings, and poses
   the frames (run1-6, idle1-3, jump1, hurt1) into `juliana/` at 150×190.

`grid.py` overlays a coordinate grid on a photo; the eye positions and cut polygons in the scripts were
read off those grids. If a photo changes, those coordinates need updating.
