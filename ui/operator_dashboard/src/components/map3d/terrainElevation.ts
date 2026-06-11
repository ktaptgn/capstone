/**
 * Shared terrain elevation model. Extracted so roads, trucks and the camera
 * floor can all sit on the *exact same* surface the terrain mesh is built from.
 */
import type { C5OperationMap3DData, TerrainHeightRegion } from './map3dTypes';

export const TERRAIN_EXTEND = 400;

/** Simple pseudo-noise for mountain / surface variation. */
export function noise2D(x: number, z: number): number {
  const s1 = Math.sin(x * 0.017 + z * 0.023) * 0.5;
  const s2 = Math.sin(x * 0.031 - z * 0.019) * 0.3;
  const s3 = Math.sin(x * 0.053 + z * 0.047) * 0.2;
  return s1 + s2 + s3;
}

export function elevationAt(
  x: number,
  z: number,
  regions: TerrainHeightRegion[],
  elevationScale: number,
  baseHeight: number,
  bw: number,
  bd: number,
): number {
  if (x < 0 || x > bw || z < 0 || z > bd) {
    // Distance from nearest boundary point
    const cx = Math.max(0, Math.min(bw, x));
    const cz = Math.max(0, Math.min(bd, z));
    const dist = Math.sqrt((x - cx) ** 2 + (z - cz) ** 2);
    const edgeH = elevationAt(cx, cz, regions, elevationScale, baseHeight, bw, bd);

    // Mountains rise with distance from mine boundary → basin formation
    const riseT = Math.min(dist / 280, 1);
    const riseCurve = riseT * riseT * (3 - 2 * riseT);
    const peakHeight = 90 + 50 * noise2D(x, z);
    const ridgeNoise = 15 * noise2D(x * 1.8, z * 1.8);
    const mountainH = riseCurve * peakHeight + ridgeNoise * riseT;

    const blendT = Math.min(dist / 40, 1);
    return edgeH * (1 - blendT) + mountainH * blendT;
  }

  return regions.reduce((h, r) => {
    const dx = x - r.center.x;
    const dz = z - r.center.z;
    const d = Math.sqrt(dx * dx + dz * dz);
    const rad = r.radius ?? 95;
    const fall = Math.max(0, 1 - d / Math.max(rad, 1));
    const wf = fall * fall;

    if (typeof r.height === 'number') {
      const c = baseHeight + r.height * wf;
      return Math.abs(c - baseHeight) > Math.abs(h - baseHeight) ? c : h;
    }
    return h + (r.elevation ?? 0) * wf * elevationScale;
  }, baseHeight);
}

/** Convenience: elevation at (x,z) pulling all params from the map data. */
export function sampleElevation(data: C5OperationMap3DData, x: number, z: number): number {
  const regions = data.terrain?.height_regions || [];
  const elScale = data.scene.elevationScale ?? 0.18;
  const baseH = data.scene.baseHeight ?? 0;
  const bw = data.scene.bounds.width;
  const bd = data.scene.bounds.height;
  return elevationAt(x, z, regions, elScale, baseH, bw, bd);
}

/** Lowest terrain height across the operational area (for camera floor). */
export function minOperationalElevation(data: C5OperationMap3DData, steps = 24): number {
  const bw = data.scene.bounds.width;
  const bd = data.scene.bounds.height;
  let min = Infinity;
  for (let i = 0; i <= steps; i++) {
    for (let j = 0; j <= steps; j++) {
      const e = sampleElevation(data, (i / steps) * bw, (j / steps) * bd);
      if (e < min) min = e;
    }
  }
  return Number.isFinite(min) ? min : 0;
}
