import { useState, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import Card from '../components/Card';
import SectionHeader from '../components/SectionHeader';
import StatusBadge from '../components/StatusBadge';
import { scenarioBaseline, scenarioResults, scenarioRecommendations } from '../data/scenario';
import { policies } from '../data/policies';

function SegmentedControl({ label, options, value, onChange }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', marginBottom: 6 }}>{label}</div>
      <div style={{ display: 'flex', borderRadius: 8, border: '1px solid #E2E8F0', overflow: 'hidden' }}>
        {options.map(opt => {
          const active = opt === value;
          return (
            <button key={opt} onClick={() => onChange(opt)} style={{
              flex: 1, padding: '8px 12px', border: 'none', cursor: 'pointer',
              background: active ? '#8A4931' : '#fff',
              color: active ? '#fff' : '#334155',
              fontWeight: active ? 600 : 400, fontSize: 12,
              fontFamily: 'inherit',
              transition: 'all 0.15s',
            }}>
              {opt}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function PolicySelector({ selected, onChange }) {
  const activePolicies = policies.filter(p => !p.planned);
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', marginBottom: 6 }}>Policy</div>
      <div style={{ display: 'flex', gap: 8 }}>
        {activePolicies.map(p => {
          const active = p.id === selected;
          return (
            <button key={p.id} onClick={() => onChange(p.id)} style={{
              flex: 1, padding: '10px 8px', borderRadius: 8, cursor: 'pointer',
              border: active ? `2px solid ${p.color}` : '1px solid #E2E8F0',
              background: active ? `${p.color}08` : '#fff',
              fontFamily: 'inherit',
              transition: 'all 0.15s',
            }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: p.color }}>{p.id}</div>
              <div style={{ fontSize: 9, color: '#64748B', marginTop: 2 }}>{p.name}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

const kpiConfig = [
  { key: 'demandFulfill', label: 'Demand Fulfillment', unit: '%', betterHigh: true },
  { key: 'pmCost', label: 'PM Cost', unit: 'M₩', betterHigh: false },
  { key: 'downtime', label: 'Downtime', unit: 'hrs', betterHigh: false },
  { key: 'availTrucks', label: 'Available Trucks', unit: '', betterHigh: true },
  { key: 'riskTrucks', label: 'Risk Trucks', unit: '', betterHigh: false },
  { key: 'totalCost', label: 'Total Cost', unit: 'M₩', betterHigh: false },
];

function ScenarioKpiCard({ config, baseline, scenario }) {
  const bVal = baseline[config.key];
  const sVal = scenario[config.key];
  const delta = sVal - bVal;
  const improved = config.betterHigh ? delta > 0 : delta < 0;
  const worse = config.betterHigh ? delta < 0 : delta > 0;
  const deltaColor = delta === 0 ? '#64748B' : improved ? '#16A34A' : '#DC2626';
  const arrow = delta > 0 ? '↑' : delta < 0 ? '↓' : '→';

  const fmt = (v) => config.unit === '%' ? `${v}%` : config.unit === 'M₩' ? `₩${v}M` : v;

  return (
    <Card style={{ padding: 14, flex: 1 }}>
      <div style={{ fontSize: 10, fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase' }}>{config.label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color: '#1E293B', marginTop: 4 }}>{fmt(sVal)}</div>
      <div style={{ fontSize: 11, color: '#64748B', marginTop: 4 }}>
        {fmt(bVal)} → {fmt(sVal)}
      </div>
      <div style={{ fontSize: 12, fontWeight: 600, color: deltaColor, marginTop: 4 }}>
        {arrow} {delta > 0 ? '+' : ''}{config.unit === 'M₩' ? `₩${delta.toFixed(1)}M` : config.unit === '%' ? `${delta}%p` : delta}
      </div>
    </Card>
  );
}

export default function ScenarioPage() {
  const [demand, setDemand] = useState('Normal');
  const [pmBay, setPmBay] = useState(2);
  const [roadRisk, setRoadRisk] = useState('Normal');
  const [shift, setShift] = useState('Day');
  const [policy, setPolicy] = useState('H3');

  const resultKey = `${demand}-${policy}`;
  const scenario = scenarioResults[resultKey] || scenarioBaseline;
  const recommendation = scenarioRecommendations[demand];

  const impactData = [
    { metric: 'Demand %', baseline: scenarioBaseline.demandFulfill, scenario: scenario.demandFulfill },
    { metric: 'PM Cost', baseline: scenarioBaseline.pmCost, scenario: scenario.pmCost },
    { metric: 'Downtime', baseline: scenarioBaseline.downtime, scenario: scenario.downtime },
    { metric: 'Total Cost', baseline: scenarioBaseline.totalCost, scenario: scenario.totalCost },
    { metric: 'Risk Trucks', baseline: scenarioBaseline.riskTrucks, scenario: scenario.riskTrucks },
  ];

  const riskAssessment = useMemo(() => {
    const levels = {
      Low: { pmOverload: 'Low', queueBottleneck: 'Low', unmetDemand: 'Low' },
      Normal: { pmOverload: 'Low', queueBottleneck: 'Low', unmetDemand: 'Medium' },
      High: { pmOverload: 'High', queueBottleneck: 'Medium', unmetDemand: 'High' },
    };
    return levels[demand] || levels.Normal;
  }, [demand]);

  const riskColor = (level) => level === 'Low' ? '#16A34A' : level === 'Medium' ? '#F59E0B' : '#DC2626';
  const riskBg = (level) => level === 'Low' ? '#F0FDF4' : level === 'Medium' ? '#FFFBEB' : '#FEF2F2';

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Scenario Parameters */}
      <Card style={{ padding: 20 }}>
        <SectionHeader title="Scenario Parameters" />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
          <SegmentedControl label="Demand Level" options={['Low','Normal','High']} value={demand} onChange={setDemand} />
          <SegmentedControl label="PM Bay Capacity" options={[1,2,3]} value={pmBay} onChange={setPmBay} />
          <SegmentedControl label="Road Risk" options={['Low','Normal','High']} value={roadRisk} onChange={setRoadRisk} />
          <SegmentedControl label="Shift" options={['Day','Evening','Night']} value={shift} onChange={setShift} />
        </div>
        <PolicySelector selected={policy} onChange={setPolicy} />
      </Card>

      {/* Output KPI Cards */}
      <div style={{ display: 'flex', gap: 12 }}>
        {kpiConfig.map(c => (
          <ScenarioKpiCard key={c.key} config={c} baseline={scenarioBaseline} scenario={scenario} />
        ))}
      </div>

      {/* Charts Row */}
      <div style={{ display: 'flex', gap: 20 }}>
        <Card style={{ padding: 16, flex: 2 }}>
          <SectionHeader title="Scenario Impact Comparison" />
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={impactData} layout="vertical" margin={{ left: 20, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: '#94A3B8' }} />
              <YAxis type="category" dataKey="metric" tick={{ fontSize: 11, fill: '#64748B' }} width={80} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="baseline" name={`Baseline (H3 Normal)`} fill="#94A3B8" radius={[0, 4, 4, 0]} barSize={12} />
              <Bar dataKey="scenario" name="Scenario" fill="#8A4931" radius={[0, 4, 4, 0]} barSize={12} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Recommended Policy */}
          <Card style={{
            padding: 16,
            borderLeft: `4px solid ${policies.find(p => p.id === recommendation.policy)?.color || '#8A4931'}`,
          }}>
            <SectionHeader title="Recommended Policy" />
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <span style={{ fontSize: 20, fontWeight: 700, color: policies.find(p => p.id === recommendation.policy)?.color }}>
                {recommendation.policy}
              </span>
              <span style={{ fontSize: 12, color: '#64748B' }}>
                {policies.find(p => p.id === recommendation.policy)?.name}
              </span>
              {recommendation.policy === policy && (
                <StatusBadge status="available" label="Selected ✓" />
              )}
            </div>
            <div style={{ fontSize: 12, color: '#334155', lineHeight: 1.5 }}>{recommendation.reason}</div>
          </Card>

          {/* Risk Assessment */}
          <Card style={{ padding: 16 }}>
            <SectionHeader title="Risk Assessment" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[
                { label: 'PM Overload Risk', level: riskAssessment.pmOverload },
                { label: 'Queue Bottleneck', level: riskAssessment.queueBottleneck },
                { label: 'Unmet Demand', level: riskAssessment.unmetDemand },
              ].map(r => (
                <div key={r.label} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '8px 12px', borderRadius: 6, background: riskBg(r.level),
                }}>
                  <span style={{ fontSize: 12, color: '#334155' }}>{r.label}</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: riskColor(r.level) }}>{r.level}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
