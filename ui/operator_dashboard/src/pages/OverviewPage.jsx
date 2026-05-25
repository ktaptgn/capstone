import { Target, Truck, Wrench, DollarSign, AlertTriangle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Line, ComposedChart } from 'recharts';
import KpiCard from '../components/KpiCard';
import Card from '../components/Card';
import StatusBadge from '../components/StatusBadge';
import HealthBar from '../components/HealthBar';
import MineMap from '../components/MineMap';
import SectionHeader from '../components/SectionHeader';
import { dashboardKpis } from '../data/dashboardKpis';
import { alerts, recommendedActions } from '../data/alerts';

const d = dashboardKpis;

const demandChartData = d.demandTrend.hours.map((h, i) => ({
  hour: h, demand: d.demandTrend.demand[i], completed: d.demandTrend.completed[i],
}));

const statusBarData = d.truckStatusDistribution;
const totalTrucks = Object.values(statusBarData).reduce((a, b) => a + b, 0);
const statusBarColors = { running: '#16A34A', standby: '#6B7280', pm: '#7C3AED', warning: '#F59E0B', critical: '#DC2626' };

function DecisionPanel() {
  return (
    <div style={{ width: 300, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Card style={{ padding: 16 }}>
        <SectionHeader title="Recommended Actions" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {recommendedActions.map(a => {
            const colors = { critical: '#DC2626', warning: '#F59E0B', standby: '#6B7280' };
            const bgs = { critical: '#FEF2F2', warning: '#FFFBEB', standby: '#F9FAFB' };
            return (
              <div key={a.id} style={{
                display: 'flex', gap: 10, padding: 10, borderRadius: 8,
                background: bgs[a.status], border: `1px solid ${colors[a.status]}20`,
              }}>
                <span style={{
                  width: 22, height: 22, borderRadius: '50%', flexShrink: 0,
                  background: colors[a.status], color: '#fff',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 11, fontWeight: 700,
                }}>{a.id}</span>
                <span style={{ fontSize: 12, color: '#334155', lineHeight: 1.4 }}>{a.text}</span>
              </div>
            );
          })}
        </div>
      </Card>

      <Card style={{ padding: 16, flex: 1 }}>
        <SectionHeader title="Active Alerts" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {alerts.map(a => {
            const dotColors = { critical: '#DC2626', warning: '#F59E0B', 'in-progress': '#7C3AED', info: '#2563EB' };
            return (
              <div key={a.id} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 4 }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: dotColors[a.status] || '#6B7280' }} />
                  <span style={{ width: 1, height: 20, background: '#E2E8F0' }} />
                </div>
                <div>
                  <div style={{ fontSize: 12, color: '#334155', lineHeight: 1.4 }}>{a.message}</div>
                  <div style={{ fontSize: 10, color: '#94A3B8', marginTop: 2 }}>{a.timestamp}</div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

function TruckStatusBar() {
  return (
    <Card style={{ padding: 16 }}>
      <SectionHeader title="Truck Status Distribution" />
      <div style={{ height: 14, borderRadius: 7, display: 'flex', overflow: 'hidden', marginBottom: 10 }}>
        {Object.entries(statusBarData).map(([status, count]) => (
          <div key={status} style={{
            width: `${(count / totalTrucks) * 100}%`, height: '100%',
            background: statusBarColors[status],
          }} />
        ))}
      </div>
      <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
        {Object.entries(statusBarData).map(([status, count]) => (
          <div key={status} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11 }}>
            <span style={{ width: 8, height: 8, borderRadius: 2, background: statusBarColors[status] }} />
            <span style={{ color: '#64748B', textTransform: 'capitalize' }}>{status}</span>
            <span style={{ fontWeight: 600, color: '#334155' }}>{count}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

function PMBayMini() {
  return (
    <Card style={{ padding: 16 }}>
      <SectionHeader title="PM Bay Status" />
      {d.pmBayStatus.map(bay => (
        <div key={bay.bay} style={{ marginBottom: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
            <span><strong>{bay.bay}</strong>: {bay.truckId} {bay.type}</span>
            <span style={{ color: '#64748B' }}>{bay.remaining}</span>
          </div>
          <HealthBar value={bay.progress} color="#7C3AED" height={4} />
        </div>
      ))}
      <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
        <span style={{ fontSize: 11, color: '#64748B' }}>Queue:</span>
        {d.pmBayQueue.map(id => (
          <span key={id} style={{
            fontSize: 11, fontWeight: 600, color: '#B45309',
            background: '#FFFBEB', padding: '2px 8px', borderRadius: 4,
            border: '1px solid #FDE68A',
          }}>{id}</span>
        ))}
      </div>
    </Card>
  );
}

export default function OverviewPage() {
  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* KPI Row */}
      <div style={{ display: 'flex', gap: 16 }}>
        <KpiCard label="Demand Fulfillment" value={`${d.demandFulfillment}%`} sublabel={`${d.completedLoads} / ${d.dailyDemand} loads`} color="#8A4931" icon={<Target size={20} />} definition="Completed loads / daily demand target" />
        <KpiCard label="Available Trucks" value={d.availableTrucks} sublabel={`of ${d.totalTrucks} total`} color="#16A34A" icon={<Truck size={20} />} definition="Trucks not in PM or standby" />
        <KpiCard label="Trucks in PM" value={d.trucksInPM} sublabel={`${d.activePM} active + ${d.queuedPM} queued`} color="#7C3AED" icon={<Wrench size={20} />} definition="Trucks currently in PM bay or queue" />
        <KpiCard label="PM Cost" value={`₩${d.pmCostMKRW}M`} sublabel="Today shift total" icon={<DollarSign size={20} />} definition="Today shift maintenance cost" />
        <KpiCard label="Risk Trucks" value={d.riskTrucks} sublabel="HI below 60%" color="#DC2626" icon={<AlertTriangle size={20} />} definition="Trucks with Health Index below 60%" />
      </div>

      {/* Main content: Map + Decision panel */}
      <div style={{ display: 'flex', gap: 20 }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <MineMap />
          <div style={{ display: 'flex', gap: 16 }}>
            <div style={{ flex: 1 }}>
              <Card style={{ padding: 16, height: '100%' }}>
                <SectionHeader title="Demand vs Completed (Cumulative)" />
                <ResponsiveContainer width="100%" height={200}>
                  <ComposedChart data={demandChartData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                    <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                    <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} domain={[0, 110]} />
                    <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
                    <Area type="monotone" dataKey="demand" stroke="#94A3B8" strokeDasharray="6 3" fill="none" name="Demand" />
                    <Area type="monotone" dataKey="completed" stroke="#8A4931" fill="#8A4931" fillOpacity={0.06} strokeWidth={2} name="Completed" dot={{ r: 3, fill: '#8A4931' }} />
                  </ComposedChart>
                </ResponsiveContainer>
              </Card>
            </div>
            <div style={{ width: 240, display: 'flex', flexDirection: 'column', gap: 16 }}>
              <TruckStatusBar />
              <PMBayMini />
            </div>
          </div>
        </div>
        <DecisionPanel />
      </div>
    </div>
  );
}
