# Notes for Claude

- Birthday game for Juliana Carvalho Gallo ("JCG"), a friend of the repo owner. Built on a copy of
  the Lola engine (github.com/aschaves/lola) but fully independent: never push to or depend on lola.
- Repo name and game title are temporary. Keep the title in one place (`game/index.html` title/logo
  and `game/js/data/strings.js`) so it is easy to rename. If the repo is renamed, the Pages URL changes.
- Plain HTML/CSS/JS, no dependencies, no build step. Keep it that way.
- localStorage keys are prefixed `jcg.` — the game shares the aschaves.github.io origin with Lola.
- `raw/` holds the owner's original media; process it into `game/assets/img/` (ffmpeg, ImageMagick
  and Pillow are available). Never publish raw media; Pages deploys only `game/`.
- Art comes from the owner's photos/videos processed in code; there is no AI image generation.
- Cloud containers are ephemeral: commit and push after each meaningful step.
- Verify changes by running the game in headless Chromium (Playwright is preinstalled) and
  taking screenshots.
