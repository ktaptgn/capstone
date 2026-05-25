export default function KpiCard({ label, value, sublabel, color, icon, definition }) {
  return (
    <div style={{
      background: '#fff', border: '1px solid #E2E8F0', borderRadius: 12,
      boxShadow: '0 1px 3px rgba(0,0,0,0.04)', padding: '16px 20px',
      flex: 1, minWidth: 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
        {icon && (
          <div style={{
            width: 40, height: 40, borderRadius: 8,
            background: color ? `${color}14` : '#F3E7E214',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: color || '#8A4931', flexShrink: 0,
          }}>
            {icon}
          </div>
        )}
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5 }}>
            {label}
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: color || '#1E293B', marginTop: 2 }}>
            {value}
          </div>
          {sublabel && <div style={{ fontSize: 11, color: '#64748B', marginTop: 2 }}>{sublabel}</div>}
          {definition && <div style={{ fontSize: 9, color: '#94A3B8', marginTop: 4 }}>{definition}</div>}
        </div>
      </div>
    </div>
  );
}
