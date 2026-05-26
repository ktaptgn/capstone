import { Bell, Download, Thermometer } from 'lucide-react';
import { dashboardKpis } from '../data/dashboardKpis';

const pageNames = {
  overview: '전체 현황',
  fleet: 'Fleet 및 PM 상태',
  policy: '정책 비교',
  analysis: '휴리스틱 분석',
  scenario: '시나리오 재생',
};

export default function Header({ activePage }) {
  const d = dashboardKpis;
  return (
    <header style={{
      height: 56, background: '#fff', borderBottom: '1px solid #E2E8F0',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 24px', flexShrink: 0,
    }}>
      <h1 style={{ fontSize: 16, fontWeight: 700, color: '#1E293B', margin: 0 }}>
        {pageNames[activePage]}
      </h1>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <span style={{
          fontSize: 11, fontWeight: 600, color: '#8A4931',
          background: '#F3E7E2', padding: '4px 10px', borderRadius: 6,
        }}>
          근무조 {d.shift}
        </span>
        <span style={{ fontSize: 12, color: '#64748B' }}>{d.date}</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: '#64748B' }}>
          <Thermometer size={14} /> {d.temperature}°C
        </span>
        <div style={{ position: 'relative', cursor: 'pointer' }}>
          <Bell size={18} color="#64748B" />
          {d.alertCount > 0 && (
            <span style={{
              position: 'absolute', top: -4, right: -6,
              background: '#DC2626', color: '#fff', fontSize: 9, fontWeight: 700,
              width: 16, height: 16, borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {d.alertCount}
            </span>
          )}
        </div>
        <button style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '6px 12px', borderRadius: 6,
          border: '1px solid #E2E8F0', background: '#fff',
          fontSize: 12, color: '#334155', cursor: 'pointer',
          fontFamily: 'inherit',
        }}>
          <Download size={14} /> 내보내기
        </button>
      </div>
    </header>
  );
}
