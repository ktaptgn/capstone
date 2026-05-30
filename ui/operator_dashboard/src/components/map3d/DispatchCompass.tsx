import { useMemo } from 'react';
import * as THREE from 'three';

type DispatchCompassProps = {
  position: [number, number, number];
  radius?: number;
};

export default function DispatchCompass({
  position,
  radius = 36,
}: DispatchCompassProps) {
  const starGeo = useMemo(() => {
    const verts: number[] = [];

    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2 - Math.PI / 2;
      const isCardinal = i % 2 === 0;
      const len = isCardinal ? radius * 0.82 : radius * 0.52;
      const hw = isCardinal ? radius * 0.07 : radius * 0.055;

      const c = Math.cos(angle);
      const s = Math.sin(angle);
      const pc = Math.cos(angle + Math.PI / 2);
      const ps = Math.sin(angle + Math.PI / 2);

      const tipX = c * len;
      const tipZ = s * len;
      const lx = pc * hw;
      const lz = ps * hw;
      const rx = -pc * hw;
      const rz = -ps * hw;
      const cx = -c * radius * 0.06;
      const cz = -s * radius * 0.06;

      verts.push(cx, 0, cz, lx, 0, lz, tipX, 0, tipZ);
      verts.push(cx, 0, cz, tipX, 0, tipZ, rx, 0, rz);
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute(
      'position',
      new THREE.Float32BufferAttribute(verts, 3),
    );
    return geo;
  }, [radius]);

  const tickGeo = useMemo(() => {
    const verts: number[] = [];
    const count = 36;

    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const isMajor = i % 9 === 0;
      const isMid = i % 3 === 0 && !isMajor;
      const tl = isMajor
        ? radius * 0.07
        : isMid
          ? radius * 0.045
          : radius * 0.025;
      const inner = radius * 0.88;

      const c = Math.cos(angle);
      const s = Math.sin(angle);
      const pc = Math.cos(angle + Math.PI / 2);
      const ps = Math.sin(angle + Math.PI / 2);
      const tw = isMajor ? 0.4 : 0.25;

      const x1 = c * inner;
      const z1 = s * inner;
      const x2 = c * (inner + tl);
      const z2 = s * (inner + tl);

      verts.push(
        x1 - pc * tw, 0, z1 - ps * tw,
        x1 + pc * tw, 0, z1 + ps * tw,
        x2 + pc * tw, 0, z2 + ps * tw,
      );
      verts.push(
        x1 - pc * tw, 0, z1 - ps * tw,
        x2 + pc * tw, 0, z2 + ps * tw,
        x2 - pc * tw, 0, z2 - ps * tw,
      );
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute(
      'position',
      new THREE.Float32BufferAttribute(verts, 3),
    );
    return geo;
  }, [radius]);

  return (
    <group position={position} renderOrder={10}>
      {/* Outer glow ring — gives a soft border separating compass from terrain */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.05, 0]} renderOrder={10}>
        <ringGeometry args={[radius * 0.96, radius * 1.08, 64]} />
        <meshBasicMaterial color="#D07E61" transparent opacity={0.18} depthWrite={false} />
      </mesh>

      {/* Base disc — slightly more opaque for contrast */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.1, 0]} renderOrder={11}>
        <circleGeometry args={[radius, 64]} />
        <meshBasicMaterial color="#D07E61" transparent opacity={0.3} depthWrite={false} />
      </mesh>

      {/* Outer ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.15, 0]} renderOrder={12}>
        <ringGeometry args={[radius * 0.92, radius * 0.96, 64]} />
        <meshBasicMaterial color="#4D221B" transparent opacity={0.8} depthWrite={false} />
      </mesh>

      {/* Second ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.15, 0]} renderOrder={12}>
        <ringGeometry args={[radius * 0.86, radius * 0.88, 64]} />
        <meshBasicMaterial color="#4D221B" transparent opacity={0.7} depthWrite={false} />
      </mesh>

      {/* Inner ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.15, 0]} renderOrder={12}>
        <ringGeometry args={[radius * 0.14, radius * 0.17, 32]} />
        <meshBasicMaterial color="#4D221B" transparent opacity={0.85} depthWrite={false} />
      </mesh>

      {/* Center dot */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.16, 0]} renderOrder={13}>
        <circleGeometry args={[radius * 0.05, 16]} />
        <meshBasicMaterial color="#1E293B" transparent opacity={0.9} depthWrite={false} />
      </mesh>

      {/* Star */}
      <mesh geometry={starGeo} position={[0, 0.2, 0]} renderOrder={14}>
        <meshBasicMaterial
          color="#1E293B"
          transparent
          opacity={0.9}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Tick marks */}
      <mesh geometry={tickGeo} position={[0, 0.18, 0]} renderOrder={13}>
        <meshBasicMaterial
          color="#4D221B"
          transparent
          opacity={0.72}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Transparent dome */}
      <mesh position={[0, 0.3, 0]} renderOrder={15}>
        <sphereGeometry
          args={[radius * 0.7, 32, 24, 0, Math.PI * 2, 0, Math.PI / 2]}
        />
        <meshStandardMaterial
          color="#D07E61"
          transparent
          opacity={0.08}
          roughness={0.3}
          metalness={0.1}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Dome wireframe */}
      <mesh position={[0, 0.3, 0]} renderOrder={15}>
        <sphereGeometry
          args={[radius * 0.71, 16, 12, 0, Math.PI * 2, 0, Math.PI / 2]}
        />
        <meshBasicMaterial
          color="#B35F44"
          transparent
          opacity={0.14}
          wireframe
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}
