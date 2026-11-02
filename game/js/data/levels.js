// Level definitions. The layouts live in maps.js; this file explains what each character means in
// each level and which assets it uses.
//
// Entity types:
//   treat  – collectible, adds score
//   music  – collectible that also toggles the drum track in the music (as in the original)
//   enemy  – walks (or flies) and catches the player; stomping it from above defeats it
//   goal   – what waits at the end of the level
//
// Speeds are in pixels per second (the original used pixels per millisecond: 0.05 -> 50).

const IMG = 'assets/img/';

function frames(base, indexes, ms) {
  const times = Array.isArray(ms) ? ms : indexes.map(() => ms);
  return indexes.map((i, k) => [`${IMG}${base}${i}.png`, times[k]]);
}

function tileset(dir, chars) {
  const map = {};
  [...chars].forEach((ch, i) => { map[ch] = `${IMG}${dir}/tile_${String.fromCharCode(65 + i)}.png`; });
  return map;
}

const treat = (name, fr, score, box) => ({ type: 'treat', name, frames: fr, score, box: box || { ox: 8, oy: 8, w: 67, h: 67 } });
const music = (name, fr, score) => ({ type: 'music', name, frames: fr, score, box: { ox: 8, oy: 8, w: 67, h: 67 } });
const enemy = (name, fr, opts) => Object.assign({ type: 'enemy', name, frames: fr, speed: 50, flying: false, turnAtEdges: false }, opts);
const goal = (name, fr, box) => ({ type: 'goal', name, frames: fr, box });

const LEVELS = [
  {
    id: 'park',
    name: { en: 'Saturday parkrun', pt: 'parkrun de sábado' },
    subtitle: { en: 'Greenwich Peninsula. Grab the croissants, dodge the wine and the work laptop!', pt: 'Greenwich Peninsula. Pegue os croissants, fuja do vinho e do laptop do trabalho!' },
    found: 'foundPark',
    bgColor: '#88d5fc',
    // Three parallax layers: sky with the cable cars, Canary Wharf across the river, the riverside walkway.
    layers: [
      { image: IMG + 'park/sky.png', y: 0, mode: 'stretch' },
      { image: IMG + 'park/city.png', y: 150, mode: 'stretch' },
      { image: IMG + 'park/path.png', y: 400, mode: 'tile', speed: 0.8 },
    ],
    // Ground: A B C top (Q with a cone), D E F kerb row (R with bike racks), G H I soil; J K L floating platforms.
    tiles: Object.fromEntries([...'ABCDEFGHIJKLQR'].map((ch) => [ch, `${IMG}park/tile_${ch}.png`])),
    rows: MAPS.park,
    spawn: { col: 3 },
    legend: {
      'o': treat('croissant', frames('park/croissant', [1, 2], [260, 260]), 100, { ox: 6, oy: 16, w: 68, h: 40 }),
      '!': music('asics', frames('park/asics', [1, 1, 2], [300, 300, 200]), 250),
      '1': enemy('waiter', frames('park/waiter', [1, 2, 3, 4], 180), { speed: 60, turnAtEdges: true, box: { ox: 40, oy: 14, w: 62, h: 182 } }),
      '2': enemy('wine', frames('park/bottle', [1, 2, 3, 4, 5, 6, 7, 8], 70), { speed: 190, flying: true, box: { ox: 30, oy: 30, w: 50, h: 50 } }),
      '3': enemy('laptop', frames('park/laptop', [1, 2, 3, 2], 110), { speed: 140, flying: true, box: { ox: 36, oy: 10, w: 78, h: 62 } }),
      '-': goal('finish', frames('park/finish', [1, 2, 3], 220), { ox: 20, oy: 30, w: 160, h: 230 }),
    },
    // Placeholder until we know who is waiting at the finish.
    final: frames('juliana/jump', [1], 500),
  },
];

// Juliana, the player: photo cut-out frames (oversized photo head on a rigged body in her running kit).
// Faces: smile while running/idle, a smirk now and then while waiting, laughing in the air, tongue out when caught.
const PLAYER = {
  run: frames('juliana/run', [1, 2, 3, 4, 5, 6], 95),
  idle: frames('juliana/idle', [1, 2, 1, 2, 3, 1], [700, 500, 600, 500, 900, 400]),
  jump: frames('juliana/jump', [1], 100),
  hurt: frames('juliana/hurt', [1], 100),
  box: { ox: 54, oy: 24, w: 46, h: 164 },
};

const UI_IMAGES = [
  IMG + 'ui/splash-title.png',
  IMG + 'ui/splash-loading.png',
  IMG + 'ui/splash-end.png',
];
