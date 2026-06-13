import { Edges, Html } from '@react-three/drei';
import type { Facility3D } from './map3dTypes';
import {
  getCubeSize,
  getFacilityAccentColor,
  getFacilityColor,
  getQueueRatioColor,
} from './map3dUtils';

type FacilityCubeProps = {
  facility: Facility3D;
};

const FACILITY_SHORT_NAMES: Record<string, string> = {
  shovel: 'Shovel',
  crusher: 'Crusher',
  pm_bay: 'PM Bay',
};

export default function FacilityCube({ facility }: FacilityCubeProps) {
  const cubeSize = getCubeSize(facility);
  const accentColor = getFacilityAccentColor(facility.status, facility.riskLevel);
  const bodyColor = getFacilityColor(facility.status, facility.riskLevel);
  const queueRatio =
    facility.capacity && facility.capacity > 0
      ? Math.min((facility.queue ?? 0) / facility.capacity, 1)
      : 0;
  const queueColor = getQueueRatioColor(queueRatio);
  // Floor indicator radius — capped so overlay never exceeds it
  const queueRadius = cubeSize * 1.5;
  const hasQueue = (facility.queue ?? 0) > 0 || facility.type === 'shovel';
  const shortName = FACILITY_SHORT_NAMES[facility.type] || facility.name;

  return (
    <group
      position={[
        facility.position.x,
        facility.position.y,
        facility.position.z,
      ]}
      rotation={[
        facility.rotation?.x || 0,
        facility.rotation?.y || 0,
        facility.rotation?.z || 0,
      ]}
    >
      {/* Floor indicator circle — semi-transparent */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.2, 0]}>
        <circleGeometry args={[queueRadius, 48]} />
        <meshBasicMaterial color={queueColor} transparent opacity={0.1} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.25, 0]}>
        <ringGeometry args={[queueRadius - 0.5, queueRadius, 48]} />
        <meshBasicMaterial color={queueColor} transparent opacity={0.35} />
      </mesh>

      {/* Facility cube */}
      <mesh position={[0, cubeSize / 2, 0]}>
        <boxGeometry args={[cubeSize, cubeSize, cubeSize]} />
        <meshStandardMaterial
          color={bodyColor}
          roughness={0.78}
          metalness={0.02}
          emissive={accentColor}
          emissiveIntensity={0.02}
        />
        <Edges color={accentColor} />
      </mesh>

      {/* Compact queue status label — semi-transparent, small */}
      {hasQueue && (
        <Html position={[0, cubeSize + 3, 0]} center style={{ pointerEvents: 'none' }}>
          <div
            style={{
              padding: '1px 4px',
              borderRadius: 3,
              background: 'rgba(255,255,255,0.68)',
              border: `1px solid ${queueColor}40`,
              color: '#334155',
              fontSize: 7,
              fontWeight: 700,
              whiteSpace: 'nowrap',
              lineHeight: 1.3,
              textAlign: 'center',
            }}
          >
            <span style={{ color: accentColor }}>{shortName}</span>
            <br />
            Q: {facility.queue ?? 0}/{facility.capacity ?? '-'}
          </div>
        </Html>
      )}
    </group>
  );
}
