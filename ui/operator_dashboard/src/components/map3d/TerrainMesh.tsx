import { useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import type { C5OperationMap3DData } from './map3dTypes';
import { getDetailTextures } from './proceduralTextures';
import { TERRAIN_EXTEND as EXTEND, noise2D, elevationAt } from './terrainElevation';

/* Sandy-khaki desert palette (replaces the old reddish clay tones) */
const palette = {
  base: '#C2B280',       // sand / khaki
  slope: '#A6976A',      // shaded khaki slope
  shadow: '#5F5639',     // deep crevice shadow
  highlight: '#DACEA2',  // sun-bleached sand
  mountain: '#8B7E5A',   // khaki-brown peaks
  ridge: '#AEA078',      // lighter ridge
};

type TerrainMeshProps = {
  data: C5OperationMap3DData;
};

export default function TerrainMesh({ data }: TerrainMeshProps) {
  const gl = useThree((s) => s.gl);
  const detail = getDetailTextures(gl);

  const terrainGeo = useMemo(() => {
    const bw = data.scene.bounds.width;
    const bd = data.scene.bounds.height;
    const totalW = bw + EXTEND * 2;
    const totalD = bd + EXTEND * 2;
    const seg = 100;
    const positions: number[] = [];
    const uvs: number[] = [];
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
        // Planar UVs across the whole terrain (texture .repeat tiles the detail)
        uvs.push((x + EXTEND) / totalW, (z + EXTEND) / totalD);
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
    geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
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
        // Organic multi-scale color mottling so the flat ground reads as sandy
        // rock rather than a uniform clay slab.
        const n = noise2D(px * 0.6, pz * 0.6) + 0.5 * noise2D(px * 1.7, pz * 1.7);
        if (n > 0) c.lerp(shadowC, Math.min(n * 0.1, 0.16));
        else c.lerp(highC, Math.min(-n * 0.08, 0.12));
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
      <mesh geometry={terrainGeo} receiveShadow castShadow>
        <meshStandardMaterial
          vertexColors
          roughness={1}
          metalness={0}
          bumpMap={detail.terrainBump}
          bumpScale={2.2}
          roughnessMap={detail.terrainRough}
          envMapIntensity={0.3}
          dithering
        />
      </mesh>
      <primitive object={boundaryLine} />
      <lineSegments geometry={gridGeo}>
        <lineBasicMaterial color="#DCE7F5" opacity={0.06} transparent />
      </lineSegments>
    </group>
  );
}
