import { Html } from '@react-three/drei';

/**
 * Visual gate placed on the PM Bay access road, marking where the final
 * "enter PM or not" decision is enforced before a truck reaches the bay.
 */
export default function PMDecisionGate({ position }: { position: [number, number, number] }) {
  const [x, y, z] = position;
  return (
    <group position={[x, y, z]}>
      {/* gate floor band */}
      <mesh position={[0, 0.4, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[18, 9]} />
        <meshStandardMaterial color="#7C3AED" transparent opacity={0.2} />
      </mesh>
      {/* posts */}
      {[-8, 8].map((dx) => (
        <mesh key={dx} position={[dx, 9, 0]}>
          <cylinderGeometry args={[1, 1, 18, 10]} />
          <meshStandardMaterial color="#7C3AED" metalness={0.2} roughness={0.5} />
        </mesh>
      ))}
      {/* top beam */}
      <mesh position={[0, 18.5, 0]}>
        <boxGeometry args={[18, 2.6, 2.6]} />
        <meshStandardMaterial color="#7C3AED" emissive="#7C3AED" emissiveIntensity={0.3} />
      </mesh>
      <Html position={[0, 25, 0]} center distanceFactor={140} occlude={false} style={{ pointerEvents: 'none' }}>
        <div style={{
          fontFamily: 'system-ui, sans-serif', whiteSpace: 'nowrap', textAlign: 'center',
        }}>
          <div style={{
            background: '#7C3AED', color: '#fff', padding: '3px 9px', borderRadius: 6,
            fontSize: 11, fontWeight: 800,
          }}>
            🛠 PM Decision Gate
          </div>
          <div style={{
            marginTop: 2, background: 'rgba(255,255,255,0.92)', color: '#5B21B6',
            padding: '1px 7px', borderRadius: 4, fontSize: 9, fontWeight: 700,
          }}>
            최종 PM 진입 결정
          </div>
        </div>
      </Html>
    </group>
  );
}
