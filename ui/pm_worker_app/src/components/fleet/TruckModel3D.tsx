import { Suspense, useRef, useMemo, useState, useEffect, Component, type ReactNode } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF, Html } from '@react-three/drei';
import * as THREE from 'three';
import { getHIColor } from '../../utils/statusColors';
import type { TireComponent } from '../../policies/types';

import modelUrl from '../../assets/models/caterpillar_797f_mining_truck_opt.glb?url';
const MODEL_PATH = modelUrl;
const DRACO_CDN = 'https://www.gstatic.com/draco/versioned/decoders/1.5.7/';

function TruckScene({ tires }: { tires: TireComponent[] }) {
  const gltf = useGLTF(MODEL_PATH, DRACO_CDN);
  const groupRef = useRef<THREE.Group>(null);
  const { camera } = useThree();
  const cameraSet = useRef(false);

  const prepared = useMemo(() => {
    const clone = gltf.scene.clone(true);
    const material = new THREE.MeshStandardMaterial({
      color: 0xcccccc,
      metalness: 0.3,
      roughness: 0.6,
      side: THREE.DoubleSide,
    });
    clone.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.material = material;
      }
    });

    const box = new THREE.Box3().setFromObject(clone);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    clone.position.sub(center);

    return { clone, size, center };
  }, [gltf]);

  useEffect(() => {
    if (cameraSet.current) return;
    const maxDim = Math.max(prepared.size.x, prepared.size.y, prepared.size.z);
    if (maxDim === 0) return;
    const fov = (camera as THREE.PerspectiveCamera).fov * (Math.PI / 180);
    const dist = maxDim / (2 * Math.tan(fov / 2)) * 1.6;
    // 바닥 아래에서 위를 올려다보는 시점 (underside view)
    camera.position.set(dist * 0.2, -dist * 0.45, dist * 0.55);
    camera.lookAt(0, 0, 0);
    (camera as THREE.PerspectiveCamera).near = 0.1;
    (camera as THREE.PerspectiveCamera).far = dist * 5;
    camera.updateProjectionMatrix();
    cameraSet.current = true;
  }, [prepared, camera]);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.15;
    }
  });

  const overlayPositions = useMemo(() => {
    const hw = prepared.size.x * 0.48;
    const hd = prepared.size.z * 0.35;
    const bottomY = -prepared.size.y * 0.38;
    return {
      FL: new THREE.Vector3(-hw, bottomY, hd),
      FR: new THREE.Vector3(hw, bottomY, hd),
      RL: new THREE.Vector3(-hw, bottomY, -hd),
      RR: new THREE.Vector3(hw, bottomY, -hd),
    };
  }, [prepared]);

  return (
    <group ref={groupRef}>
      <primitive object={prepared.clone} />
      {tires.map(tire => {
        const pos = overlayPositions[tire.position as keyof typeof overlayPositions];
        if (!pos) return null;
        const color = getHIColor(tire.healthIndex);
        return (
          <group key={tire.id} position={pos}>
            <mesh rotation={[-Math.PI / 2, 0, 0]}>
              <ringGeometry args={[0.6, 0.9, 32]} />
              <meshBasicMaterial color={color} transparent opacity={0.8} side={THREE.DoubleSide} />
            </mesh>
            <Html center distanceFactor={10} style={{ pointerEvents: 'none' }}>
              <div style={{ background: color, color: '#fff', padding: '2px 6px', borderRadius: 4, fontSize: 10, fontWeight: 700, whiteSpace: 'nowrap' }}>
                {tire.position} {tire.healthIndex}%
              </div>
            </Html>
          </group>
        );
      })}
    </group>
  );
}

function LoadingSpinner() {
  return (
    <Html center>
      <div style={{ color: '#8A4931', fontSize: 12, fontWeight: 600, textAlign: 'center' }}>
        <div style={{ width: 28, height: 28, border: '3px solid #F3E7E2', borderTopColor: '#8A4931', borderRadius: '50%', margin: '0 auto 8px', animation: 'spin 1s linear infinite' }} />
        Loading 3D Model...
      </div>
    </Html>
  );
}

interface EBProps { fallback: ReactNode; children: ReactNode }
interface EBState { hasError: boolean }

class GLTFErrorBoundary extends Component<EBProps, EBState> {
  state: EBState = { hasError: false };
  static getDerivedStateFromError(): EBState {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) return this.props.fallback;
    return this.props.children;
  }
}

interface TruckModel3DProps {
  tires: TireComponent[];
  onError?: () => void;
}

export default function TruckModel3D({ tires, onError }: TruckModel3DProps) {
  const [renderKey, setRenderKey] = useState(0);
  const [status, setStatus] = useState<'ok' | 'error'>('ok');

  const errorFallback = (
    <div className="flex flex-col items-center justify-center h-full gap-2">
      <span className="text-xs text-text-sub">3D model load failed</span>
      <button
        onClick={() => { setRenderKey(k => k + 1); setStatus('ok'); }}
        className="text-[10px] px-3 py-1 rounded-full bg-sanguine-soft text-sanguine hover:bg-sanguine hover:text-white transition-colors"
      >
        Retry
      </button>
    </div>
  );

  if (status === 'error') {
    return (
      <div className="rounded-lg overflow-hidden flex items-center justify-center" style={{ height: 220, background: 'linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%)' }}>
        {errorFallback}
      </div>
    );
  }

  return (
    <div className="rounded-lg overflow-hidden" style={{ height: 220, background: 'linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%)' }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <GLTFErrorBoundary key={renderKey} fallback={errorFallback}>
        <Canvas
          camera={{ fov: 40, position: [20, -60, 55] }}
          gl={{ antialias: true, alpha: true }}
          dpr={1}
          onCreated={({ gl }) => {
            gl.domElement.addEventListener('webglcontextlost', (e) => {
              e.preventDefault();
              setStatus('error');
              onError?.();
            });
          }}
        >
          <ambientLight intensity={1.0} />
          <directionalLight position={[10, 15, 10]} intensity={1.2} />
          <directionalLight position={[-8, 5, -8]} intensity={0.4} />
          {/* 하단 조명: 바닥에서 위로 비춰 언더바디가 잘 보이도록 */}
          <directionalLight position={[0, -20, 10]} intensity={1.4} />
          <directionalLight position={[10, -15, -10]} intensity={0.8} />
          <hemisphereLight args={['#e8e8e8', '#888888', 0.6]} />
          <Suspense fallback={<LoadingSpinner />}>
            <TruckScene tires={tires} />
          </Suspense>
          <OrbitControls
            enablePan={false}
            enableZoom
            minDistance={5}
            maxDistance={200}
            minPolarAngle={0}
            maxPolarAngle={Math.PI}
            target={[0, 0, 0]}
          />
        </Canvas>
      </GLTFErrorBoundary>
    </div>
  );
}
