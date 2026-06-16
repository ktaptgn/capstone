import { Suspense, useMemo } from 'react';
import { useLoader } from '@react-three/fiber';
import { Edges, Html } from '@react-three/drei';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import * as THREE from 'three';
import type { Facility3D } from './map3dTypes';
import {
  getCubeSize,
  getFacilityAccentColor,
  getFacilityColor,
  getQueueRatioColor,
} from './map3dUtils';
import shovelModelUrl from '../../assets/models/shovel.obj?url';
import crusherModelUrl from '../../assets/models/crusher.obj?url';
import pmBayModelUrl from '../../assets/models/pm_bay.obj?url';

type FacilityCubeProps = {
  facility: Facility3D;
  groundY?: number;
};

const FACILITY_SHORT_NAMES: Record<string, string> = {
  shovel: 'Shovel',
  crusher: 'Crusher',
  pm_bay: 'PM Bay',
};

const FACILITY_OBJ_URLS: Record<string, string> = {
  shovel: shovelModelUrl,
  crusher: crusherModelUrl,
  pm_bay: pmBayModelUrl,
};

const MODEL_GROUND_OFFSETS: Record<string, number> = {
  shovel: -0.35,
  crusher: 0,
  pm_bay: 0,
};

function FacilityBox({
  cubeSize,
  bodyColor,
  accentColor,
}: {
  cubeSize: number;
  bodyColor: string;
  accentColor: string;
}) {
  return (
    <mesh position={[0, cubeSize / 2, 0]} castShadow receiveShadow>
      <boxGeometry args={[cubeSize, cubeSize, cubeSize]} />
      <meshStandardMaterial
        color={bodyColor}
        roughness={0.55}
        metalness={0.18}
        envMapIntensity={0.6}
        emissive={accentColor}
        emissiveIntensity={0.025}
      />
      <Edges color={accentColor} />
    </mesh>
  );
}

function FacilityObjModel({
  facility,
  bodyColor,
  accentColor,
  cubeSize,
}: {
  facility: Facility3D;
  bodyColor: string;
  accentColor: string;
  cubeSize: number;
}) {
  const modelUrl = FACILITY_OBJ_URLS[facility.type];
  const source = useLoader(OBJLoader, modelUrl);

  const model = useMemo(() => {
    const clone = source.clone(true);
    const sourceBox = new THREE.Box3().setFromObject(clone);
    const sourceSize = sourceBox.getSize(new THREE.Vector3());
    const targetWidth = facility.size?.width ?? cubeSize;
    const targetHeight = facility.size?.height ?? cubeSize;
    const targetDepth = facility.size?.depth ?? cubeSize;
    const scale = Math.min(
      targetWidth / Math.max(sourceSize.x, 1),
      targetHeight / Math.max(sourceSize.y, 1),
      targetDepth / Math.max(sourceSize.z, 1),
    );

    clone.scale.setScalar(scale);
    const scaledBox = new THREE.Box3().setFromObject(clone);
    const center = scaledBox.getCenter(new THREE.Vector3());
    clone.position.x -= center.x;
    clone.position.z -= center.z;
    clone.position.y -= scaledBox.min.y;
    clone.position.y += MODEL_GROUND_OFFSETS[facility.type] ?? 0;

    const material = new THREE.MeshStandardMaterial({
      color: new THREE.Color(bodyColor),
      roughness: 0.55,
      metalness: 0.18,
      envMapIntensity: 0.6,
      emissive: new THREE.Color(accentColor),
      emissiveIntensity: 0.025,
      side: THREE.DoubleSide,
    });

    clone.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.castShadow = true;
        child.receiveShadow = true;
        child.material = material;
      }
    });

    return clone;
  }, [source, facility.size?.width, facility.size?.height, facility.size?.depth, cubeSize, bodyColor, accentColor]);

  return <primitive object={model} />;
}

export default function FacilityCube({ facility, groundY }: FacilityCubeProps) {
  const cubeSize = getCubeSize(facility);
  const accentColor = getFacilityAccentColor(facility.status, facility.riskLevel);
  const bodyColor = getFacilityColor(facility.status, facility.riskLevel);
  const modelUrl = FACILITY_OBJ_URLS[facility.type];
  const anchorY =
    facility.type === 'shovel' && typeof groundY === 'number'
      ? groundY
      : facility.position.y;
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
        anchorY,
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

      {modelUrl ? (
        <Suspense
          fallback={
            <FacilityBox
              cubeSize={cubeSize}
              bodyColor={bodyColor}
              accentColor={accentColor}
            />
          }
        >
          <FacilityObjModel
            facility={facility}
            bodyColor={bodyColor}
            accentColor={accentColor}
            cubeSize={cubeSize}
          />
        </Suspense>
      ) : (
        <FacilityBox
          cubeSize={cubeSize}
          bodyColor={bodyColor}
          accentColor={accentColor}
        />
      )}

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
