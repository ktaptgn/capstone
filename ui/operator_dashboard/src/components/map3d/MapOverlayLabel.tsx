import { Html } from '@react-three/drei';
import type { C5OperationMap3DData, Overlay3D } from './map3dTypes';
import { findTargetPosition, getStatusColor } from './map3dUtils';

type MapOverlayLabelProps = {
  overlay: Overlay3D;
  data: C5OperationMap3DData;
};

const BACKGROUNDS: Record<string, string> = {
  critical: 'rgba(254,242,242,0.72)',
  warning: 'rgba(255,251,235,0.72)',
  'in-progress': 'rgba(245,243,255,0.72)',
  normal: 'rgba(255,255,255,0.68)',
};

export default function MapOverlayLabel({ overlay, data }: MapOverlayLabelProps) {
  if (!overlay.visible) return null;

  const position = findTargetPosition(overlay.target_id, data);
  if (!position) return null;

  const severity = overlay.severity || 'normal';
  const color = getStatusColor(severity);
  const yOffset = overlay.type === 'route' ? 12 : 22;

  return (
    <Html
      position={[position.x, position.y + yOffset, position.z]}
      center
      style={{ pointerEvents: 'none' }}
    >
      <div
        style={{
          maxWidth: 140,
          padding: '2px 5px',
          borderRadius: 3,
          border: `1px solid ${color}40`,
          background: BACKGROUNDS[severity] || BACKGROUNDS.normal,
          color: '#1E293B',
          fontSize: 8,
          fontWeight: 700,
          lineHeight: 1.25,
          textAlign: 'center',
          whiteSpace: 'normal',
          boxShadow: '0 2px 6px rgba(15,23,42,0.08)',
        }}
      >
        {overlay.label}
      </div>
    </Html>
  );
}
