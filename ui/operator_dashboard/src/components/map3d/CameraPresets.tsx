import { useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import type {
  C5OperationMap3DData,
  CameraConfig3D,
  CameraPreset3D,
  Vec3,
} from './map3dTypes';

type OrbitControlsLike = {
  target: {
    set: (x: number, y: number, z: number) => void;
  };
  update: () => void;
};

type SceneCameraControllerProps = {
  data: C5OperationMap3DData;
  activePresetId: string;
  controlsRef: React.MutableRefObject<OrbitControlsLike | null>;
};

type CameraPresetsProps = {
  camera: CameraConfig3D;
  activePresetId: string;
  onSelect: (presetId: string) => void;
};

function resolveTarget(preset: CameraPreset3D, data: C5OperationMap3DData): Vec3 {
  if (!preset.followTruckId) return preset.target;
  const targetTruck = data.truckFrames.find(
    (truck) => truck.truck_id === preset.followTruckId,
  );
  return targetTruck?.position || preset.target;
}

export function SceneCameraController({
  data,
  activePresetId,
  controlsRef,
}: SceneCameraControllerProps) {
  const { camera } = useThree();

  useEffect(() => {
    const preset =
      data.camera.presets.find((item) => item.id === activePresetId)
      || data.camera.presets[0];
    if (!preset) return;

    // For the first preset (overview / full mine), allow free orbit — skip snapping
    const isOverview = preset.id === (data.camera.presets[0]?.id || 'overview');
    if (isOverview) return;

    const target = resolveTarget(preset, data);
    camera.position.set(preset.position.x, preset.position.y, preset.position.z);
    camera.lookAt(target.x, target.y, target.z);
    camera.updateProjectionMatrix();
    controlsRef.current?.target.set(target.x, target.y, target.z);
    controlsRef.current?.update();
  }, [activePresetId, camera, controlsRef, data]);

  return null;
}

export default function CameraPresets({
  camera,
  activePresetId,
  onSelect,
}: CameraPresetsProps) {
  return (
    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
      {camera.presets.map((preset) => {
        const isActive = preset.id === activePresetId;
        return (
          <button
            key={preset.id}
            type="button"
            onClick={() => onSelect(preset.id)}
            style={{
              border: `1px solid ${isActive ? '#8A4931' : '#CBD5E1'}`,
              background: isActive ? '#F3E7E2' : '#FFFFFF',
              color: isActive ? '#7C2D12' : '#334155',
              borderRadius: 6,
              padding: '5px 9px',
              fontSize: 11,
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            {preset.label}
          </button>
        );
      })}
    </div>
  );
}
