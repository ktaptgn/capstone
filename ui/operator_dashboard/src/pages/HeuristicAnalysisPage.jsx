import { useMemo, useState } from 'react';
import { AlertTriangle, CheckCircle2, Info, TrendingUp, Layers } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts';
import Card from '../components/Card';
import SectionHeader from '../components/SectionHeader';
import StatusBadge from '../components/StatusBadge';
import {
  C5_4_META, C5_4_POLICIES, C5_4_REGIMES, C5_4_RANKING_KO, C5_4_NOTES, C5_4_LIMITATIONS,
  FAMILY_LABEL, improvementVsH0,
} from '../data/c5_4Analysis';

const fmtTco = (v) => Number(v).toLocaleString('ko-KR', { maximumFractionDigits: 0 });
const fmtPct = (v, d = 1) => `${Number(v).toFixed(d)}%`;

function RegimeSelector({ regimes, value, onChange }) {
  return (
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
      {regimes.map((r) => {
        const active = r.id === value;
        return (
          <button
            key={r.id}
            onClick={() => onChange(r.id)}
            style={{
              padding: '8px 14px', borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit', textAlign: 'left',
              border: active ? '2px solid #8A4931' : '1px solid #E2E8F0',
              background: active ? '#F3E7E2' : '#fff', transition: 'all 0.15s',
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 800, color: active ? '#7C2D12' : '#334155' }}>{r.label}</div>
            <div style={{ fontSize: 10, color: '#94A3B8', marginTop: 2 }}>best: {r.best}</div>
          </button>
        );
      })}
    </div>
  );
}

function RecommendedPanel({ regime }) {
  const best = C5_4_POLICIES[regime.best];
  const bestRow = regime.rows.find((r) => r.policy === regime.best);
  return (
    <Card style={{ padding: 20, borderLeft: `4px solid ${best.color}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <CheckCircle2 size={20} color={best.color} />
            <span style={{ fontSize: 12, color: '#64748B', fontWeight: 700 }}>이 조건 최적 정책</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 34, lineHeight: 1, fontWeight: 800, color: best.color }}>{best.id}</span>
            <span style={{ fontSize: 14, fontWeight: 700, color: '#334155' }}>{best.name}</span>
            <StatusBadge status="available" label={FAMILY_LABEL[best.family]} size="md" />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(120px, 1fr))', gap: 12, marginTop: 18 }}>
            <Metric label="TCO (정규화)" value={fmtTco(bestRow.tco)} />
            <Metric label="H0 대비 절감" value={fmtPct(regime.headlineImprovementPct)} accent="#16A34A" />
            <Metric label="고장/run" value={bestRow.cmPerRun.toFixed(1)} />
          </div>
        </div>
        <div style={{
          minWidth: 200, border: '1px solid #FDE68A', background: '#FFFBEB', borderRadius: 8,
          padding: 12, color: '#92400E', fontSize: 12, fontWeight: 700,
        }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}><AlertTriangle size={16} /><span>주의</span></div>
          <div style={{ marginTop: 6, fontWeight: 600, lineHeight: 1.5 }}>
            인-랩 벤치마크입니다. 수학적 전체 최적을 보장하지 않습니다.
          </div>
        </div>
      </div>
    </Card>
  );
}

function Metric({ label, value, accent = '#1E293B' }) {
  return (
    <div>
      <div style={{ fontSize: 11, color: '#94A3B8', fontWeight: 700 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 800, color: accent }}>{value}</div>
    </div>
  );
}

function RankingTable({ regime }) {
  const rows = improvementVsH0(regime);
  return (
    <Card style={{ padding: 20 }}>
      <SectionHeader title="정책 순위 — Total TCO (낮을수록 우수)" />
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #E2E8F0' }}>
              {['#', '정책', '계열', 'TCO', 'H0 대비', 'PM 방문', 'CM·고장/run', '충족률', '종료 HI', '다운타임(h)'].map((h, i) => (
                <th key={h} style={{ padding: '10px 8px', textAlign: i <= 2 ? 'left' : 'right', color: '#64748B', fontSize: 11, fontWeight: 800 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => {
              const p = C5_4_POLICIES[row.policy];
              const isBest = row.policy === regime.best;
              const isBlind = p.family === 'blind';
              return (
                <tr key={row.policy} style={{ borderBottom: '1px solid #F1F5F9', background: isBest ? '#F0FDF4' : isBlind ? '#FAFAFA' : 'transparent' }}>
                  <td style={{ padding: '10px 8px', color: '#94A3B8', fontWeight: 700 }}>{idx + 1}</td>
                  <td style={{ padding: '10px 8px', fontWeight: 800, color: p.color }}>
                    {p.id}{isBest && <span style={{ marginLeft: 6, fontSize: 9, color: '#16A34A' }}>★ best</span>}
                    <div style={{ fontSize: 10, color: '#94A3B8', fontWeight: 500 }}>{p.name}</div>
                  </td>
                  <td style={{ padding: '10px 8px' }}>
                    <span style={{
                      fontSize: 10, fontWeight: 800, padding: '2px 7px', borderRadius: 10,
                      background: isBlind ? '#F1F5F9' : '#EFF6FF', color: isBlind ? '#64748B' : '#1D4ED8',
                    }}>{FAMILY_LABEL[p.family]}</span>
                  </td>
                  <td style={{ padding: '10px 8px', textAlign: 'right', fontWeight: 700 }}>{fmtTco(row.tco)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right', fontWeight: 700, color: row.improvementPct > 0.05 ? '#16A34A' : '#94A3B8' }}>
                    {row.improvementPct > 0.05 ? `▼ ${fmtPct(row.improvementPct)}` : '기준'}
                  </td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{fmtTco(row.pmVisits)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right', color: row.cmPerRun >= 10 ? '#DC2626' : row.cmPerRun >= 1 ? '#D97706' : '#16A34A', fontWeight: row.cmPerRun >= 10 ? 700 : 500 }}>
                    {row.cmPerRun.toFixed(1)}
                  </td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{row.fulfil.toFixed(3)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{row.endHI.toFixed(2)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{fmtTco(row.downHrs)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: 12, fontSize: 11, color: '#64748B', display: 'flex', alignItems: 'center', gap: 6 }}>
        <Layers size={13} /> 전 조건 공통 순위: <strong style={{ color: '#334155' }}>{C5_4_RANKING_KO}</strong>
      </div>
    </Card>
  );
}

function ImprovementChart({ regime }) {
  const data = improvementVsH0(regime)
    .filter((r) => r.policy !== 'H0')
    .map((r) => ({ policy: r.policy, improvement: Number(r.improvementPct.toFixed(1)), color: C5_4_POLICIES[r.policy].color }));
  return (
    <Card style={{ padding: 20 }}>
      <SectionHeader title="H0(달력 시간 주기) 대비 TCO 절감율" />
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} margin={{ left: 4, right: 16, top: 8, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
          <XAxis dataKey="policy" tick={{ fontSize: 12, fill: '#64748B', fontWeight: 700 }} />
          <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} unit="%" />
          <Tooltip formatter={(v) => [`${v}%`, 'H0 대비 절감']} contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
          <ReferenceLine y={0} stroke="#94A3B8" />
          <Bar dataKey="improvement" radius={[4, 4, 0, 0]}>
            {data.map((d) => <Cell key={d.policy} fill={d.color} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

function HeuristicTable() {
  return (
    <Card style={{ padding: 20 }}>
      <SectionHeader title="휴리스틱 정의 (PM 계열 × 배차 계열)" />
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #E2E8F0' }}>
              {['정책', '계열', 'PM 트리거', '배차 규칙'].map((h, i) => (
                <th key={h} style={{ padding: '10px 8px', textAlign: 'left', color: '#64748B', fontSize: 11, fontWeight: 800, width: i === 0 ? 90 : 'auto' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.values(C5_4_POLICIES).map((p) => (
              <tr key={p.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                <td style={{ padding: '10px 8px', fontWeight: 800, color: p.color }}>
                  {p.id}
                  <div style={{ fontSize: 10, color: '#94A3B8', fontWeight: 500 }}>{p.name}</div>
                </td>
                <td style={{ padding: '10px 8px' }}>
                  <span style={{
                    fontSize: 10, fontWeight: 800, padding: '2px 7px', borderRadius: 10,
                    background: p.family === 'blind' ? '#F1F5F9' : '#EFF6FF', color: p.family === 'blind' ? '#64748B' : '#1D4ED8',
                  }}>{FAMILY_LABEL[p.family]}</span>
                </td>
                <td style={{ padding: '10px 8px', color: '#334155' }}>{p.pm}</td>
                <td style={{ padding: '10px 8px', color: '#334155' }}>{p.dispatch}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function NotesPanel() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.2fr) minmax(280px, 0.8fr)', gap: 20 }}>
      <Card style={{ padding: 20 }}>
        <SectionHeader title="해석 — 왜 이 순위인가" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {C5_4_NOTES.map((note, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', padding: 10, borderRadius: 8, background: '#F8FAFC', border: '1px solid #E2E8F0' }}>
              <TrendingUp size={16} color="#2563EB" style={{ marginTop: 1, flexShrink: 0 }} />
              <span style={{ fontSize: 12, color: '#334155', lineHeight: 1.55 }}>{note}</span>
            </div>
          ))}
        </div>
      </Card>
      <Card style={{ padding: 18 }}>
        <details open>
          <summary style={{ cursor: 'pointer', fontSize: 14, fontWeight: 800, color: '#1E293B', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Info size={16} color="#64748B" /> 분석 한계
          </summary>
          <ul style={{ margin: '12px 0 0 18px', color: '#64748B', fontSize: 12, lineHeight: 1.7 }}>
            {C5_4_LIMITATIONS.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </details>
      </Card>
    </div>
  );
}

export default function HeuristicAnalysisPage() {
  const [regimeId, setRegimeId] = useState(C5_4_REGIMES[0].id);
  const regime = useMemo(() => C5_4_REGIMES.find((r) => r.id === regimeId) || C5_4_REGIMES[0], [regimeId]);

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: '#1E293B' }}>휴리스틱 분석</h2>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: '#64748B' }}>
              통합 PM-스케줄링 + 배차 벤치마크 · 목적함수 = {C5_4_META.objective}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <Metric label="시드" value={C5_4_META.seeds} />
            <Metric label="기간(일)" value={C5_4_META.days} />
            <Metric label="트럭" value={C5_4_META.trucks} />
            <Metric label="부품 HI" value={C5_4_META.components.length} />
          </div>
        </div>
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: 8 }}>운영 조건 (Regime)</div>
          <RegimeSelector regimes={C5_4_REGIMES} value={regimeId} onChange={setRegimeId} />
          <div style={{ fontSize: 12, color: '#64748B', marginTop: 10 }}>{regime.desc}</div>
        </div>
      </Card>

      <RecommendedPanel regime={regime} />

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(420px, 1.4fr) minmax(300px, 0.9fr)', gap: 20, alignItems: 'start' }}>
        <RankingTable regime={regime} />
        <ImprovementChart regime={regime} />
      </div>

      <HeuristicTable />
      <NotesPanel />
    </div>
  );
}
