import { useMemo } from 'react';
import * as THREE from 'three';
import type { Route3D } from './map3dTypes';

const DISPATCH_X = 290;
const DISPATCH_Z = 155;
const ROAD_COLOR = '#36454F';

/** Circular cutout around dispatch compass — road quads inside this radius are skipped */
const COMPASS_CUTOUT_R = 42;

type RouteLineProps = {
  route: Route3D;
};

function halfWidth(x: number, z: number, baseWidth: number, kind: string): number {
  if (kind === 'conveyor_feed') return baseWidth * 0.3;
  if (kind === 'service_road') return baseWidth * 0.6;

  const dist = Math.sqrt((x - DISPATCH_X) ** 2 + (z - DISPATCH_Z) ** 2);
  const t = Math.max(0, 1 - dist / 300);
  return baseWidth * 0.5 * (1 + t * t * 1.5);
}

function distToDispatch(x: number, z: number): number {
  return Math.sqrt((x - DISPATCH_X) ** 2 + (z - DISPATCH_Z) ** 2);
}

export default function RouteLine({ route }: RouteLineProps) {
  const geometry = useMemo(() => {
    if (!route.points || route.points.length < 2) return null;

    const rawPts = route.points.map(
      (p) => new THREE.Vector3(p.x, p.y + 0.5, p.z),
    );
    const curve = new THREE.CatmullRomCurve3(rawPts, false, 'catmullrom', 0.25);
    const divisions = Math.max(rawPts.length * 14, 24);
    const sampled = curve.getPoints(divisions);
    const positions: number[] = [];
    const indices: number[] = [];

    for (let i = 0; i < sampled.length; i++) {
      const pt = sampled[i];
      let tangent: THREE.Vector3;
      if (i < sampled.length - 1) {
        tangent = sampled[i + 1].clone().sub(pt).normalize();
      } else {
        tangent = pt.clone().sub(sampled[i - 1]).normalize();
      }
      const perp = new THREE.Vector3(-tangent.z, 0, tangent.x).normalize();
      const hw = halfWidth(pt.x, pt.z, route.width, route.kind);

      positions.push(
        pt.x - perp.x * hw, pt.y, pt.z - perp.z * hw,
        pt.x + perp.x * hw, pt.y, pt.z + perp.z * hw,
      );
    }

    // Build index buffer — skip quads that fall inside the compass cutout zone
    for (let i = 0; i < sampled.length - 1; i++) {
      const pt = sampled[i];
      const ptNext = sampled[i + 1];
      const d0 = distToDispatch(pt.x, pt.z);
      const d1 = distToDispatch(ptNext.x, ptNext.z);

      // Both endpoints inside the compass zone → skip this quad entirely
      if (d0 < COMPASS_CUTOUT_R && d1 < COMPASS_CUTOUT_R) continue;

      const a = i * 2;
      indices.push(a, a + 2, a + 1, a + 1, a + 2, a + 3);
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setIndex(indices);
    geo.computeVertexNormals();
    return geo;
  }, [route]);

  if (!geometry) return null;

  const isConveyor = route.kind === 'conveyor_feed';
  const color = isConveyor ? '#475569' : ROAD_COLOR;
  const opacity = isConveyor ? 0.72 : 0.9;

  return (
    <group>
      {route.riskLevel === 'high' && (
        <mesh geometry={geometry}>
          <meshBasicMaterial
            color="#FEE2E2"
            transparent
            opacity={0.25}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}
      <mesh geometry={geometry}>
        <meshStandardMaterial
          color={color}
          roughness={0.86}
          metalness={0}
          transparent
          opacity={opacity}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}
