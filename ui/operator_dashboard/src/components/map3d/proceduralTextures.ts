/**
 * Procedural, tileable PBR detail textures generated on a <canvas> at runtime.
 * No network / asset files — safe for the single-file offline build.
 *
 * These add high-frequency surface relief (bump) and roughness variation so the
 * terrain and roads read as real rock / asphalt instead of smooth "clay".
 */
import * as THREE from 'three';

/* Deterministic PRNG so textures are stable across reloads */
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function smooth(t: number): number {
  return t * t * (3 - 2 * t);
}

/** Tileable value-noise field sampled to [0,1], periodic over `freq` lattice cells. */
function valueNoise(size: number, freq: number, seed: number): Float32Array {
  const rand = mulberry32(seed);
  const lattice = new Float32Array(freq * freq);
  for (let i = 0; i < lattice.length; i++) lattice[i] = rand();
  const at = (gx: number, gz: number) =>
    lattice[((gz % freq) + freq) % freq * freq + (((gx % freq) + freq) % freq)];

  const out = new Float32Array(size * size);
  for (let z = 0; z < size; z++) {
    for (let x = 0; x < size; x++) {
      const fx = (x / size) * freq;
      const fz = (z / size) * freq;
      const x0 = Math.floor(fx);
      const z0 = Math.floor(fz);
      const tx = smooth(fx - x0);
      const tz = smooth(fz - z0);
      const v00 = at(x0, z0);
      const v10 = at(x0 + 1, z0);
      const v01 = at(x0, z0 + 1);
      const v11 = at(x0 + 1, z0 + 1);
      const top = v00 + (v10 - v00) * tx;
      const bot = v01 + (v11 - v01) * tx;
      out[z * size + x] = top + (bot - top) * tz;
    }
  }
  return out;
}

/** Fractal Brownian motion (summed octaves) → [0,1], tileable. */
function fbm(
  size: number,
  baseFreq: number,
  octaves: number,
  persistence: number,
  seed: number,
): Float32Array {
  const out = new Float32Array(size * size);
  let amp = 1;
  let freq = baseFreq;
  let norm = 0;
  for (let o = 0; o < octaves; o++) {
    const layer = valueNoise(size, freq, seed + o * 911);
    for (let i = 0; i < out.length; i++) out[i] += layer[i] * amp;
    norm += amp;
    amp *= persistence;
    freq *= 2;
  }
  for (let i = 0; i < out.length; i++) out[i] /= norm;
  return out;
}

function makeCanvas(size: number): { canvas: HTMLCanvasElement; ctx: CanvasRenderingContext2D } {
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  return { canvas, ctx };
}

/** Build a grayscale CanvasTexture from a per-pixel value function (0..255). */
function grayTexture(size: number, valueAt: (i: number) => number): THREE.CanvasTexture {
  const { canvas, ctx } = makeCanvas(size);
  const img = ctx.createImageData(size, size);
  for (let i = 0; i < size * size; i++) {
    const g = Math.max(0, Math.min(255, valueAt(i))) | 0;
    img.data[i * 4] = g;
    img.data[i * 4 + 1] = g;
    img.data[i * 4 + 2] = g;
    img.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  return new THREE.CanvasTexture(canvas);
}

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

function configure(tex: THREE.Texture, repeat: number, renderer?: THREE.WebGLRenderer): THREE.Texture {
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(repeat, repeat);
  tex.anisotropy = renderer ? renderer.capabilities.getMaxAnisotropy() : 8;
  tex.needsUpdate = true;
  return tex;
}

let _cache: {
  terrainBump: THREE.Texture;
  terrainRough: THREE.Texture;
  asphaltBump: THREE.Texture;
  asphaltRough: THREE.Texture;
} | null = null;

/**
 * Lazily build & cache the detail texture set. Pass the renderer once it exists
 * so anisotropic filtering is maxed for crisp grazing-angle detail.
 */
export function getDetailTextures(renderer?: THREE.WebGLRenderer) {
  if (_cache) {
    if (renderer) {
      const aniso = renderer.capabilities.getMaxAnisotropy();
      for (const t of Object.values(_cache)) t.anisotropy = aniso;
    }
    return _cache;
  }

  const SIZE = 256;

  /* ── Terrain: coarse rocky relief + fine grain ── */
  const tHi = fbm(SIZE, 24, 4, 0.55, 1337);
  const tLo = fbm(SIZE, 6, 3, 0.5, 7);
  const terrainBumpTex = grayTexture(SIZE, (i) => 30 + clamp01(tHi[i] * 0.7 + tLo[i] * 0.3) * 200);
  // Roughness: drier highs rougher, hollows slightly smoother → varied sheen
  const terrainRoughTex = grayTexture(
    SIZE,
    (i) => clamp01(0.62 + (tLo[i] - 0.5) * 0.5 + (tHi[i] - 0.5) * 0.18) * 255,
  );

  /* ── Asphalt: fine gravelly grain + faint worn patches ── */
  const aHi = fbm(SIZE, 48, 4, 0.6, 4242);
  const aLo = fbm(SIZE, 10, 2, 0.5, 99);
  const asphaltBumpTex = grayTexture(SIZE, (i) => 60 + clamp01(aHi[i] * 0.8 + aLo[i] * 0.2) * 150);
  const asphaltRoughTex = grayTexture(
    SIZE,
    (i) => clamp01(0.78 - (aLo[i] - 0.5) * 0.45 + (aHi[i] - 0.5) * 0.12) * 255,
  );

  _cache = {
    // Terrain uses 0..1 planar UVs, so .repeat sets the tile density directly.
    terrainBump: configure(terrainBumpTex, 90, renderer),
    terrainRough: configure(terrainRoughTex, 90, renderer),
    // Roads bake world-scale tiling into their own UVs → keep repeat at 1.
    asphaltBump: configure(asphaltBumpTex, 1, renderer),
    asphaltRough: configure(asphaltRoughTex, 1, renderer),
  };
  return _cache;
}
