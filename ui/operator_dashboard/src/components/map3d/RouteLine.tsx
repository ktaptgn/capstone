import { useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import type { Route3D } from './map3dTypes';
import { getDetailTextures } from './proceduralTextures';

const DISPATCH_X = 290;
const DISPATCH_Z = 155;
const ROAD_COLOR = '#46331F';      // dark brown earth road
const CONVEYOR_COLOR = '#5A4B3A';
/** World units per asphalt detail tile (baked into per-road UVs). */
const TILE = 12;
/** Tiny lift so the road paints onto the terrain without z-fighting. */
const ROAD_LIFT = 0.12;

type RouteLineProps = {
  route: Route3D;
  /** Terrain surface height sampler so the road hugs the ground (no floating). */
  elevation: (x: number, z: number) => number;
};

function halfWidth(x: number, z: number, baseWidth: number, kind: string): number {
  if (kind === 'conveyor_feed') return baseWidth * 0.3;
  if (kind === 'service_road') return baseWidth * 0.6;

  const dist = Math.sqrt((x - DISPATCH_X) ** 2 + (z - DISPATCH_Z) ** 2);
  const t = Math.max(0, 1 - dist / 300);
  return baseWidth * 0.5 * (1 + t * t * 1.5);
}

export default function RouteLine({ route, elevation }: RouteLineProps) {
  const gl = useThree((s) => s.gl);
  const detail = getDetailTextures(gl);

  const built = useMemo(() => {
    if (!route.points || route.points.length < 2) return null;

    // Build the centerline in XZ, then snap every sample onto the terrain.
    const rawPts = route.points.map((p) => new THREE.Vector3(p.x, 0, p.z));
    const curve = new THREE.CatmullRomCurve3(rawPts, false, 'catmullrom', 0.25);
    const divisions = Math.max(rawPts.length * 14, 24);
    const sampled = curve.getPoints(divisions);
    for (const pt of sampled) pt.y = elevation(pt.x, pt.z) + ROAD_LIFT;

    const positions: number[] = [];
    const uvs: number[] = [];
    const indices: number[] = [];
    const centerline: THREE.Vector3[] = [];

    let cumDist = 0;
    for (let i = 0; i < sampled.length; i++) {
      const pt = sampled[i];
      if (i > 0) cumDist += pt.distanceTo(sampled[i - 1]);

      let tangent: THREE.Vector3;
      if (i < sampled.length - 1) tangent = sampled[i + 1].clone().sub(pt).normalize();
      else tangent = pt.clone().sub(sampled[i - 1]).normalize();
      const perp = new THREE.Vector3(-tangent.z, 0, tangent.x).normalize();
      const hw = halfWidth(pt.x, pt.z, route.width, route.kind);

      // Snap each edge to the terrain too, so wide roads follow cross-slope.
      const lx = pt.x - perp.x * hw;
      const lz = pt.z - perp.z * hw;
      const rx = pt.x + perp.x * hw;
      const rz = pt.z + perp.z * hw;
      positions.push(
        lx, elevation(lx, lz) + ROAD_LIFT, lz,
        rx, elevation(rx, rz) + ROAD_LIFT, rz,
      );
      const u = cumDist / TILE;
      uvs.push(u, -hw / TILE, u, hw / TILE);
      centerline.push(new THREE.Vector3(pt.x, pt.y + 0.14, pt.z));
    }

    for (let i = 0; i < sampled.length - 1; i++) {
      const a = i * 2;
      indices.push(a, a + 2, a + 1, a + 1, a + 2, a + 3);
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geo.setIndex(indices);
    geo.computeVertexNormals();

    // Center divider line for the big haul roads → reads as a two-lane road.
    const wantsLane = route.kind === 'main_haul' || route.kind === 'main_haul_risk_segment';
    let laneLine: THREE.Line | null = null;
    if (wantsLane && centerline.length > 2) {
      const lgeo = new THREE.BufferGeometry().setFromPoints(centerline);
      const lmat = new THREE.LineDashedMaterial({
        color: '#E9D38A',
        dashSize: 6,
        gapSize: 6,
        transparent: true,
        opacity: 0.6,
      });
      laneLine = new THREE.Line(lgeo, lmat);
      laneLine.computeLineDistances();
    }

    return { geo, laneLine };
  }, [route, elevation]);

  if (!built) return null;
  const { geo, laneLine } = built;

  const isConveyor = route.kind === 'conveyor_feed';
  const color = isConveyor ? CONVEYOR_COLOR : ROAD_COLOR;

  return (
    <group>
      {route.riskLevel === 'high' && (
        <mesh geometry={geo} position={[0, 0.05, 0]}>
          <meshBasicMaterial color="#E8A87C" transparent opacity={0.22} side={THREE.DoubleSide} />
        </mesh>
      )}
      <mesh geometry={geo} receiveShadow>
        <meshStandardMaterial
          color={color}
          roughness={1}
          metalness={0}
          bumpMap={detail.asphaltBump}
          bumpScale={0.5}
          roughnessMap={detail.asphaltRough}
          envMapIntensity={0.25}
          transparent={isConveyor}
          opacity={isConveyor ? 0.85 : 1}
          side={THREE.DoubleSide}
          polygonOffset
          polygonOffsetFactor={-2}
          polygonOffsetUnits={-2}
        />
      </mesh>
      {laneLine && <primitive object={laneLine} />}
    </group>
  );
}
