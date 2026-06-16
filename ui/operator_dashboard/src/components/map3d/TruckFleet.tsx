/**
 * TruckFleet — renders every truck and drives a single shared useFrame loop
 * so trucks on the same route can detect proximity and overtake by shifting
 * into a passing lane (lateral offset on the perpendicular axis).
 */
import { Suspense, useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Edges, Html, useGLTF } from '@react-three/drei';
import * as THREE from 'three';
import type { TruckFrame3D } from './map3dTypes';
import { getTruckHIColor, getCargoState, getDestinationLabel, CARGO_META, type CargoState } from './map3dUtils';
import truckModelUrl from '../../assets/models/caterpillar_797f_mining_truck_opt.glb?url';

/* ── constants ────────────────────────────────────── */
const TRUCK_W = 5;
const TRUCK_H = 3.5;
const TRUCK_D = 8;
const SPEED_FACTOR = 0.002;

/* ── 3D GLB model (shared with the PM worker app) ──── */
const DRACO_CDN = 'https://www.gstatic.com/draco/versioned/decoders/1.5.7/';
/** Only the first N trucks get the detailed GLB model; the rest fall back to a box. */
const MAX_3D_TRUCKS = 25;
/** Target length (world units) for the model's longest horizontal dimension.
 *  The GLB's length runs along its local Z (after a baked −90° X node rotation),
 *  which matches the fleet's forward (+Z), so the model aligns with travel. */
const MODEL_TARGET_LEN = 14;
/** Yaw offset to pick which end leads (0 = +Z nose). Tunable cosmetic only. */
const MODEL_YAW = 0;

useGLTF.preload(truckModelUrl, DRACO_CDN);

/* ── Box body (fallback while the GLB loads / beyond the 3D cap) ── */
function TruckBox({ color, isStopped }: { color: string; isStopped: boolean }) {
  return (
    <mesh castShadow receiveShadow>
      <boxGeometry args={[TRUCK_W, TRUCK_H, TRUCK_D]} />
      <meshStandardMaterial
        color={color}
        roughness={0.52}
        metalness={0.05}
        transparent={isStopped}
        opacity={isStopped ? 0.66 : 1}
      />
      <Edges color="#1E293B" />
    </mesh>
  );
}

/* ── GLB truck body, scaled to box footprint and tinted by HI ── */
function Truck3DModel({ color, isStopped }: { color: string; isStopped: boolean }) {
  const { scene } = useGLTF(truckModelUrl, DRACO_CDN) as unknown as { scene: THREE.Group };

  // Clone once per truck (geometry buffers are shared — cheap). Scale to the
  // box footprint and sit the wheels where the box bottom used to be.
  const model = useMemo(() => {
    const clone = scene.clone(true);

    const rawBox = new THREE.Box3().setFromObject(clone);
    const rawSize = rawBox.getSize(new THREE.Vector3());
    const horiz = Math.max(rawSize.x, rawSize.z) || 1;
    clone.scale.setScalar(MODEL_TARGET_LEN / horiz);

    const box = new THREE.Box3().setFromObject(clone);
    const center = box.getCenter(new THREE.Vector3());
    // Center horizontally; drop the model so its underside rests at -TRUCK_H/2
    // (matching the box, which the parent group lifts 0.8 above the route).
    clone.position.x -= center.x;
    clone.position.z -= center.z;
    clone.position.y -= box.min.y + TRUCK_H / 2;

    return clone;
  }, [scene]);

  // Tint the whole truck by HI status color (mirrors the box's solid color).
  const material = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color(color),
        metalness: 0.25,
        roughness: 0.55,
        side: THREE.DoubleSide,
        transparent: isStopped,
        opacity: isStopped ? 0.66 : 1,
      }),
    [color, isStopped],
  );

  useMemo(() => {
    model.traverse((child) => {
      const m = child as THREE.Mesh;
      if (m.isMesh) {
        m.material = material;
        m.castShadow = true;
        m.receiveShadow = true;
      }
    });
  }, [model, material]);

  return (
    <group rotation={[0, MODEL_YAW, 0]}>
      <primitive object={model} />
    </group>
  );
}

/** Progress-distance at which a truck starts shifting into the passing lane */
const OVERTAKE_RANGE = 0.08;
/** World-unit lateral shift when fully alongside another truck (overtaking) */
const LANE_WIDTH = 4;
/** Smoothing speed for the lane offset (higher = snappier) */
const LANE_LERP = 5;
/** Base lateral offset per travel direction → split each road into two lanes
 *  so oncoming trucks keep to opposite sides instead of overlapping. */
const LANE_SEP = 4.5;

/* ── Standby row positioning near PM bay ────────── */
const STANDBY_ROW_X_START = 550;
const STANDBY_ROW_X_SPACING = 12;
const STANDBY_ROW_Y = 9.4 + TRUCK_H / 2 + 0.8;
const STANDBY_ROW_Z = 50;

/* ── per-truck mutable state ─────────────────────── */
interface AnimState {
  progress: number;
  dir: number;        // +1 forward, −1 backward
  laneOffset: number; // current smoothed offset
  cargo: CargoState;  // dynamic load state
  target?: string;    // node the truck is currently heading to
  hi: number;         // dynamic health index (improves after PM)
}

/** Dynamic, render-facing truck state (mirrored from AnimState on events). */
type DynEntry = { cargo: CargoState; target?: string; hi: number };

/* Compound haul routes are named full_s{a|b|c}_{c1|c2|pm}: shovel → … → dest.
   progress 0 = shovel end, progress 1 = crusher / PM-bay end. */
const COMPOUND_RE = /^full_s([abc])_(c\d|pm)$/;
function routeEndpoints(routeId: string): { end0: string; end1: string } | null {
  const m = COMPOUND_RE.exec(routeId);
  if (!m) return null;
  return {
    end0: `shovel_${m[1]}`,
    end1: m[2] === 'pm' ? 'pm_bay' : `crusher_${m[2].slice(1)}`,
  };
}

/** Initial dynamic state — trucks start heading toward end1 (dir +1). */
function computeInitialDyn(truck: TruckFrame3D): DynEntry {
  const ep = routeEndpoints(truck.route_id);
  if (!ep) return { cargo: getCargoState(truck), target: truck.target_node, hi: truck.truck_hi };
  return {
    cargo: ep.end1 === 'pm_bay' ? 'pm' : 'loaded', // loaded out of the shovel (or PM-bound)
    target: ep.end1,
    hi: truck.truck_hi,
  };
}

/** Transition the truck at an endpoint. Returns true if dynamic state changed. */
function applyArrival(routeId: string, s: AnimState, end: 'end0' | 'end1'): boolean {
  const ep = routeEndpoints(routeId);
  if (!ep) return false;
  if (end === 'end1') {
    // Arrived at the crusher / PM bay → now empty, heading back to the shovel.
    if (ep.end1 === 'pm_bay') s.hi = Math.min(1, s.hi + 0.3); // PM done → health restored
    s.cargo = 'empty';
    s.target = ep.end0;
  } else {
    // Arrived back at the shovel → reload (or head out for PM), bound for end1.
    s.cargo = ep.end1 === 'pm_bay' ? 'pm' : 'loaded';
    s.target = ep.end1;
  }
  return true;
}

/* ── props ────────────────────────────────────────── */
type TruckFleetProps = {
  trucks: TruckFrame3D[];
  routeCurves: Map<string, THREE.CatmullRomCurve3>;
  timeSpeed?: number;
};

export default function TruckFleet({ trucks, routeCurves, timeSpeed = 1 }: TruckFleetProps) {
  const groupRefs = useRef(new Map<string, THREE.Group>());
  const animStates = useRef(new Map<string, AnimState>());

  // Lazy-init state for any truck that doesn't have one yet
  for (const t of trucks) {
    if (!animStates.current.has(t.truck_id)) {
      const d = computeInitialDyn(t);
      animStates.current.set(t.truck_id, {
        progress: t.route_progress,
        dir: 1,
        laneOffset: 0,
        cargo: d.cargo,
        target: d.target,
        hi: d.hi,
      });
    }
  }

  // Render-facing dynamic state (label / load / HI). Updated only on endpoint
  // events, so labels & colors refresh when a truck heads to a new destination.
  const [dynState, setDynState] = useState<Record<string, DynEntry>>(() => {
    const o: Record<string, DynEntry> = {};
    for (const t of trucks) o[t.truck_id] = computeInitialDyn(t);
    return o;
  });

  useFrame((_, delta) => {
    const states = animStates.current;
    const groups = groupRefs.current;

    /* ── 1. advance progress + endpoint transitions ─ */
    let dynChanged = false;
    for (const t of trucks) {
      if (t.speed <= 0) continue;
      const s = states.get(t.truck_id);
      if (!s) continue;

      s.progress += t.speed * SPEED_FACTOR * delta * s.dir * timeSpeed;

      if (s.progress >= 1) {
        s.progress = 1; s.dir = -1;
        if (applyArrival(t.route_id, s, 'end1')) dynChanged = true;
      } else if (s.progress <= 0) {
        s.progress = 0; s.dir = 1;
        if (applyArrival(t.route_id, s, 'end0')) dynChanged = true;
      }
    }
    if (dynChanged) {
      const next: Record<string, DynEntry> = {};
      for (const [id, st] of states) next[id] = { cargo: st.cargo, target: st.target, hi: st.hi };
      setDynState(next);
    }

    /* ── 2. group trucks by route ────────────────── */
    const byRoute = new Map<string, TruckFrame3D[]>();
    for (const t of trucks) {
      let arr = byRoute.get(t.route_id);
      if (!arr) { arr = []; byRoute.set(t.route_id, arr); }
      arr.push(t);
    }

    /* ── 3. compute target lane offsets (overtake) ─ */
    const targetOffset = new Map<string, number>();

    for (const [, routeTrucks] of byRoute) {
      if (routeTrucks.length < 2) continue;

      for (const a of routeTrucks) {
        if (a.speed <= 0) continue;
        const sa = states.get(a.truck_id);
        if (!sa) continue;

        let best = 0; // largest offset needed

        for (const b of routeTrucks) {
          if (a.truck_id === b.truck_id) continue;
          const sb = states.get(b.truck_id);
          if (!sb) continue;
          // Only overtake trucks heading the SAME way (opposing trucks are
          // already separated onto the other lane).
          if (sb.dir !== sa.dir) continue;

          // signed gap: positive → b is ahead of a in a's travel direction
          const gap = (sb.progress - sa.progress) * sa.dir;

          if (gap > 0 && gap < OVERTAKE_RANGE && a.speed > b.speed) {
            // intensity: 1 when very close, 0 at threshold
            const t = 1 - gap / OVERTAKE_RANGE;
            // bell-curve shape so offset rises, peaks, then falls as a passes b
            const offset = LANE_WIDTH * Math.sin(t * Math.PI);
            if (offset > best) best = offset;
          }
        }

        targetOffset.set(a.truck_id, best);
      }
    }

    /* ── 4. Position STANDBY trucks in a row near PM bay ── */
    let standbyIdx = 0;
    const standbyIds = new Set<string>();
    for (const t of trucks) {
      if (t.truck_state === 'STANDBY') {
        standbyIds.add(t.truck_id);
        const g = groups.get(t.truck_id);
        if (g) {
          g.position.set(
            STANDBY_ROW_X_START + standbyIdx * STANDBY_ROW_X_SPACING,
            STANDBY_ROW_Y,
            STANDBY_ROW_Z,
          );
          g.rotation.y = 0;
          standbyIdx++;
        }
      }
    }

    /* ── 5. apply positions with smoothed lane offset */
    for (const t of trucks) {
      if (standbyIds.has(t.truck_id)) continue; // already positioned

      const g = groups.get(t.truck_id);
      const s = states.get(t.truck_id);
      if (!g || !s) continue;

      // Directional lane: keep right per travel direction, plus any overtake
      // shift (pushed further out on the truck's own side).
      const dirLane = s.dir >= 0 ? LANE_SEP : -LANE_SEP;
      const overtake = targetOffset.get(t.truck_id) ?? 0;
      const target = dirLane + (s.dir >= 0 ? overtake : -overtake);
      s.laneOffset += (target - s.laneOffset) * Math.min(1, delta * LANE_LERP);

      const curve = routeCurves.get(t.route_id);

      if (curve && t.speed > 0) {
        const pt = curve.getPoint(s.progress);
        const tan = curve.getTangent(s.progress);

        // perpendicular direction (XZ plane)
        const perpX = -tan.z;
        const perpZ = tan.x;
        const pLen = Math.sqrt(perpX * perpX + perpZ * perpZ) || 1;

        g.position.set(
          pt.x + (perpX / pLen) * s.laneOffset,
          pt.y + TRUCK_H / 2 + 0.8,
          pt.z + (perpZ / pLen) * s.laneOffset,
        );

        // face travel direction
        const fwd = s.dir >= 0 ? tan : tan.clone().negate();
        g.rotation.y = Math.atan2(fwd.x, fwd.z);
      }
    }
  });

  return (
    <>
      {trucks.map((truck, idx) => {
        const dyn = dynState[truck.truck_id] || computeInitialDyn(truck);
        const hi = dyn.hi;
        const color = getTruckHIColor(hi, truck.truck_state);
        const isStopped = truck.speed <= 0;
        const use3DModel = idx < MAX_3D_TRUCKS;
        const cargo = dyn.cargo;
        const cargoMeta = CARGO_META[cargo];
        const hiPct = Math.round(hi * 100);
        const dest = getDestinationLabel(dyn.target);

        return (
          <group
            key={truck.truck_id}
            ref={(el: THREE.Group | null) => {
              if (el) groupRefs.current.set(truck.truck_id, el);
            }}
            position={[
              truck.position.x,
              truck.position.y + TRUCK_H / 2 + 0.8,
              truck.position.z,
            ]}
            rotation={[0, truck.rotation_y || 0, 0]}
          >
            {/* Selection ring */}
            {truck.selected && (
              <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -TRUCK_H / 2 + 0.1, 0]}>
                <torusGeometry args={[TRUCK_D * 0.85, 0.6, 8, 56]} />
                <meshBasicMaterial color="#DC2626" transparent opacity={0.82} />
              </mesh>
            )}

            {/* PM-due warning ring */}
            {truck.pm_due_hours <= 12 && !truck.selected && (
              <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -TRUCK_H / 2 + 0.1, 0]}>
                <torusGeometry args={[TRUCK_D * 0.75, 0.45, 8, 44]} />
                <meshBasicMaterial color="#F59E0B" transparent opacity={0.7} />
              </mesh>
            )}

            {/* Truck body: detailed GLB model for the first N trucks, box otherwise */}
            {use3DModel ? (
              <Suspense fallback={<TruckBox color={color} isStopped={isStopped} />}>
                <Truck3DModel color={color} isStopped={isStopped} />
              </Suspense>
            ) : (
              <TruckBox color={color} isStopped={isStopped} />
            )}

            {/* Loaded → dark ore block on the tray */}
            {cargo === 'loaded' && (
              <mesh position={[0, TRUCK_H / 2 + 0.9, -0.4]}>
                <boxGeometry args={[TRUCK_W - 1, 1.8, TRUCK_D - 2.4]} />
                <meshStandardMaterial color="#3A2E25" roughness={0.95} />
              </mesh>
            )}

            {/* PM-bound → purple wrench marker */}
            {cargo === 'pm' && (
              <mesh position={[0, TRUCK_H / 2 + 1.8, 0]}>
                <cylinderGeometry args={[0, 1.4, 2.6, 4]} />
                <meshStandardMaterial color="#7C3AED" emissive="#7C3AED" emissiveIntensity={0.35} />
              </mesh>
            )}

            {/* Direction arrow at the front (points along travel) */}
            {!isStopped && (
              <mesh position={[0, 0, TRUCK_D / 2 + 1.3]} rotation={[Math.PI / 2, 0, 0]}>
                <coneGeometry args={[1.3, 2.6, 8]} />
                <meshBasicMaterial color={color} />
              </mesh>
            )}

            {/* Floating label: ID → destination + HI + load state */}
            <Html position={[0, TRUCK_H / 2 + 3.6, 0]} center distanceFactor={120} occlude={false} style={{ pointerEvents: 'none' }}>
              <div style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2,
                fontFamily: 'system-ui, sans-serif', whiteSpace: 'nowrap',
              }}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 4,
                  background: 'rgba(15,23,42,0.86)', color: '#fff',
                  padding: '2px 7px', borderRadius: 5, fontSize: 11, fontWeight: 700,
                }}>
                  <span>{truck.truck_id}</span>
                  <span style={{ opacity: 0.6 }}>→</span>
                  <span style={{ fontWeight: 600 }}>{dest}</span>
                </div>
                <div style={{ display: 'flex', gap: 3 }}>
                  <span style={{
                    background: color, color: '#fff', padding: '1px 5px',
                    borderRadius: 4, fontSize: 9, fontWeight: 700,
                  }}>HI {hiPct}%</span>
                  <span style={{
                    background: cargoMeta.color, color: cargo === 'empty' ? '#1E293B' : '#fff',
                    padding: '1px 5px', borderRadius: 4, fontSize: 9, fontWeight: 700,
                  }}>{cargoMeta.label}</span>
                </div>
              </div>
            </Html>
          </group>
        );
      })}
    </>
  );
}
