import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Edges } from '@react-three/drei';
import * as THREE from 'three';
import type { TruckFrame3D } from './map3dTypes';
import { getTruckHIColor } from './map3dUtils';

type TruckHemisphereProps = {
  truck: TruckFrame3D;
  statusColorMap: Record<string, string>;
  routeCurve?: THREE.CatmullRomCurve3;
};

const TRUCK_W = 5;
const TRUCK_H = 3.5;
const TRUCK_D = 8;

/** Normalised speed factor — at speed=30 the truck takes ~17s to traverse a full route */
const SPEED_FACTOR = 0.002;

export default function TruckHemisphere({
  truck,
  routeCurve,
}: TruckHemisphereProps) {
  const color = getTruckHIColor(truck.truck_hi, truck.truck_state);
  const isStopped = truck.speed <= 0;

  const groupRef = useRef<THREE.Group>(null);
  const progressRef = useRef(truck.route_progress);
  const dirRef = useRef(1);

  useFrame((_, delta) => {
    if (!routeCurve || !groupRef.current || isStopped) return;

    // Advance progress along route
    const step = truck.speed * SPEED_FACTOR * delta;
    progressRef.current += step * dirRef.current;

    // Bounce at ends
    if (progressRef.current >= 1) {
      progressRef.current = 1;
      dirRef.current = -1;
    } else if (progressRef.current <= 0) {
      progressRef.current = 0;
      dirRef.current = 1;
    }

    // Sample position & tangent from curve
    const point = routeCurve.getPoint(progressRef.current);
    const tangent = routeCurve.getTangent(progressRef.current);

    groupRef.current.position.set(
      point.x,
      point.y + TRUCK_H / 2 + 0.8,
      point.z,
    );

    // Face movement direction
    const fwd = dirRef.current >= 0 ? tangent : tangent.clone().negate();
    groupRef.current.rotation.y = Math.atan2(fwd.x, fwd.z);
  });

  return (
    <group
      ref={groupRef}
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
}
