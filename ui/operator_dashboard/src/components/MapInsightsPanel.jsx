import { AlertTriangle, Disc, Gauge, Wrench, ShieldAlert, Activity } from 'lucide-react';
import Card from './Card';
import SectionHeader from './SectionHeader';

// Live operational warnings (proxy DES-derived). Each maps to a map condition.
const WARNINGS = [
  { id: 'w-collision', icon: ShieldAlert, label: '충돌 위험', detail: '고위험 구간 차량 2대 근접', severity: 'high' },
  { id: 'w-tire', icon: Disc, label: '타이어 손상', detail: 'T07 FL 타이어 HI 32%', severity: 'high' },
  { id: 'w-crit', icon: AlertTriangle, label: '임계 HI', detail: '위험 트럭 4대 (HI < 60%)', severity: 'high' },
  { id: 'w-slow', icon: Gauge, label: '감속 구간', detail: 'Shovel C 진입로 속도 0.94', severity: 'warning' },
  { id: 'w-pmfull', icon: Wrench, label: 'PM Bay 만차', detail: '2/2 사용 · 대기 2대', severity: 'warning' },
];

// Route-level pressure: traffic intensity, road wear index, congestion/risk.
const ROUTE_PRESSURE = [
  { id: 'main_road', name: 'Main Haul Road', traffic: 5, wear: 0, risk: 'normal' },
  { id: 'high_risk_segment', name: '고위험 구간 (high-risk)', traffic: 2, wear: 12, risk: 'high' },
  { id: 'branch_shovel_c', name: 'Shovel C 진입로', traffic: 1, wear: 9, risk: 'warning' },
  { id: 'branch_crusher_1', name: 'Crusher 1 진입로', traffic: 2, wear: 4, risk: 'normal' },
  { id: 'branch_pm_bay', name: 'PM Bay 진입로', traffic: 2, wear: 3, risk: 'normal' },
];
const MAX_TRAFFIC = 5;

const sevColor = (s) => (s === 'high' ? '#DC2626' : s === 'warning' ? '#D97706' : '#16A34A');
const sevBg = (s) => (s === 'high' ? '#FEF2F2' : s === 'warning' ? '#FFFBEB' : '#F0FDF4');

export default function MapInsightsPanel({ scenarioWarnings = [] }) {
  // Scenario-specific warnings come first, highlighted.
  const scenarioChips = scenarioWarnings.map((w, i) => ({
    id: `scn-${i}`, icon: AlertTriangle, label: w.label, detail: w.detail, severity: w.severity, scenario: true,
  }));
  const allWarnings = [...scenarioChips, ...WARNINGS];

  return (
    <Card style={{ padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <SectionHeader title="Route Pressure & Warnings" />
        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>proxy DES 운영 신호</span>
      </div>

      {/* Warning chips */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
        {allWarnings.map(w => {
          const Icon = w.icon;
          const c = sevColor(w.severity);
          return (
            <div key={w.id} style={{
              display: 'flex', alignItems: 'center', gap: 8, padding: '6px 10px', borderRadius: 8,
              background: sevBg(w.severity),
              border: w.scenario ? `2px solid ${c}` : `1px solid ${c}30`,
              boxShadow: w.scenario ? `0 0 0 3px ${c}18` : 'none',
            }}>
              <Icon size={15} color={c} />
              <div>
                <div style={{ fontSize: 11, fontWeight: 800, color: c, display: 'flex', alignItems: 'center', gap: 4 }}>
                  {w.label}
                  {w.scenario && <span style={{ fontSize: 8, background: c, color: '#fff', padding: '0 4px', borderRadius: 3 }}>시나리오</span>}
                </div>
                <div style={{ fontSize: 9, color: 'var(--text-sub)' }}>{w.detail}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Route heat / wear table */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <Activity size={13} color="var(--text-sub)" />
        <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-sub)' }}>경로 트래픽 · 노면 마모 (Road Wear)</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {ROUTE_PRESSURE.map(r => {
          const c = sevColor(r.risk);
          return (
            <div key={r.id} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: c, flexShrink: 0 }} />
              <span style={{ fontSize: 11, color: 'var(--text-body)', width: 150, flexShrink: 0 }}>{r.name}</span>
              {/* traffic bar */}
              <div style={{ flex: 1, height: 8, background: 'var(--divider)', borderRadius: 4, overflow: 'hidden', minWidth: 60 }}>
                <div style={{ width: `${(r.traffic / MAX_TRAFFIC) * 100}%`, height: '100%', background: c }} />
              </div>
              <span style={{ fontSize: 10, color: 'var(--text-sub)', width: 70, flexShrink: 0 }}>차량 {r.traffic}대</span>
              <span style={{ fontSize: 10, fontWeight: 700, color: r.wear >= 10 ? '#DC2626' : r.wear >= 5 ? '#D97706' : 'var(--text-sub)', width: 78, flexShrink: 0 }}>
                마모 +{r.wear}%
              </span>
              {r.risk !== 'normal' && (
                <span style={{ fontSize: 9, fontWeight: 800, color: c, background: sevBg(r.risk), padding: '1px 6px', borderRadius: 4 }}>
                  {r.risk === 'high' ? '충돌위험' : '주의'}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
