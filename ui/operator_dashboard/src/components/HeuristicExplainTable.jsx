import { X } from 'lucide-react';
import { heuristicsExplain, heuristicsNote } from '../data/heuristicsExplain';

const COLS = [
  { key: 'definition', label: '한 줄 정의' },
  { key: 'rule', label: '의사결정 규칙' },
  { key: 'benefit', label: '기대 효과' },
  { key: 'weakness', label: '약점' },
];

export function HeuristicExplainTable() {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, minWidth: 880 }}>
        <thead>
          <tr style={{ borderBottom: '2px solid var(--border)' }}>
            <th style={{ padding: '10px 8px', textAlign: 'left', color: 'var(--text-muted)', fontSize: 11, fontWeight: 800, width: 150 }}>정책</th>
            {COLS.map(c => (
              <th key={c.key} style={{ padding: '10px 8px', textAlign: 'left', color: 'var(--text-muted)', fontSize: 11, fontWeight: 800 }}>{c.label}</th>
            ))}
            <th style={{ padding: '10px 8px', textAlign: 'left', color: 'var(--text-muted)', fontSize: 11, fontWeight: 800, width: 150 }}>KPI (대표)</th>
          </tr>
        </thead>
        <tbody>
          {heuristicsExplain.map(h => (
            <tr key={h.id} style={{ borderBottom: '1px solid var(--divider)', background: h.best ? 'rgba(22,163,74,0.06)' : 'transparent' }}>
              <td style={{ padding: '12px 8px', verticalAlign: 'top' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ fontSize: 15, fontWeight: 800, color: h.color }}>{h.id}</span>
                  {h.best && (
                    <span style={{ fontSize: 9, fontWeight: 800, color: '#fff', background: '#16A34A', padding: '2px 6px', borderRadius: 4 }}>추천</span>
                  )}
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-sub)', marginTop: 2 }}>{h.name}</div>
              </td>
              {COLS.map(c => (
                <td key={c.key} style={{ padding: '12px 8px', verticalAlign: 'top', color: 'var(--text-body)', lineHeight: 1.5 }}>
                  {h[c.key]}
                </td>
              ))}
              <td style={{ padding: '12px 8px', verticalAlign: 'top' }}>
                <div style={{ fontSize: 11, color: 'var(--text-sub)', lineHeight: 1.6 }}>
                  <div>비용 <strong style={{ color: 'var(--text-main)' }}>{h.kpi.totalCost}</strong></div>
                  <div>수요 <strong style={{ color: 'var(--text-main)' }}>{h.kpi.demand}</strong></div>
                  <div>다운타임 <strong style={{ color: 'var(--text-main)' }}>{h.kpi.downtime}</strong></div>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 12, lineHeight: 1.5 }}>{heuristicsNote}</div>
    </div>
  );
}

export function HeuristicExplainModal({ open, onClose }) {
  if (!open) return null;
  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.5)', zIndex: 1000,
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: 'var(--bg-card)', borderRadius: 12, padding: 24, width: '100%', maxWidth: 1100,
          maxHeight: '85vh', overflow: 'auto', boxShadow: '0 20px 60px rgba(15,23,42,0.25)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: 'var(--text-main)' }}>H0–H4 휴리스틱 설명</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}>
            <X size={20} color="var(--text-sub)" />
          </button>
        </div>
        <HeuristicExplainTable />
      </div>
    </div>
  );
}
