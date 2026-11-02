# JCG (working title)

A birthday platformer for Juliana, built in November 2026 on top of the engine from
[Lola](https://github.com/aschaves/lola), an earlier family game. This project is independent: the
code was copied in, not forked, and evolves on its own.

> Status: the game still shows Lola's art, levels and story. They are being replaced with
> Juliana's.

## Play

Open `game/index.html` in a modern browser, or serve the folder:

```sh
python3 -m http.server 8000
# then open http://localhost:8000/game/
```

Once GitHub Pages is enabled (Settings → Pages → Source → "GitHub Actions"), every push to `main`
deploys to https://aschaves.github.io/jcg-game/

## Project layout

```
game/                 Everything that is published
  index.html          Page and menus
  css/style.css       Menu styling
  js/data/            Level layouts, legends, music notes, sound data, UI text (en/pt)
  js/engine/          Image loading, animation, input, sound (Web Audio)
  js/game/            Entities, level simulation, rendering
  js/main.js          Game flow: loading, title, play, pause, level complete, game over, end
  assets/img/         Sprites, tiles, backgrounds
raw/                  Original photos/videos used to make the art (not published)
```

Level layouts are text in `game/js/data/maps.js`; the meaning of each character is in
`game/js/data/levels.js`. URL flags: `?nopause` (don't pause when the tab loses focus) and
`?debug` (exposes `window.GameDebug` with `loadLevel(i)` and `teleport(col)`).
