export function getHIColor(value) {
  if (value >= 80) return '#16A34A';
  if (value >= 60) return '#D97706';
  if (value >= 40) return '#F59E0B';
  return '#DC2626';
}

export function getHIStatus(value) {
  if (value >= 80) return 'normal';
  if (value >= 60) return 'watch';
  if (value >= 40) return 'warning';
  return 'critical';
}

export default function HealthBar({ value, max = 100, color, height = 6 }) {
  const fillColor = color || getHIColor(value);
  return (
    <div style={{
      width: '100%', height, borderRadius: height / 2, background: '#F1F5F9',
    }}>
      <div style={{
        width: `${Math.min((value / max) * 100, 100)}%`, height: '100%',
        borderRadius: height / 2, background: fillColor,
        transition: 'width 0.4s ease',
      }} />
    </div>
  );
}
