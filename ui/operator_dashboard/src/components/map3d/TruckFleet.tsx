/**
 * TruckFleet — renders every truck and drives a single shared useFrame loop
 * so trucks on the same route can detect proximity and overtake by shifting
 * into a passing lane (lateral offset on the perpendicular axis).
 */
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Edges } from '@react-three/drei';
import * as THREE from 'three';
import type { TruckFrame3D } from './map3dTypes';
import { getTruckHIColor } from './map3dUtils';

/* ── constants ────────────────────────────────────── */
const TRUCK_W = 5;
const TRUCK_H = 3.5;
const TRUCK_D = 8;
const SPEED_FACTOR = 0.002;

/** Progress-distance at which a truck starts shifting into the passing lane */
const OVERTAKE_RANGE = 0.08;
/** World-unit lateral shift when fully alongside another truck */
const LANE_WIDTH = 9;
/** Smoothing speed for the lane offset (higher = snappier) */
const LANE_LERP = 5;

/* ── Standby row positioning near PM bay ────────── */
const STANDBY_ROW_X_START = 550;
const STANDBY_ROW_X_SPACING = 12;
const STANDBY_ROW_Y = 9.4 + TRUCK_H / 2 + 0.8;
const STANDBY_ROW_Z = 50;

/* ── per-truck mutable state ─────────────────────── */
interface AnimState {
  progress: number;
  dir: number;       // +1 forward, −1 backward
  laneOffset: number; // current smoothed offset
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
      animStates.current.set(t.truck_id, {
        progress: t.route_progress,
        dir: 1,
        laneOffset: 0,
      });
    }
  }

  useFrame((_, delta) => {
    const states = animStates.current;
    const groups = groupRefs.current;

    /* ── 1. advance progress ─────────────────────── */
    for (const t of trucks) {
      if (t.speed <= 0) continue;
      const s = states.get(t.truck_id);
      if (!s) continue;

      s.progress += t.speed * SPEED_FACTOR * delta * s.dir * timeSpeed;

      if (s.progress >= 1) { s.progress = 1; s.dir = -1; }
      else if (s.progress <= 0) { s.progress = 0; s.dir = 1; }
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

      // smooth lane offset toward target
      const target = targetOffset.get(t.truck_id) ?? 0;
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
      {trucks.map((truck) => {
        const color = getTruckHIColor(truck.truck_hi, truck.truck_state);
        const isStopped = truck.speed <= 0;

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

            {/* Truck box body */}
            <mesh>
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
          </group>
        );
      })}
    </>
  );
}
