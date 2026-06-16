import { useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import operationMapData from '../../data/c5_operation_map_3d.json';
import CameraPresets, { SceneCameraController } from './CameraPresets';
import FacilityCube from './FacilityCube';
import PMDecisionGate from './PMDecisionGate';
import MapLegend from './MapLegend';
import { getRouteMidpoint } from './map3dUtils';
import MapOverlayLabel from './MapOverlayLabel';
import QueueArea from './QueueArea';
import RouteLine from './RouteLine';
import TerrainMesh from './TerrainMesh';
import TruckFleet from './TruckFleet';
import SceneLighting from './SceneLighting';
import PostFX from './PostFX';
import { sampleElevation, minOperationalElevation } from './terrainElevation';
import type { C5OperationMap3DData } from './map3dTypes';

/* Clamp the camera so it can never drop below the terrain and look up through
   the whole map from underground. */
function CameraFloor({ minY }: { minY: number }) {
  const camera = useThree((s) => s.camera);
  useFrame(() => {
    if (camera.position.y < minY) camera.position.y = minY;
  });
  return null;
}

const DISPATCH_AREA_IDS = new Set(['dispatch', 'service_zone', 'standby']);

/* ── Sky gradient dome ─────────────────────────────── */
const SKY_PALETTES = [
  // 0: dawn (06:00–08:00)
  { top: '#1a1a3e', mid: '#7b5ea7', horizon: '#f4a460', ground: '#c67b4f' },
  // 1: morning (08:00–12:00)
  { top: '#1e90ff', mid: '#87ceeb', horizon: '#dce8f0', ground: '#c9b8a8' },
  // 2: afternoon (12:00–16:00)
  { top: '#2563eb', mid: '#60a5fa', horizon: '#e0e7f1', ground: '#c2a88a' },
  // 3: sunset (16:00–19:00)
  { top: '#1e3a5f', mid: '#d4735e', horizon: '#f59e0b', ground: '#a0522d' },
  // 4: night (19:00–06:00)
  { top: '#0a0a2e', mid: '#1a1a4e', horizon: '#2d2d5e', ground: '#1e1e3e' },
];

function lerpColor(a: THREE.Color, b: THREE.Color, t: number): THREE.Color {
  return a.clone().lerp(b, t);
}

function SkyDome({ timeSpeed = 1 }: { timeSpeed: number }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const timeRef = useRef(8); // start at 08:00

  useFrame((_, delta) => {
    // Advance simulated hour: 1 real second = 1/60 simulated hour at 1x speed
    timeRef.current += (delta / 60) * timeSpeed;
    if (timeRef.current >= 24) timeRef.current -= 24;

    const hour = timeRef.current;
    let paletteIdx: number;
    let t: number;

    if (hour >= 6 && hour < 8) { paletteIdx = 0; t = (hour - 6) / 2; }
    else if (hour >= 8 && hour < 12) { paletteIdx = 1; t = (hour - 8) / 4; }
    else if (hour >= 12 && hour < 16) { paletteIdx = 2; t = (hour - 12) / 4; }
    else if (hour >= 16 && hour < 19) { paletteIdx = 3; t = (hour - 16) / 3; }
    else { paletteIdx = 4; t = 0; }

    const from = SKY_PALETTES[paletteIdx];
    const to = SKY_PALETTES[(paletteIdx + 1) % SKY_PALETTES.length];

    const topC = lerpColor(new THREE.Color(from.top), new THREE.Color(to.top), t);
    const midC = lerpColor(new THREE.Color(from.mid), new THREE.Color(to.mid), t);
    const horizC = lerpColor(new THREE.Color(from.horizon), new THREE.Color(to.horizon), t);

    const mesh = meshRef.current;
    if (!mesh) return;
    const geo = mesh.geometry;
    const posAttr = geo.getAttribute('position');
    const colors = geo.getAttribute('color');

    if (!colors) {
      const arr = new Float32Array(posAttr.count * 3);
      geo.setAttribute('color', new THREE.BufferAttribute(arr, 3));
    }
    const colAttr = geo.getAttribute('color') as THREE.BufferAttribute;

    for (let i = 0; i < posAttr.count; i++) {
      const ny = posAttr.getY(i) / 800; // normalized y: -1 (bottom) to +1 (top)
      let c: THREE.Color;
      if (ny > 0.3) {
        c = lerpColor(midC, topC, Math.min((ny - 0.3) / 0.7, 1));
      } else if (ny > -0.1) {
        c = lerpColor(horizC, midC, (ny + 0.1) / 0.4);
      } else {
        c = horizC.clone();
      }
      colAttr.setXYZ(i, c.r, c.g, c.b);
    }
    colAttr.needsUpdate = true;
  });

  return (
    <mesh ref={meshRef} position={[330, -50, 140]}>
      <sphereGeometry args={[800, 32, 24]} />
      <meshBasicMaterial vertexColors side={THREE.BackSide} fog={false} />
    </mesh>
  );
}

type C5OperationMap3DProps = {
  timeSpeed?: number;
  /** When true, the map fills its parent's height instead of a fixed 388px. */
  fill?: boolean;
};

export default function C5OperationMap3D({ timeSpeed = 1, fill = false }: C5OperationMap3DProps) {
  const data = operationMapData as C5OperationMap3DData;
  const [activePresetId, setActivePresetId] = useState(
    data.camera?.presets?.[0]?.id || 'overview',
  );
  const [labelsVisible, setLabelsVisible] = useState(true);
  const controlsRef = useRef(null);

  const initialCamera = useMemo(() => {
    const position = data.camera?.default_position || { x: 330, y: 185, z: 365 };
    return {
      position: [position.x, position.y, position.z] as [number, number, number],
      fov: 45,
      near: 1,
      far: 2000,
    };
  }, [data.camera]);

  // PM Decision Gate position: on the PM Bay access road (or near the bay).
  const pmGatePos = useMemo<[number, number, number]>(() => {
    const pmRoute = data.routes.find((r) => r.id === 'branch_pm_bay');
    if (pmRoute && pmRoute.points?.length) {
      const m = getRouteMidpoint(pmRoute);
      return [m.x, m.y, m.z];
    }
    const bay = data.facilities.find((f) => f.id === 'pm_bay');
    return bay ? [bay.position.x - 24, bay.position.y, bay.position.z + 24] : [500, 10, 80];
  }, [data.routes, data.facilities]);

  // Pre-build CatmullRomCurve3 for each route so trucks can animate along them
  const routeCurves = useMemo(() => {
    const map = new Map<string, THREE.CatmullRomCurve3>();
    const routeById = new Map<string, typeof data.routes[0]>();
    for (const route of data.routes) {
      if (!route.points || route.points.length < 2) continue;
      routeById.set(route.id, route);
      const pts = route.points.map(
        (p: {x:number;y:number;z:number}) => new THREE.Vector3(p.x, sampleElevation(data, p.x, p.z), p.z),
      );
      const curve = new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0.25);
      map.set(route.id, curve);
    }

    /* Build compound routes: full shovel→crusher/PM via main road */
    const compoundDefs: Record<string, { segs: [string, boolean][] }> = {
      full_sa_c1: { segs: [['branch_shovel_a', true], ['main_road', false], ['branch_crusher_1', false]] },
      full_sb_c2: { segs: [['branch_shovel_b', true], ['main_road', false], ['branch_crusher_2', false]] },
      full_sc_c1: { segs: [['branch_shovel_c', true], ['main_road', false], ['branch_crusher_1', false]] },
      full_sa_c2: { segs: [['branch_shovel_a', true], ['main_road', false], ['branch_crusher_2', false]] },
      full_sb_c1: { segs: [['branch_shovel_b', true], ['main_road', false], ['branch_crusher_1', false]] },
      full_sc_pm: { segs: [['branch_shovel_c', true], ['main_road', false], ['branch_pm_bay', false]] },
      full_sa_pm: { segs: [['branch_shovel_a', true], ['main_road', false], ['branch_pm_bay', false]] },
    };

    for (const [compId, def] of Object.entries(compoundDefs)) {
      const allPts: THREE.Vector3[] = [];
      for (const [segId, reversed] of def.segs) {
        const route = routeById.get(segId);
        if (!route?.points) continue;
        let segPts = route.points.map((p: {x:number;y:number;z:number}) => new THREE.Vector3(p.x, sampleElevation(data, p.x, p.z), p.z));
        if (reversed) segPts = segPts.slice().reverse();
        // Skip first point if overlapping with previous segment's last point
        const start = allPts.length > 0 && segPts.length > 0 && allPts[allPts.length - 1].distanceTo(segPts[0]) < 25 ? 1 : 0;
        for (let i = start; i < segPts.length; i++) allPts.push(segPts[i]);
      }
      if (allPts.length >= 2) {
        map.set(compId, new THREE.CatmullRomCurve3(allPts, false, 'catmullrom', 0.25));
      }
    }

    return map;
  }, [data]);

  // Terrain height sampler so roads hug the ground; camera floor = lowest ground.
  const elevation = useMemo(() => (x: number, z: number) => sampleElevation(data, x, z), [data]);
  const groundFloorY = useMemo(() => minOperationalElevation(data) + 3, [data]);

  // Reassign trucks to compound routes for full road traversal
  const mappedTrucks = useMemo(() => {
    const routeRemap: Record<string, string> = {
      T01: 'full_sa_c1', T02: 'full_sb_c2', T03: 'full_sc_c1',
      T04: 'full_sa_c2', T05: 'full_sa_c2', T06: 'full_sb_c1',
      T07: 'full_sa_pm', T08: 'full_sc_c1', T09: 'full_sc_pm',
      T10: 'full_sa_c1', T11: 'full_sb_c2', T13: 'full_sb_c1',
      T14: 'full_sc_pm', T16: 'full_sa_c2', T17: 'full_sb_c1',
      T18: 'full_sc_c1', T19: 'full_sa_pm', T20: 'full_sb_c2',
      T21: 'full_sc_c1', T22: 'full_sa_c1', T23: 'full_sb_c1',
      T24: 'full_sc_pm', T25: 'full_sa_pm',
    };
    return data.truckFrames.map(t => {
      const newRoute = routeRemap[t.truck_id];
      if (newRoute && t.speed > 0) {
        return { ...t, route_id: newRoute, route_progress: 0.1 + Math.random() * 0.3 };
      }
      return t;
    });
  }, [data.truckFrames]);

  if (!data?.scene || !data?.facilities) {
    return (
      <div
        style={{
          height: 360,
          border: '1px dashed #CBD5E1',
          borderRadius: 8,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#64748B',
          background: '#F8FAFC',
        }}
      >
        3D map data not available
      </div>
    );
  }

  return (
    <div style={fill ? { flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' } : undefined}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          gap: 12,
          alignItems: 'center',
          marginBottom: 10,
          flexWrap: 'wrap',
        }}
      >
        <CameraPresets
          camera={data.camera}
          activePresetId={activePresetId}
          onSelect={setActivePresetId}
        />
        <button
          type="button"
          onClick={() => setLabelsVisible((v) => !v)}
          style={{
            border: '1px solid #CBD5E1',
            background: labelsVisible ? '#FFFFFF' : '#F8FAFC',
            color: '#334155',
            borderRadius: 6,
            padding: '5px 9px',
            fontSize: 11,
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          Labels {labelsVisible ? 'On' : 'Off'}
        </button>
      </div>

      <div
        style={{
          ...(fill ? { flex: 1, minHeight: 320 } : { height: 388 }),
          borderRadius: 8,
          overflow: 'hidden',
          border: '1px solid #E2E8F0',
          background: '#EEF2F7',
        }}
      >
        <Canvas
          shadows
          camera={initialCamera}
          dpr={[1, 1.6]}
          gl={{ antialias: false, toneMapping: THREE.NoToneMapping }}
        >
          <fog attach="fog" args={['#cabfa3', 380, 1350]} />
          <SkyDome timeSpeed={timeSpeed} />
          <SceneLighting
            center={[data.scene.bounds.width / 2, data.scene.bounds.height / 2]}
            shadowExtent={420}
          />
          <TerrainMesh data={data} />
          {data.routes.map((route) => (
            <RouteLine key={route.id} route={route} elevation={elevation} />
          ))}
          {data.facilities
            .filter((f) => !DISPATCH_AREA_IDS.has(f.id))
            .map((facility) => (
              <FacilityCube key={facility.id} facility={facility} />
            ))}
          <PMDecisionGate position={pmGatePos} />
          {data.queueAreas.map((area) => (
            <QueueArea key={area.id} area={area} />
          ))}
          <TruckFleet
            trucks={mappedTrucks}
            routeCurves={routeCurves}
            timeSpeed={timeSpeed}
          />
          {labelsVisible &&
            data.overlays.map((overlay) => (
              <MapOverlayLabel key={overlay.id} overlay={overlay} data={data} />
            ))}
          <OrbitControls
            ref={controlsRef}
            makeDefault
            enableDamping
            dampingFactor={0.08}
            zoomSpeed={0.35}
            minDistance={data.camera.minZoom}
            maxDistance={data.camera.maxZoom}
            maxPolarAngle={Math.PI * 0.49}
            mouseButtons={{
              LEFT: THREE.MOUSE.ROTATE,
              MIDDLE: THREE.MOUSE.DOLLY,
              RIGHT: THREE.MOUSE.PAN,
            }}
          />
          <CameraFloor minY={groundFloorY} />
          <SceneCameraController
            data={data}
            activePresetId={activePresetId}
            controlsRef={controlsRef}
          />
          <PostFX />
        </Canvas>
      </div>
      <MapLegend />
    </div>
  );
}
