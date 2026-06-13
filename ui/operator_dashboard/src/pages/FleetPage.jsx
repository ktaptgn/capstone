import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import Card from '../components/Card';
import StatusBadge from '../components/StatusBadge';
import HealthBar, { getHIColor, getHIStatus } from '../components/HealthBar';
import ProgressRing from '../components/ProgressRing';
import SectionHeader from '../components/SectionHeader';
import { trucks } from '../data/trucks';
import { todayPM, pmHistory } from '../data/pmSchedule';
import { dashboardKpis } from '../data/dashboardKpis';

const tireDistData = [
  { name: 'Normal', range: '80%+', count: trucks.filter(t => t.tireHI >= 80).length, color: '#16A34A' },
  { name: 'Watch', range: '60-79%', count: trucks.filter(t => t.tireHI >= 60 && t.tireHI < 80).length, color: '#D97706' },
  { name: 'Warning', range: '40-59%', count: trucks.filter(t => t.tireHI >= 40 && t.tireHI < 60).length, color: '#F59E0B' },
  { name: 'Critical', range: '<40%', count: trucks.filter(t => t.tireHI < 40).length, color: '#DC2626' },
];

function FleetGrid({ selectedId, onSelect }) {
  const rows = [];
  for (let i = 0; i < trucks.length; i += 5) rows.push(trucks.slice(i, i + 5));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {rows.map((row, ri) => (
        <div key={ri} style={{ display: 'flex', gap: 6 }}>
          {row.map(t => {
            const sel = t.id === selectedId;
            const hiColor = getHIColor(t.healthIndex);
            return (
              <div key={t.id} onClick={() => onSelect(t.id)} style={{
                flex: 1, padding: '8px 6px', borderRadius: 8, cursor: 'pointer',
                background: sel ? '#F3E7E2' : '#fff',
                border: sel ? '2px solid #8A4931' : '1px solid #E2E8F0',
                textAlign: 'center', transition: 'all 0.15s',
              }}>
                <div style={{ fontSize: 10, color: '#64748B', fontWeight: 500 }}>{t.id}</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: hiColor }}>{t.healthIndex}%</div>
                <StatusBadge status={t.status} size="sm" />
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

function TruckDetail({ truck }) {
  if (!truck) return null;
  const tires = [
    { name: 'Front Left', hi: truck.frontLeftTireHI },
    { name: 'Front Right', hi: truck.frontRightTireHI },
    { name: 'Rear Left', hi: truck.rearLeftTireHI },
    { name: 'Rear Right', hi: truck.rearRightTireHI },
  ];
  const history = pmHistory[truck.id] || [];

  return (
    <div style={{ width: 300, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <Card style={{ padding: 16, background: '#F3E7E2', border: '1px solid #E7D0C6' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 22, fontWeight: 700, color: '#1E293B' }}>{truck.id}</span>
              <StatusBadge status={truck.status} size="md" />
            </div>
            <div style={{ fontSize: 11, color: '#64748B', marginTop: 4 }}>Mining Haul Truck · 797F-class</div>
          </div>
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ProgressRing value={truck.healthIndex} size={56} />
            <span style={{ position: 'absolute', fontSize: 14, fontWeight: 700, color: getHIColor(truck.healthIndex) }}>
              {truck.healthIndex}%
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
          <div style={{ flex: 1, background: '#fff', borderRadius: 6, padding: '6px 10px' }}>
            <div style={{ fontSize: 9, color: '#94A3B8', textTransform: 'uppercase' }}>Location</div>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#334155' }}>{truck.location}</div>
          </div>
          <div style={{ flex: 1, background: '#fff', borderRadius: 6, padding: '6px 10px' }}>
            <div style={{ fontSize: 9, color: '#94A3B8', textTransform: 'uppercase' }}>PM Due</div>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#334155' }}>{truck.pmDue || '—'}</div>
          </div>
        </div>
      </Card>

      {/* Tire Health */}
      <Card style={{ padding: 16 }}>
        <SectionHeader title="Tire Health" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {tires.map(tire => (
            <div key={tire.name}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <div style={{
                  width: 28, height: 28, borderRadius: '50%',
                  border: `3px solid ${getHIColor(tire.hi)}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 8, fontWeight: 600, color: getHIColor(tire.hi),
                }}>
                  {tire.hi}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 12, fontWeight: 500 }}>{tire.name}</span>
                    <StatusBadge status={getHIStatus(tire.hi)} />
                  </div>
                </div>
              </div>
              <HealthBar value={tire.hi} height={4} />
            </div>
          ))}
        </div>
      </Card>

      {/* PM History */}
      <Card style={{ padding: 16 }}>
        <SectionHeader title="PM History" />
        {history.length === 0 ? (
          <div style={{ fontSize: 12, color: '#94A3B8' }}>No history available</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {history.map((h, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 12 }}>
                <div>
                  <span style={{ color: '#94A3B8', marginRight: 8 }}>{h.date}</span>
                  <span style={{ color: '#334155' }}>{h.type}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <StatusBadge status={h.result} />
                  <span style={{ color: '#64748B', fontSize: 11 }}>{h.duration}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

export default function FleetPage() {
  const [selectedTruck, setSelectedTruck] = useState('T07');
  const truck = trucks.find(t => t.id === selectedTruck);
  const d = dashboardKpis;

  const riskTrucks = trucks.filter(t => t.healthIndex < 60).sort((a, b) => a.healthIndex - b.healthIndex);

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ display: 'flex', gap: 20 }}>
        {/* Left - Fleet Grid + Charts */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Card style={{ padding: 16 }}>
            <div style={{ marginBottom: 12 }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: '#1E293B' }}>Fleet Health Grid</h3>
              <div style={{ fontSize: 11, color: '#64748B' }}>25 trucks · {trucks.filter(t => t.status === 'critical').length} Critical · {trucks.filter(t => t.status === 'warning').length} Warning</div>
            </div>
            <FleetGrid selectedId={selectedTruck} onSelect={setSelectedTruck} />
          </Card>

          <div style={{ display: 'flex', gap: 16 }}>
            <Card style={{ padding: 16, flex: 1 }}>
              <SectionHeader title="Tire HI Distribution" />
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={tireDistData} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#64748B' }} width={60} />
                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={16}>
                    {tireDistData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card style={{ padding: 16, flex: 1 }}>
              <SectionHeader title="PM Bay Queue" />
              {d.pmBayStatus.map(bay => (
                <div key={bay.bay} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                    <div>
                      <span style={{ fontWeight: 600 }}>{bay.bay}</span>: {bay.truckId} / {bay.type}
                    </div>
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
                    background: '#FFFBEB', padding: '2px 8px', borderRadius: 4, border: '1px solid #FDE68A',
                  }}>{id}</span>
                ))}
              </div>
            </Card>
          </div>

          <div style={{ display: 'flex', gap: 16 }}>
            {/* PM Schedule Timeline */}
            <Card style={{ padding: 16, flex: 1 }}>
              <SectionHeader title="PM Schedule Timeline" />
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #E2E8F0' }}>
                    {['Time','Truck','Type','Status','Duration'].map(h => (
                      <th key={h} style={{ padding: '6px 8px', textAlign: 'left', color: '#94A3B8', fontSize: 10, fontWeight: 600, textTransform: 'uppercase' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {todayPM.map(pm => (
                    <tr key={pm.truckId} style={{ borderBottom: '1px solid #F1F5F9' }}>
                      <td style={{ padding: '8px' }}>{pm.time}</td>
                      <td style={{ padding: '8px', fontWeight: 600 }}>{pm.truckId}</td>
                      <td style={{ padding: '8px' }}>{pm.type}</td>
                      <td style={{ padding: '8px' }}><StatusBadge status={pm.status} /></td>
                      <td style={{ padding: '8px', color: '#64748B' }}>{pm.duration}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>

            {/* Risk Trucks */}
            <Card style={{ padding: 16, width: 280, flexShrink: 0 }}>
              <SectionHeader title="Risk Trucks" action={`${riskTrucks.length} trucks`} />
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {riskTrucks.map(t => (
                  <div key={t.id} style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '6px 8px', borderRadius: 6, background: '#FEF2F2',
                    cursor: 'pointer',
                  }} onClick={() => setSelectedTruck(t.id)}>
                    <div>
                      <span style={{ fontWeight: 600, fontSize: 12 }}>{t.id}</span>
                      <span style={{ fontSize: 11, color: '#64748B', marginLeft: 8 }}>{t.location}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ fontWeight: 700, fontSize: 13, color: getHIColor(t.healthIndex) }}>{t.healthIndex}%</span>
                      <StatusBadge status={t.status} />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>

        {/* Right - Truck Detail */}
        <TruckDetail truck={truck} />
      </div>
    </div>
  );
}
