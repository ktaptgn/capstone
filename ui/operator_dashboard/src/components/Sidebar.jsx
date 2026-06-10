import { LayoutGrid, Truck, BarChart3, Settings, Clock, LineChart, ClipboardList, Share2, BookOpen, Radio } from 'lucide-react';

const navItems = [
  { id: 'overview', label: '전체 현황', icon: LayoutGrid },
  { id: 'fleet', label: 'Fleet 및 PM 상태', icon: Truck },
  { id: 'policy', label: '정책 비교', icon: BarChart3 },
  { id: 'decisions', label: '정책 결정 내역', icon: ClipboardList },
  { id: 'analysis', label: '휴리스틱 분석', icon: LineChart },
  { id: 'story', label: '스토리 모드', icon: BookOpen },
  { id: 'realtime', label: '실시간 시뮬레이션', icon: Radio },
  { id: 'scenario', label: '시나리오 재생', icon: Settings },
  { id: 'transfer', label: '산업 확장성', icon: Share2 },
];

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside style={{
      width: 220, minWidth: 220, background: 'var(--bg-card)', borderRight: '1px solid var(--border)',
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
          <div style={{ fontSize: 14, fontWeight: 700, color: '#8A4931' }}>C5 Mine PM</div>
          <div style={{ fontSize: 11, color: 'var(--text-sub)' }}>관제 대시보드</div>
        </div>
      </div>

      <div style={{ padding: '0 12px' }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, padding: '16px 8px 8px' }}>
          메뉴
        </div>
        {navItems.map(item => {
          const active = activePage === item.id;
          const Icon = item.icon;
          return (
            <button key={item.id} onClick={() => onNavigate(item.id)} style={{
              width: '100%', display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 12px', borderRadius: 8, border: 'none', cursor: 'pointer',
              background: active ? 'var(--primary-soft)' : 'transparent',
              color: active ? '#8A4931' : 'var(--text-body)',
              fontWeight: active ? 600 : 500, fontSize: 13,
              position: 'relative', marginBottom: 2,
              fontFamily: 'inherit',
              transition: 'background 0.15s',
            }}>
              <Icon size={18} color={active ? '#8A4931' : 'var(--text-sub)'} />
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
          background: 'var(--primary-soft)', borderRadius: 10, padding: 14,
        }}>
          <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>현재 추천 정책</div>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#8A4931', marginTop: 4 }}>H3 Cost-weighted</div>
          <div style={{ fontSize: 11, color: 'var(--text-sub)', marginTop: 2 }}>현재 KPI 가중치 기준</div>
        </div>
      </div>
    </aside>
  );
}
