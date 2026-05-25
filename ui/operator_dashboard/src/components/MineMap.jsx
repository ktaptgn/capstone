import { facilities, routes, truckMarkers } from '../data/mineMap';

const statusColors = {
  running: '#16A34A', warning: '#F59E0B', critical: '#DC2626',
  'in-progress': '#7C3AED', standby: '#6B7280', normal: '#16A34A',
};

const facilityHeaderColors = {
  shovel: '#16A34A', crusher: '#2563EB', pm_bay: '#7C3AED',
  standby: '#6B7280', dispatch: '#8A4931',
};

export default function MineMap() {
  return (
    <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.04)', padding: 16, overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h3 style={{ fontSize: 14, fontWeight: 700, color: '#1E293B' }}>Mine Operation Map</h3>
        <span style={{ fontSize: 11, color: '#8A4931', fontWeight: 600, background: '#F3E7E2', padding: '3px 8px', borderRadius: 4 }}>
          Policy: H3 Cost-weighted
        </span>
      </div>
      <svg viewBox="0 0 660 280" style={{ width: '100%', height: 'auto', background: '#F8FAFC', borderRadius: 8 }}>
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#E2E8F0" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="660" height="280" fill="url(#grid)" />

        {routes.map(r => (
          <path key={r.id} d={r.path} fill="none"
            stroke={r.riskLevel === 'high' ? '#F59E0B' : '#94A3B8'}
            strokeWidth={r.riskLevel === 'high' ? 4 : 2}
            strokeDasharray={r.riskLevel === 'high' ? '8 4' : '6 3'}
            opacity={r.riskLevel === 'high' ? 0.6 : 0.5}
          />
        ))}

        {/* Dispatch zone ellipse */}
        <ellipse cx={290} cy={155} rx={60} ry={35} fill="none" stroke="#8A4931" strokeWidth={1.5} strokeDasharray="6 3" opacity={0.4} />
        <text x={290} y={140} textAnchor="middle" fontSize={8} fill="#8A4931" fontWeight={600} opacity={0.6}>Dispatch Zone</text>

        {facilities.map(f => {
          const hdrColor = facilityHeaderColors[f.type] || '#64748B';
          const w = f.type === 'standby' ? 70 : 60;
          const h = 36;
          const isDashed = f.type === 'standby';
          return (
            <g key={f.id}>
              <rect x={f.x - w/2} y={f.y - h/2} width={w} height={h} rx={4}
                fill="#fff" stroke={isDashed ? '#9CA3B8' : hdrColor}
                strokeWidth={f.type === 'pm_bay' ? 2 : 1}
                strokeDasharray={isDashed ? '4 2' : 'none'}
              />
              <rect x={f.x - w/2} y={f.y - h/2} width={w} height={12} rx={0}
                fill={hdrColor} opacity={0.15}
              />
              <text x={f.x} y={f.y - h/2 + 9} textAnchor="middle" fontSize={7} fill={hdrColor} fontWeight={700}>
                {f.name}
              </text>
              <text x={f.x} y={f.y + 6} textAnchor="middle" fontSize={8} fill="#334155" fontWeight={600}>
                {f.type === 'pm_bay' ? `${f.occupied}/${f.capacity} occupied` :
                 f.queue !== undefined && f.queue > 0 ? `Queue: ${f.queue}` :
                 f.type === 'standby' ? '' : 'Queue: 0'}
              </text>
            </g>
          );
        })}

        {truckMarkers.map(t => {
          const col = statusColors[t.status] || '#6B7280';
          return (
            <g key={t.truckId}>
              <circle cx={t.x} cy={t.y} r={10} fill="#fff" stroke={col} strokeWidth={2} />
              <circle cx={t.x + 5} cy={t.y - 5} r={3} fill={col} />
              <text x={t.x} y={t.y - 14} textAnchor="middle" fontSize={7} fill="#334155" fontWeight={600}>
                {t.truckId}
              </text>
            </g>
          );
        })}
      </svg>

      <div style={{ display: 'flex', gap: 16, marginTop: 10, justifyContent: 'center' }}>
        {[['Running','#16A34A'],['Warning','#F59E0B'],['Critical','#DC2626'],['PM','#7C3AED'],['Standby','#6B7280']].map(([label, color]) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10, color: '#64748B' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: color }} /> {label}
          </div>
        ))}
      </div>
    </div>
  );
}
