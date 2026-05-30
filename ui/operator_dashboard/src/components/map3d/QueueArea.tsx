import { Html } from '@react-three/drei';
import type { QueueArea3D } from './map3dTypes';
import { getQueueRatioColor } from './map3dUtils';

type QueueAreaProps = {
  area: QueueArea3D;
};

export default function QueueArea({ area }: QueueAreaProps) {
  const ratio = area.capacity > 0 ? area.liveCount / area.capacity : 0;
  const color = getQueueRatioColor(ratio);
  const radius = Math.max(area.size.width, area.size.depth) * 0.5;

  return (
    <group position={[area.position.x, area.position.y + 0.3, area.position.z]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[radius, 48]} />
        <meshBasicMaterial color={color} transparent opacity={0.14} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.05, 0]}>
        <ringGeometry args={[radius - 0.8, radius, 48]} />
        <meshBasicMaterial color={color} transparent opacity={0.5} />
      </mesh>
      <Html position={[0, 5, 0]} center style={{ pointerEvents: 'none' }}>
        <div
          style={{
            padding: '2px 5px',
            borderRadius: 3,
            background: 'rgba(255,255,255,0.72)',
            border: `1px solid ${color}40`,
            color: '#334155',
            fontSize: 8,
            fontWeight: 700,
            whiteSpace: 'nowrap',
            boxShadow: '0 1px 4px rgba(15,23,42,0.08)',
          }}
        >
          {area.label.replace(/Dump Queue|Queue/g, 'Q')} {area.liveCount}/{area.capacity}
        </div>
      </Html>
    </group>
  );
}
