import { SlidersHorizontal } from 'lucide-react';
import { OVERVIEW_SCENARIOS } from '../data/overviewScenarios';

// Compact scenario switcher for the Overview page. Updates KPI cards + map warnings.
export default function ScenarioToggle({ scenarioId, onChange }) {
  const active = OVERVIEW_SCENARIOS.find(s => s.id === scenarioId) || OVERVIEW_SCENARIOS[0];
  const isNormal = active.id === 'normal';

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap',
      padding: '10px 14px', borderRadius: 10,
      background: isNormal ? 'var(--bg-card)' : '#FFFBEB',
      border: `1px solid ${isNormal ? 'var(--border)' : '#FDE68A'}`,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <SlidersHorizontal size={15} color="#8A4931" />
        <span style={{ fontSize: 12, fontWeight: 800, color: 'var(--text-main)' }}>시나리오</span>
      </div>
      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
        {OVERVIEW_SCENARIOS.map(s => {
          const on = s.id === scenarioId;
          return (
            <button
              key={s.id}
              onClick={() => onChange(s.id)}
              style={{
                padding: '5px 11px', borderRadius: 7, border: 'none', cursor: 'pointer',
                fontSize: 11, fontWeight: 700, fontFamily: 'inherit',
                background: on ? '#8A4931' : 'var(--divider)',
                color: on ? '#fff' : 'var(--text-sub)',
              }}
            >
              {s.label}
            </button>
          );
        })}
      </div>
      <span style={{ fontSize: 11, color: isNormal ? 'var(--text-muted)' : '#92400E', fontWeight: 600, marginLeft: 'auto' }}>
        {active.banner}
      </span>
    </div>
  );
}
