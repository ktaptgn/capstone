import { useEffect, useMemo, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ScatterChart, Scatter, ZAxis, ReferenceArea } from 'recharts';
import Card from '../components/Card';
import StatusBadge from '../components/StatusBadge';
import SectionHeader from '../components/SectionHeader';
import { policies as mockPolicies } from '../data/policies';
import { loadDashboardSnapshots, mapPolicyComparison } from '../data/c5Snapshots';

const kpiFields = ['demandFulfill', 'pmCost', 'downtime', 'failures', 'totalCost'];
const higherBetter = { demandFulfill: true };

function getBestValue(field, policies) {
  const valid = policies.filter(p => !p.planned && p[field] != null);
  if (higherBetter[field]) return Math.max(...valid.map(p => p[field]));
  return Math.min(...valid.map(p => p[field]));
}

export default function PolicyPage() {
  const [policies, setPolicies] = useState(mockPolicies);
  const [usingSnapshot, setUsingSnapshot] = useState(false);

  useEffect(() => {
    loadDashboardSnapshots().then(snapshot => {
      if (snapshot.policyComparison) {
        setPolicies(mapPolicyComparison(snapshot.policyComparison, mockPolicies));
        setUsingSnapshot(true);
      }
    });
  }, []);

  const recommended = useMemo(
    () => policies.filter(p => !p.planned).reduce((best, policy) => policy.totalCost < best.totalCost ? policy : best, policies[0]),
    [policies],
  );

  const costChartData = policies.filter(p => !p.planned).map(p => ({
    name: p.id, cost: p.totalCost, color: p.color, active: p.id === recommended.id,
  }));

  const scatterData = policies.filter(p => !p.planned).map(p => ({
    x: p.pmCost, y: p.demandFulfill, name: p.id, color: p.color, active: p.id === recommended.id,
    z: p.id === recommended.id ? 200 : 100,
  }));

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      <Card style={{ padding: 20, borderLeft: '4px solid #16A34A' }}>
        <SectionHeader title="Official C5.1 Policy Comparison" />
        <div style={{ fontSize: 13, color: '#334155' }}>
          Recommended by current KPI: <strong>{recommended.id}</strong>. This is the lowest total_cost in the loaded C5.1 summary, not a global optimum claim.
        </div>
        <div style={{ fontSize: 11, color: '#64748B', marginTop: 4 }}>
          Data source: {usingSnapshot ? '/c5_1/policy_comparison.json' : 'mock fallback data'}
        </div>
      </Card>

      <Card style={{ padding: 20 }}>
        <SectionHeader title="Policy KPI Table" />
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #E2E8F0' }}>
                {['Policy', 'Demand %', 'PM Cost', 'Queue Time', 'Unmet Demand', 'Completed Loads', 'Total Cost', 'Status'].map(header => (
                  <th key={header} style={{ padding: '10px 12px', textAlign: header === 'Policy' ? 'left' : 'right', color: '#94A3B8', fontSize: 10, fontWeight: 600, textTransform: 'uppercase' }}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {policies.map(p => {
                const active = p.id === recommended.id;
                return (
                  <tr key={p.id} style={{ borderBottom: '1px solid #F1F5F9', background: active ? '#F0FDF4' : 'transparent', fontWeight: active ? 650 : 400 }}>
                    <td style={{ padding: '10px 12px', textAlign: 'left' }}>
                      <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: p.color, marginRight: 8 }} />
                      <strong>{p.id}</strong> <span style={{ color: '#64748B' }}>{p.name}</span>
                    </td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{p.demandFulfill}%</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{p.pmCost}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{p.downtime}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{p.unmetDemand ?? p.failures}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{p.completedLoads ?? 'n/a'}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{p.totalCost}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>{active && <StatusBadge status="active" label="Recommended" />}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      <div style={{ display: 'flex', gap: 20 }}>
        <Card style={{ padding: 16, flex: 1 }}>
          <SectionHeader title="Total Cost" />
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={costChartData} layout="vertical" margin={{ left: 10, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: '#94A3B8' }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: '#64748B', fontWeight: 600 }} width={36} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
              <Bar dataKey="cost" radius={[0, 6, 6, 0]} barSize={20}>
                {costChartData.map((entry, i) => <Cell key={i} fill={entry.active ? entry.color : `${entry.color}99`} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card style={{ padding: 16, flex: 1 }}>
          <SectionHeader title="PM Cost vs Demand Fulfillment" />
          <ResponsiveContainer width="100%" height={240}>
            <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis type="number" dataKey="x" name="PM Cost" tick={{ fontSize: 10, fill: '#94A3B8' }} />
              <YAxis type="number" dataKey="y" name="Demand %" tick={{ fontSize: 10, fill: '#94A3B8' }} />
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
        </Card>
      </div>

      <div>
        <SectionHeader title="Policy Notes" />
        <div style={{ display: 'flex', gap: 16 }}>
          {policies.map(p => (
            <Card key={p.id} style={{ flex: 1, padding: 16, borderTop: `3px solid ${p.color}` }}>
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
