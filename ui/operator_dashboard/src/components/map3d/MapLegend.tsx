const LEGEND_ITEMS: Array<{
  label: string;
  color: string;
  shape?: 'circle' | 'square' | 'ring' | 'line';
}> = [
  { label: 'HI ≥ 95% / Idle', color: '#3B82F6', shape: 'square' },
  { label: 'HI ≥ 70%', color: '#22C55E', shape: 'square' },
  { label: 'HI ≥ 50%', color: '#F97316', shape: 'square' },
  { label: 'HI < 50%', color: '#EF4444', shape: 'square' },
  { label: 'Queue Low', color: '#3B82F6', shape: 'ring' },
  { label: 'Queue High', color: '#EF4444', shape: 'ring' },
  { label: 'High Risk Route', color: '#DC2626', shape: 'line' },
  { label: 'PM In Progress', color: '#7C3AED', shape: 'circle' },
];

export default function MapLegend() {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px 14px',
        justifyContent: 'center',
        marginTop: 10,
      }}
    >
      {LEGEND_ITEMS.map(({ label, color, shape }) => (
        <div
          key={label}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            fontSize: 10,
            color: '#64748B',
            whiteSpace: 'nowrap',
          }}
        >
          <span
            style={{
              display: 'inline-block',
              width: shape === 'line' ? 14 : 8,
              height: shape === 'line' ? 3 : 8,
              borderRadius:
                shape === 'square'
                  ? 2
                  : shape === 'line'
                    ? 1
                    : '50%',
              background: shape === 'ring' ? 'transparent' : color,
              border: shape === 'ring' ? `2px solid ${color}` : 'none',
              boxSizing: 'border-box',
            }}
          />
          {label}
        </div>
      ))}
    </div>
  );
}
