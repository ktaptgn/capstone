/**
 * SceneLighting — physically-motivated lighting rig for the operation map.
 *
 *  • a warm key "sun" (directional) that casts soft shadows, aimed at the
 *    operational area so shadow-map resolution is spent where it matters;
 *  • a sky/ground hemisphere light for natural ambient gradient;
 *  • a cool rim/fill from the opposite side to model sky bounce;
 *  • a procedural image-based Environment (built from Lightformers, so it needs
 *    no downloaded HDRI) that gives metals/asphalt believable reflections.
 */
import { useEffect, useRef } from 'react';
import { Environment, Lightformer } from '@react-three/drei';
import * as THREE from 'three';

type SceneLightingProps = {
  /** World-space center of the operational area [x, z] (shadow + sun focus). */
  center?: [number, number];
  /** Half-size of the shadow frustum (covers the active area). */
  shadowExtent?: number;
};

export default function SceneLighting({
  center = [330, 140],
  shadowExtent = 420,
}: SceneLightingProps) {
  const sunRef = useRef<THREE.DirectionalLight>(null);
  const targetRef = useRef<THREE.Object3D>(null);

  // Bind the sun's shadow/light target to the operational center.
  useEffect(() => {
    if (sunRef.current && targetRef.current) {
      sunRef.current.target = targetRef.current;
      sunRef.current.target.updateMatrixWorld();
    }
  }, []);

  const [cx, cz] = center;

  return (
    <>
      {/* Shadow / sun focus point */}
      <object3D ref={targetRef} position={[cx, 0, cz]} />

      {/* Natural ambient gradient: warm-ish sky over sandy ground bounce */}
      <hemisphereLight args={['#dCEBFF', '#9c7b54', 0.55]} />
      <ambientLight intensity={0.18} />

      {/* Warm key sun — lower raking angle reveals terrain relief & casts
          longer, more dramatic shadows (kills the flat "clay" read). */}
      <directionalLight
        ref={sunRef}
        position={[cx - 300, 250, cz + 280]}
        intensity={2.9}
        color="#FFEFD2"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-bias={-0.0004}
        shadow-normalBias={0.6}
        shadow-camera-near={40}
        shadow-camera-far={1100}
        shadow-camera-left={-shadowExtent}
        shadow-camera-right={shadowExtent}
        shadow-camera-top={shadowExtent}
        shadow-camera-bottom={-shadowExtent}
      />

      {/* Cool sky-bounce fill from the opposite side (no shadow) */}
      <directionalLight position={[cx + 200, 150, cz - 220]} intensity={0.55} color="#AFC7FF" />

      {/* Procedural IBL — soft reflections without any downloaded asset */}
      <Environment resolution={256} frames={1} background={false}>
        {/* Bright sky panel overhead */}
        <Lightformer
          form="rect"
          intensity={1.6}
          color="#cfe2ff"
          position={[0, 60, 0]}
          rotation={[Math.PI / 2, 0, 0]}
          scale={[140, 140, 1]}
        />
        {/* Warm sun disc */}
        <Lightformer
          form="circle"
          intensity={3.2}
          color="#fff0d6"
          position={[-40, 50, 40]}
          scale={28}
        />
        {/* Horizon fills for gentle wrap light */}
        <Lightformer form="rect" intensity={0.8} color="#b9d0f0" position={[80, 8, 0]} rotation={[0, -Math.PI / 2, 0]} scale={[60, 24, 1]} />
        <Lightformer form="rect" intensity={0.6} color="#a7b9d6" position={[-80, 8, 0]} rotation={[0, Math.PI / 2, 0]} scale={[60, 24, 1]} />
      </Environment>
    </>
  );
}
