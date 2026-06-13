import { useMemo } from 'react';
import * as THREE from 'three';
import type { C5OperationMap3DData, TerrainHeightRegion } from './map3dTypes';

const palette = {
  base: '#B35F44',
  slope: '#9E4935',
  shadow: '#4D221B',
  highlight: '#D07E61',
  mountain: '#6B4F3A',   // rocky brown for high peaks
  ridge: '#8B7355',      // lighter ridge color
};

type TerrainMeshProps = {
  data: C5OperationMap3DData;
};

const EXTEND = 400;

/** Simple pseudo-noise for mountain variation */
function noise2D(x: number, z: number): number {
  const s1 = Math.sin(x * 0.017 + z * 0.023) * 0.5;
  const s2 = Math.sin(x * 0.031 - z * 0.019) * 0.3;
  const s3 = Math.sin(x * 0.053 + z * 0.047) * 0.2;
  return s1 + s2 + s3;
}

function elevationAt(
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
    const riseT = Math.min(dist / 280, 1);          // 0 at boundary → 1 at EXTEND
    const riseCurve = riseT * riseT * (3 - 2 * riseT); // smooth hermite
    const peakHeight = 90 + 50 * noise2D(x, z);     // varied mountain peaks
    const ridgeNoise = 15 * noise2D(x * 1.8, z * 1.8); // secondary ridgeline noise
    const mountainH = riseCurve * peakHeight + ridgeNoise * riseT;

    // Blend from edge height to mountain height
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

export default function TerrainMesh({ data }: TerrainMeshProps) {
  const terrainGeo = useMemo(() => {
    const bw = data.scene.bounds.width;
    const bd = data.scene.bounds.height;
    const totalW = bw + EXTEND * 2;
    const totalD = bd + EXTEND * 2;
    const seg = 80;
    const positions: number[] = [];
    const indices: number[] = [];
    const regions = data.terrain?.height_regions || [];
    const elScale = data.scene.elevationScale ?? 0.18;
    const baseH = data.scene.baseHeight ?? 0;
    const maxH = data.terrain?.maxHeight || 48;

    for (let zi = 0; zi <= seg; zi++) {
      for (let xi = 0; xi <= seg; xi++) {
        const x = -EXTEND + (xi / seg) * totalW;
        const z = -EXTEND + (zi / seg) * totalD;
        positions.push(x, elevationAt(x, z, regions, elScale, baseH, bw, bd), z);
      }
    }

    for (let zi = 0; zi < seg; zi++) {
      for (let xi = 0; xi < seg; xi++) {
        const row = seg + 1;
        const a = zi * row + xi;
        indices.push(a, a + row, a + 1, a + 1, a + row, a + row + 1);
      }
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setIndex(indices);
    geo.computeVertexNormals();

    const normals = geo.getAttribute('normal');
    const posAttr = geo.getAttribute('position');
    const colors: number[] = [];
    const baseC = new THREE.Color(palette.base);
    const slopeC = new THREE.Color(palette.slope);
    const shadowC = new THREE.Color(palette.shadow);
    const highC = new THREE.Color(palette.highlight);
    const mountainC = new THREE.Color(palette.mountain);
    const ridgeC = new THREE.Color(palette.ridge);

    for (let i = 0; i < posAttr.count; i++) {
      const px = posAttr.getX(i);
      const py = posAttr.getY(i);
      const pz = posAttr.getZ(i);
      const ny = normals.getY(i);
      const outside = px < 0 || px > bw || pz < 0 || pz > bd;
      const c = baseC.clone();

      if (outside) {
        // Mountain coloring: height-based gradient
        const mh = Math.max(0, py) / 120; // normalize to max mountain height
        c.lerp(mountainC, 0.4 + mh * 0.3);
        // Steep slopes get darker
        const sf = 1 - Math.abs(ny);
        if (sf > 0.3) c.lerp(shadowC, Math.min((sf - 0.3) * 1.5, 0.5));
        // High peaks get lighter ridge color
        if (mh > 0.5) c.lerp(ridgeC, (mh - 0.5) * 0.6);
      } else {
        const hr = maxH > 0 ? Math.max(0, py) / maxH : 0;
        const sf = 1 - Math.abs(ny);
        if (sf > 0.25) c.lerp(slopeC, Math.min((sf - 0.25) * 2, 1));
        if (hr > 0.4) c.lerp(highC, (hr - 0.4) * 0.7);
        if (hr < 0.1) c.lerp(shadowC, (0.1 - hr) * 3);
      }
      colors.push(c.r, c.g, c.b);
    }

    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    return geo;
  }, [data]);

  const boundaryLine = useMemo(() => {
    const bw = data.scene.bounds.width;
    const bd = data.scene.bounds.height;
    const regions = data.terrain?.height_regions || [];
    const elScale = data.scene.elevationScale ?? 0.18;
    const baseH = data.scene.baseHeight ?? 0;
    const corners: [number, number][] = [
      [0, 0], [bw, 0], [bw, bd], [0, bd], [0, 0],
    ];

    const pts: THREE.Vector3[] = [];
    for (let seg = 0; seg < corners.length - 1; seg++) {
      const [sx, sz] = corners[seg];
      const [ex, ez] = corners[seg + 1];
      const steps = 24;
      for (let s = 0; s <= (seg < corners.length - 2 ? steps - 1 : steps); s++) {
        const t = s / steps;
        const x = sx + (ex - sx) * t;
        const z = sz + (ez - sz) * t;
        pts.push(new THREE.Vector3(x, elevationAt(x, z, regions, elScale, baseH, bw, bd) + 1.5, z));
      }
    }

    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    const mat = new THREE.LineDashedMaterial({
      color: '#FFFFFF',
      dashSize: 8,
      gapSize: 5,
      opacity: 0.55,
      transparent: true,
    });
    const line = new THREE.Line(geo, mat);
    line.computeLineDistances();
    return line;
  }, [data]);

  const gridGeo = useMemo(() => {
    const bw = data.scene.bounds.width;
    const bd = data.scene.bounds.height;
    const regions = data.terrain?.height_regions || [];
    const elScale = data.scene.elevationScale ?? 0.18;
    const baseH = data.scene.baseHeight ?? 0;
    const spacing = 50;
    const steps = 20;
    const pos: number[] = [];

    for (let gx = 0; gx <= bw; gx += spacing) {
      for (let s = 0; s < steps; s++) {
        const z1 = (s / steps) * bd;
        const z2 = ((s + 1) / steps) * bd;
        pos.push(gx, elevationAt(gx, z1, regions, elScale, baseH, bw, bd) + 0.8, z1);
        pos.push(gx, elevationAt(gx, z2, regions, elScale, baseH, bw, bd) + 0.8, z2);
      }
    }
    for (let gz = 0; gz <= bd; gz += spacing) {
      for (let s = 0; s < steps; s++) {
        const x1 = (s / steps) * bw;
        const x2 = ((s + 1) / steps) * bw;
        pos.push(x1, elevationAt(x1, gz, regions, elScale, baseH, bw, bd) + 0.8, gz);
        pos.push(x2, elevationAt(x2, gz, regions, elScale, baseH, bw, bd) + 0.8, gz);
      }
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    return geo;
  }, [data]);

  return (
    <group>
      <mesh geometry={terrainGeo}>
        <meshStandardMaterial vertexColors roughness={0.92} metalness={0} />
      </mesh>
      <primitive object={boundaryLine} />
      <lineSegments geometry={gridGeo}>
        <lineBasicMaterial color="#FFFFFF" opacity={0.08} transparent />
      </lineSegments>
    </group>
  );
}
