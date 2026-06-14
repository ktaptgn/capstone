import { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ScatterChart, Scatter, ZAxis, ReferenceArea } from 'recharts';
import Card from '../components/Card';
import StatusBadge from '../components/StatusBadge';
import SectionHeader from '../components/SectionHeader';
import versionResults from '../data/version_results.json';

const DASH = '—';

function fmt(value, digits = 1) {
  if (value === null || value === undefined) return DASH;
  return Number(value).toLocaleString('ko-KR', { maximumFractionDigits: digits });
}

function pct(value) {
  if (value === null || value === undefined) return DASH;
  return `${fmt(value, 1)}%`;
}

// `version` is selected in the Header; the whole policy comparison swaps between
// C5.1 / C5.2 / C5.3 result sets sourced from version_results.json.
export default function PolicyPage({ version }) {
  const versionId = version && versionResults.data[version] ? version : versionResults.default;
  const vdata = versionResults.data[versionId];
  const policies = vdata.policies;
  const recommendedId = vdata.recommended;

  const costChartData = useMemo(
    () => policies.filter(p => p.totalCost != null).map(p => ({
      name: p.id, cost: p.totalCost, color: p.color, active: p.id === recommendedId,
    })),
    [policies, recommendedId],
  );

  const scatterData = useMemo(
    () => policies.filter(p => p.pmCost != null && p.demandFulfill != null).map(p => ({
      x: p.pmCost, y: p.demandFulfill, name: p.id, color: p.color,
      active: p.id === recommendedId, z: p.id === recommendedId ? 200 : 100,
    })),
    [policies, recommendedId],
  );

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      <Card style={{ padding: 20, borderLeft: '4px solid #16A34A' }}>
        <SectionHeader title={vdata.title} />
        <div style={{ fontSize: 13, color: '#334155' }}>{vdata.subtitle}</div>
        <div style={{ fontSize: 13, color: '#166534', marginTop: 8, fontWeight: 600 }}>
          추천 정책: <strong>{recommendedId}</strong> — {vdata.headline}
        </div>
        <div style={{ fontSize: 11, color: '#64748B', marginTop: 6 }}>
          데이터 출처: {vdata.source} · 단위: {vdata.costUnit}
        </div>
      </Card>

      <Card style={{ padding: 20 }}>
        <SectionHeader title={`정책 KPI 표 (${vdata.label})`} />
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #E2E8F0' }}>
                {['정책', '수요 충족률', 'PM 비용', '다운타임', '고장 / CM', vdata.costLabel, '상태'].map(header => (
                  <th key={header} style={{ padding: '10px 12px', textAlign: header === '정책' ? 'left' : 'right', color: '#94A3B8', fontSize: 10, fontWeight: 600 }}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {policies.map(p => {
                const active = p.id === recommendedId;
                return (
                  <tr key={p.id} style={{ borderBottom: '1px solid #F1F5F9', background: active ? '#F0FDF4' : 'transparent', fontWeight: active ? 650 : 400 }}>
                    <td style={{ padding: '10px 12px', textAlign: 'left' }}>
                      <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: p.color, marginRight: 8 }} />
                      <strong>{p.id}</strong> <span style={{ color: '#64748B' }}>{p.name}</span>
                    </td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{pct(p.demandFulfill)}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{fmt(p.pmCost)}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{fmt(p.downtime)}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{fmt(p.failures)}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{fmt(p.totalCost, 2)}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{active && <StatusBadge status="active" label="추천" />}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      <div style={{ display: 'flex', gap: 20 }}>
        <Card style={{ padding: 16, flex: 1 }}>
          <SectionHeader title={vdata.costLabel} />
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={costChartData} layout="vertical" margin={{ left: 10, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: '#94A3B8' }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: '#64748B', fontWeight: 600 }} width={48} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
              <Bar dataKey="cost" radius={[0, 6, 6, 0]} barSize={20}>
                {costChartData.map((entry, i) => <Cell key={i} fill={entry.active ? entry.color : `${entry.color}99`} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card style={{ padding: 16, flex: 1 }}>
          <SectionHeader title="PM 비용 vs 수요 충족률" />
          {scatterData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis type="number" dataKey="x" name="PM 비용" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                <YAxis type="number" dataKey="y" name="수요 충족률" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                <ZAxis type="number" dataKey="z" range={[80, 200]} />
                <ReferenceArea x1={0} x2={Math.max(...scatterData.map(d => d.x))} y1={90} y2={100} fill="#16A34A" fillOpacity={0.06} stroke="#16A34A" strokeOpacity={0.2} strokeDasharray="4 2" />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
                <Scatter data={scatterData} shape={(props) => {
                  const { cx, cy, payload } = props;
                  const r = payload.active ? 10 : 7;
                  return <g><circle cx={cx} cy={cy} r={r} fill={payload.color} stroke="#fff" strokeWidth={2} /><text x={cx} y={cy - r - 4} textAnchor="middle" fontSize={10} fontWeight={600} fill={payload.color}>{payload.name}</text></g>;
                }} />
              </ScatterChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 240, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94A3B8', fontSize: 12, textAlign: 'center', padding: 16 }}>
              이 버전 데이터에는 PM 비용 / 수요 충족률 분해가 없습니다 (총비용만 문서화됨).
            </div>
          )}
        </Card>
      </div>

      <div>
        <SectionHeader title="정책 해석 메모" />
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          {policies.map(p => (
            <Card key={p.id} style={{ flex: '1 1 160px', padding: 16, borderTop: `3px solid ${p.color}` }}>
              <div style={{ fontSize: 16, fontWeight: 700, color: p.color }}>{p.id}</div>
              <div style={{ fontSize: 11, color: '#64748B', margin: '4px 0 8px' }}>{p.name}</div>
              <div style={{ fontSize: 11, color: '#334155' }}>{p.useCase}</div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
