import { LayoutGrid, Truck, BarChart3, Settings, Clock } from 'lucide-react';

const navItems = [
  { id: 'overview', label: 'Operation Overview', icon: LayoutGrid },
  { id: 'fleet', label: 'Fleet & PM Status', icon: Truck },
  { id: 'policy', label: 'Policy Comparison', icon: BarChart3 },
  { id: 'scenario', label: 'Scenario / What-if', icon: Settings },
];

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside style={{
      width: 220, minWidth: 220, background: '#fff', borderRight: '1px solid #E2E8F0',
      display: 'flex', flexDirection: 'column', height: '100vh', position: 'sticky', top: 0,
    }}>
      <div style={{ padding: '20px 16px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 8, background: '#8A4931',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Clock size={20} color="#fff" />
        </div>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#7C2D12' }}>C5 Mine PM</div>
          <div style={{ fontSize: 11, color: '#64748B' }}>Control Tower</div>
        </div>
      </div>

      <div style={{ padding: '0 12px' }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 1, padding: '16px 8px 8px' }}>
          Navigation
        </div>
        {navItems.map(item => {
          const active = activePage === item.id;
          const Icon = item.icon;
          return (
            <button key={item.id} onClick={() => onNavigate(item.id)} style={{
              width: '100%', display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 12px', borderRadius: 8, border: 'none', cursor: 'pointer',
              background: active ? '#F3E7E2' : 'transparent',
              color: active ? '#7C2D12' : '#334155',
              fontWeight: active ? 600 : 500, fontSize: 13,
              position: 'relative', marginBottom: 2,
              fontFamily: 'inherit',
              transition: 'background 0.15s',
            }}>
              <Icon size={18} color={active ? '#8A4931' : '#64748B'} />
              {item.label}
              {active && (
                <span style={{
                  position: 'absolute', right: 0, top: '50%', transform: 'translateY(-50%)',
                  width: 4, height: 16, borderRadius: 2, background: '#8A4931',
                }} />
              )}
            </button>
          );
        })}
      </div>

      <div style={{ marginTop: 'auto', padding: 16 }}>
        <div style={{
          background: '#F3E7E2', borderRadius: 10, padding: 14,
        }}>
          <div style={{ fontSize: 10, fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase' }}>Active Policy</div>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#7C2D12', marginTop: 4 }}>H3 Cost-weighted</div>
          <div style={{ fontSize: 11, color: '#64748B', marginTop: 2 }}>Balanced cost optimization</div>
        </div>
      </div>
    </aside>
  );
}
