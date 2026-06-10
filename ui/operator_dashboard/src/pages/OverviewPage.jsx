import { useState, useMemo } from 'react';
import { Target, Truck, Wrench, DollarSign, AlertTriangle, X, Send } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Line, ComposedChart } from 'recharts';
import KpiCard from '../components/KpiCard';
import Card from '../components/Card';
import StatusBadge from '../components/StatusBadge';
import HealthBar from '../components/HealthBar';
import MineMap from '../components/MineMap';
import SectionHeader from '../components/SectionHeader';
import { dashboardKpis } from '../data/dashboardKpis';
import { generateDaySnapshot } from '../data/simulationData';
import { alerts, recommendedActions } from '../data/alerts';
import { usePmOrders } from '../lib/usePmOrders';
import { publishOrder, decideOrder } from '../lib/pmSyncBus';
import DecisionRecommendationPanel from '../components/DecisionRecommendationPanel';
import { HeuristicExplainModal } from '../components/HeuristicExplainTable';
import MapInsightsPanel from '../components/MapInsightsPanel';
import ScenarioToggle from '../components/ScenarioToggle';
import { OVERVIEW_SCENARIOS } from '../data/overviewScenarios';
const statusBarColors = { running: '#16A34A', standby: '#6B7280', pm: '#7C3AED', warning: '#F59E0B', critical: '#DC2626' };

const TRUCK_IDS = Array.from({ length: 25 }, (_, i) => `T${String(i + 1).padStart(2, '0')}`);
const PM_TYPES = [
  { value: 'tire_pm', label: '타이어 정비' },
  { value: 'brake_check', label: '브레이크 점검' },
  { value: 'suspension', label: '서스펜션 점검' },
  { value: 'full_pm', label: '종합 정비' },
  { value: 'drive_unit', label: '구동부 정비' },
  { value: 'inspection', label: '정기 점검' },
];

const PM_STATUS_CFG = {
  requested:   { label: '요청', color: '#2563EB', bg: '#EFF6FF' },
  approved:    { label: '승인·전송', color: '#16A34A', bg: '#DCFCE7' },
  accepted:    { label: '접수됨', color: '#0891B2', bg: '#ECFEFF' },
  in_progress: { label: '작업 중', color: '#7C3AED', bg: '#F5F3FF' },
  completed:   { label: '완료', color: '#16A34A', bg: '#DCFCE7' },
  delayed:     { label: '지연', color: '#D97706', bg: '#FEF3C7' },
  hold:        { label: '보류', color: '#D97706', bg: '#FEF3C7' },
  rejected:    { label: '거절', color: '#DC2626', bg: '#FEE2E2' },
};

function PMWorkOrderLive({ orders }) {
  const sorted = [...orders].sort((a, b) => b.updatedAt - a.updatedAt);

  return (
    <Card style={{ padding: 16 }}>
      <SectionHeader title="실시간 PM 작업 지시" />
      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 10 }}>
        PM 작업자 앱과 실시간 연동됩니다.
      </div>
      {sorted.length === 0 ? (
        <div style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
          진행 중인 PM 작업 지시가 없습니다.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {sorted.map(order => {
            const cfg = PM_STATUS_CFG[order.status] || PM_STATUS_CFG.requested;
            return (
              <div key={order.id} style={{
                padding: 10, borderRadius: 8,
                border: '1px solid var(--border)', background: 'var(--bg-card)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-main)' }}>{order.truckId}</span>
                    <span style={{ fontSize: 11, color: 'var(--text-sub)' }}>{order.pmType}</span>
                  </div>
                  <span style={{
                    fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 10,
                    background: cfg.bg, color: cfg.color,
                  }}>{cfg.label}</span>
                </div>
                {order.reason && (
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>{order.reason}</div>
                )}
                <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 4 }}>
                  {order.origin === 'dashboard' ? '관제 발행' : 'PM앱 발행'}
                  {order.status !== 'requested' && order.decidedBy && (
                    <> · {order.decidedBy === 'pm' ? 'PM 작업자' : '관제'} 결정 {order.decidedAt || ''}</>
                  )}
                </div>
                {order.status === 'requested' && (
                  <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
                    <button
                      onClick={() => decideOrder(order.id, 'approved', 'dashboard')}
                      style={{ flex: 1, padding: '5px 0', borderRadius: 6, border: 'none', fontSize: 10, fontWeight: 700, color: '#fff', cursor: 'pointer', background: '#16A34A', fontFamily: 'inherit' }}
                    >승인</button>
                    <button
                      onClick={() => decideOrder(order.id, 'hold', 'dashboard')}
                      style={{ flex: 1, padding: '5px 0', borderRadius: 6, border: 'none', fontSize: 10, fontWeight: 700, color: '#fff', cursor: 'pointer', background: '#D97706', fontFamily: 'inherit' }}
                    >보류</button>
                    <button
                      onClick={() => decideOrder(order.id, 'rejected', 'dashboard')}
                      style={{ flex: 1, padding: '5px 0', borderRadius: 6, border: 'none', fontSize: 10, fontWeight: 700, color: '#fff', cursor: 'pointer', background: '#DC2626', fontFamily: 'inherit' }}
                    >거절</button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}

function DecisionPanel({ onDecision }) {
  // Live shared PM work orders (synced with the PM worker app)
  const pmOrders = usePmOrders();
  // Per-action decision states: approve / hold / reject
  const [actionStates, setActionStates] = useState({});
  // PM Dispatch modal
  const [showPMDispatch, setShowPMDispatch] = useState(false);
  const [dispatchTruck, setDispatchTruck] = useState('T01');
  const [dispatchPMType, setDispatchPMType] = useState('tire_pm');
  const [dispatchReason, setDispatchReason] = useState('');
  const [dispatchSent, setDispatchSent] = useState(false);
  // Policy approval dialog
  const [showPolicyApproval, setShowPolicyApproval] = useState(false);
  const [policyApproved, setPolicyApproved] = useState(null);

  const handleActionDecision = (actionId, decision, actionText) => {
    setActionStates(prev => ({ ...prev, [actionId]: decision }));
    if (onDecision) onDecision(actionId, actionText, decision);
  };

  const handleDispatchSend = () => {
    const pmTypeLabel = PM_TYPES.find(p => p.value === dispatchPMType)?.label || dispatchPMType;
    publishOrder({
      truckId: dispatchTruck,
      pmType: pmTypeLabel,
      reason: dispatchReason.trim(),
      priority: 'HIGH',
      estimatedDuration: '-',
      origin: 'dashboard',
      status: 'requested',
    });
    setDispatchSent(true);
    setTimeout(() => {
      setShowPMDispatch(false);
      setDispatchSent(false);
      setDispatchReason('');
    }, 1500);
  };

  const btnStyle = (bg) => ({
    padding: '4px 10px', borderRadius: 6, border: 'none',
    fontSize: 10, fontWeight: 700, color: '#fff', cursor: 'pointer',
    background: bg, fontFamily: 'inherit',
  });

  return (
    <div style={{ width: 300, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Card style={{ padding: 16 }}>
        <SectionHeader title="Recommended Actions" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {recommendedActions.map(a => {
            const colors = { critical: '#DC2626', warning: '#F59E0B', standby: '#6B7280' };
            const bgs = { critical: '#FEF2F2', warning: '#FFFBEB', standby: '#F9FAFB' };
            const decision = actionStates[a.id];

            return (
              <div key={a.id} style={{
                padding: 10, borderRadius: 8,
                background: bgs[a.status], border: `1px solid ${colors[a.status]}20`,
              }}>
                <div style={{ display: 'flex', gap: 10, marginBottom: 8 }}>
                  <span style={{
                    width: 22, height: 22, borderRadius: '50%', flexShrink: 0,
                    background: colors[a.status], color: '#fff',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 11, fontWeight: 700,
                  }}>{a.id}</span>
                  <span style={{ fontSize: 12, color: 'var(--text-body)', lineHeight: 1.4 }}>{a.text}</span>
                </div>

                {/* Decision buttons or result badge */}
                {decision ? (
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    padding: '4px 8px', borderRadius: 6,
                    background: decision === 'approved' ? '#DCFCE7' : decision === 'hold' ? '#FEF3C7' : '#FEE2E2',
                    fontSize: 11, fontWeight: 700,
                    color: decision === 'approved' ? '#16A34A' : decision === 'hold' ? '#D97706' : '#DC2626',
                  }}>
                    {decision === 'approved' ? '✓ 승인됨' : decision === 'hold' ? '⏸ 보류됨' : '✗ 거절됨'}
                  </div>
                ) : (
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button style={btnStyle('#16A34A')} onClick={() => handleActionDecision(a.id, 'approved', a.text)}>승인</button>
                    <button style={btnStyle('#D97706')} onClick={() => handleActionDecision(a.id, 'hold', a.text)}>보류</button>
                    <button style={btnStyle('#DC2626')} onClick={() => handleActionDecision(a.id, 'rejected', a.text)}>거절</button>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* PM Dispatch button */}
        <button
          onClick={() => setShowPMDispatch(true)}
          style={{
            marginTop: 12, width: '100%', padding: '8px 0', borderRadius: 8,
            border: '1px solid #7C3AED', background: '#F5F3FF', color: '#7C3AED',
            fontSize: 12, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
          }}
        >
          <Send size={14} /> 긴급 PM 배차
        </button>

        {/* Policy Approval button */}
        <button
          onClick={() => setShowPolicyApproval(true)}
          style={{
            marginTop: 8, width: '100%', padding: '8px 0', borderRadius: 8,
            border: '1px solid #8A4931', background: '#F3E7E2', color: '#8A4931',
            fontSize: 12, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit',
          }}
        >
          정책 승인
        </button>
      </Card>

      <PMWorkOrderLive orders={pmOrders} />

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
                  <div style={{ fontSize: 12, color: 'var(--text-body)', lineHeight: 1.4 }}>{a.message}</div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{a.timestamp}</div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* ── PM Dispatch Modal ── */}
      {showPMDispatch && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
        }}>
          <div style={{
            background: 'var(--bg-card)', borderRadius: 12, padding: 24, width: 340,
            boxShadow: '0 20px 60px rgba(15,23,42,0.25)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: 'var(--text-main)' }}>긴급 PM 배차</h3>
              <button onClick={() => setShowPMDispatch(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}>
                <X size={18} color="#94A3B8" />
              </button>
            </div>

            {dispatchSent ? (
              <div style={{ textAlign: 'center', padding: '20px 0', color: '#16A34A', fontSize: 14, fontWeight: 600 }}>
                ✓ PM 배차 요청이 전송되었습니다
              </div>
            ) : (
              <>
                <div style={{ marginBottom: 12 }}>
                  <label style={{ fontSize: 11, color: 'var(--text-sub)', fontWeight: 600, display: 'block', marginBottom: 4 }}>대상 트럭</label>
                  <select
                    value={dispatchTruck}
                    onChange={e => setDispatchTruck(e.target.value)}
                    style={{
                      width: '100%', padding: '8px 10px', borderRadius: 6,
                      border: '1px solid var(--border)', fontSize: 13, fontFamily: 'inherit',
                      color: 'var(--text-body)', background: 'var(--divider)',
                    }}
                  >
                    {TRUCK_IDS.map(id => <option key={id} value={id}>{id}</option>)}
                  </select>
                </div>

                <div style={{ marginBottom: 12 }}>
                  <label style={{ fontSize: 11, color: 'var(--text-sub)', fontWeight: 600, display: 'block', marginBottom: 4 }}>PM 유형</label>
                  <select
                    value={dispatchPMType}
                    onChange={e => setDispatchPMType(e.target.value)}
                    style={{
                      width: '100%', padding: '8px 10px', borderRadius: 6,
                      border: '1px solid var(--border)', fontSize: 13, fontFamily: 'inherit',
                      color: 'var(--text-body)', background: 'var(--divider)',
                    }}
                  >
                    {PM_TYPES.map(pt => <option key={pt.value} value={pt.value}>{pt.label}</option>)}
                  </select>
                </div>

                <div style={{ marginBottom: 16 }}>
                  <label style={{ fontSize: 11, color: 'var(--text-sub)', fontWeight: 600, display: 'block', marginBottom: 4 }}>사유</label>
                  <textarea
                    value={dispatchReason}
                    onChange={e => setDispatchReason(e.target.value)}
                    placeholder="긴급 PM 사유를 입력하세요..."
                    rows={3}
                    style={{
                      width: '100%', padding: '8px 10px', borderRadius: 6,
                      border: '1px solid var(--border)', fontSize: 12, fontFamily: 'inherit',
                      color: 'var(--text-body)', resize: 'none', background: 'var(--divider)',
                      boxSizing: 'border-box',
                    }}
                  />
                </div>

                <button
                  onClick={handleDispatchSend}
                  disabled={!dispatchReason.trim()}
                  style={{
                    width: '100%', padding: '10px 0', borderRadius: 8,
                    border: 'none', background: dispatchReason.trim() ? '#7C3AED' : '#CBD5E1',
                    color: '#fff', fontSize: 13, fontWeight: 700, cursor: dispatchReason.trim() ? 'pointer' : 'default',
                    fontFamily: 'inherit', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                  }}
                >
                  <Send size={14} /> PM 배차 전송
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* ── Policy Approval Dialog ── */}
      {showPolicyApproval && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
        }}>
          <div style={{
            background: 'var(--bg-card)', borderRadius: 12, padding: 24, width: 320,
            boxShadow: '0 20px 60px rgba(15,23,42,0.25)', textAlign: 'center',
          }}>
            {policyApproved === null ? (
              <>
                <div style={{
                  width: 48, height: 48, borderRadius: '50%', background: '#F3E7E2',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 16px',
                }}>
                  <AlertTriangle size={24} color="#8A4931" />
                </div>
                <h3 style={{ margin: '0 0 8px', fontSize: 15, fontWeight: 700, color: 'var(--text-main)' }}>
                  정책 승인 확인
                </h3>
                <p style={{ margin: '0 0 20px', fontSize: 13, color: 'var(--text-sub)', lineHeight: 1.5 }}>
                  해당 정책을 승인하겠습니까?
                </p>
                <div style={{ display: 'flex', gap: 10 }}>
                  <button
                    onClick={() => setPolicyApproved(true)}
                    style={{
                      flex: 1, padding: '10px 0', borderRadius: 8,
                      border: 'none', background: '#16A34A', color: '#fff',
                      fontSize: 14, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit',
                    }}
                  >
                    YES
                  </button>
                  <button
                    onClick={() => setPolicyApproved(false)}
                    style={{
                      flex: 1, padding: '10px 0', borderRadius: 8,
                      border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text-sub)',
                      fontSize: 14, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit',
                    }}
                  >
                    NO
                  </button>
                </div>
              </>
            ) : (
              <>
                <div style={{
                  width: 48, height: 48, borderRadius: '50%',
                  background: policyApproved ? '#DCFCE7' : '#FEE2E2',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 16px',
                }}>
                  {policyApproved
                    ? <span style={{ fontSize: 24 }}>✓</span>
                    : <X size={24} color="#DC2626" />
                  }
                </div>
                <h3 style={{ margin: '0 0 8px', fontSize: 15, fontWeight: 700, color: 'var(--text-main)' }}>
                  {policyApproved ? '정책이 승인되었습니다' : '정책 승인이 거절되었습니다'}
                </h3>
                <button
                  onClick={() => { setShowPolicyApproval(false); setPolicyApproved(null); }}
                  style={{
                    marginTop: 16, padding: '8px 24px', borderRadius: 8,
                    border: '1px solid var(--border)', background: 'var(--divider)', color: 'var(--text-body)',
                    fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
                  }}
                >
                  닫기
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function TruckStatusBar({ statusBarData, totalTrucks }) {
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
            <span style={{ color: 'var(--text-sub)', textTransform: 'capitalize' }}>{status}</span>
            <span style={{ fontWeight: 600, color: 'var(--text-body)' }}>{count}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

function PMBayMini({ data }) {
  return (
    <Card style={{ padding: 16 }}>
      <SectionHeader title="PM Bay Status" />
      {data.pmBayStatus.map(bay => (
        <div key={bay.bay} style={{ marginBottom: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
            <span><strong>{bay.bay}</strong>: {bay.truckId} {bay.type}</span>
            <span style={{ color: 'var(--text-sub)' }}>{bay.remaining}</span>
          </div>
          <HealthBar value={bay.progress} color="#7C3AED" height={4} />
        </div>
      ))}
      <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
        <span style={{ fontSize: 11, color: 'var(--text-sub)' }}>Queue:</span>
        {data.pmBayQueue.map(id => (
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

export default function OverviewPage({ timeSpeed = 1, resetNonce = 0, onDecision, simDate, isLive }) {
  // Use simulation snapshot for selected date, or live dashboardKpis
  const d = useMemo(() => {
    if (isLive || !simDate) return dashboardKpis;
    const snap = generateDaySnapshot(simDate);
    return {
      ...dashboardKpis,
      demandFulfillment: snap.demandFulfillment,
      completedLoads: snap.completedLoads,
      dailyDemand: snap.dailyDemand,
      availableTrucks: snap.availableTrucks,
      totalTrucks: 25,
      trucksInPM: snap.trucksInPM,
      activePM: Math.min(snap.trucksInPM, 2),
      queuedPM: Math.max(0, snap.trucksInPM - 2),
      pmCostMKRW: snap.pmCostMKRW,
      totalCostMKRW: snap.totalCostMKRW,
      riskTrucks: snap.riskTrucks,
      temperature: snap.temperature,
      date: snap.date,
      shift: snap.shift,
    };
  }, [simDate, isLive]);

  const demandChartData = d.demandTrend.hours.map((h, i) => ({
    hour: h, demand: d.demandTrend.demand[i],
    completed: Math.round(d.demandTrend.completed[i] * (d.demandFulfillment / dashboardKpis.demandFulfillment)),
  }));

  const statusBarData = d.truckStatusDistribution;
  const totalTrucks = Object.values(statusBarData).reduce((a, b) => a + b, 0);
  const [heuristicsOpen, setHeuristicsOpen] = useState(false);

  // Scenario toggle: overrides headline KPIs + injects map warnings
  const [scenarioId, setScenarioId] = useState('normal');
  const scenario = OVERVIEW_SCENARIOS.find(s => s.id === scenarioId) || OVERVIEW_SCENARIOS[0];
  const dd = { ...d, ...scenario.kpi };

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Scenario toggle */}
      <ScenarioToggle scenarioId={scenarioId} onChange={setScenarioId} />

      {/* KPI Row */}
      <div style={{ display: 'flex', gap: 16 }}>
        <KpiCard label="Demand Fulfillment" value={`${dd.demandFulfillment}%`} sublabel={`${dd.completedLoads} / ${dd.dailyDemand} loads`} color="#8A4931" icon={<Target size={20} />} definition="Completed loads / daily demand target" />
        <KpiCard label="Available Trucks" value={dd.availableTrucks} sublabel={`of ${dd.totalTrucks} total`} color="#16A34A" icon={<Truck size={20} />} definition="Trucks not in PM or standby" />
        <KpiCard label="Trucks in PM" value={dd.trucksInPM} sublabel={`${dd.activePM} active + ${dd.queuedPM} queued`} color="#7C3AED" icon={<Wrench size={20} />} definition="Trucks currently in PM bay or queue" />
        <KpiCard label="PM Cost" value={`₩${dd.pmCostMKRW}M`} sublabel="Today shift total" icon={<DollarSign size={20} />} definition="Today shift maintenance cost" />
        <KpiCard label="Risk Trucks" value={dd.riskTrucks} sublabel="HI below 60%" color="#DC2626" icon={<AlertTriangle size={20} />} definition="Trucks with Health Index below 60%" />
      </div>

      {/* Decision Recommendation — what decision, which heuristic, why, how to act */}
      <DecisionRecommendationPanel onDecision={onDecision} onShowHeuristics={() => setHeuristicsOpen(true)} />
      <HeuristicExplainModal open={heuristicsOpen} onClose={() => setHeuristicsOpen(false)} />

      {/* Main content: tall 3D map + status cards + Decision panel — equal height */}
      <div style={{ display: 'flex', gap: 20, alignItems: 'stretch' }}>
        {/* 3D map fills the row height (matches the Decision panel) and is narrower */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <MineMap key={`map-${resetNonce}`} timeSpeed={timeSpeed} fill />
        </div>
        {/* Status cards sit beside the map, narrowing it */}
        <div style={{ width: 250, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <TruckStatusBar statusBarData={statusBarData} totalTrucks={totalTrucks} />
          <PMBayMini data={d} />
        </div>
        <DecisionPanel onDecision={onDecision} />
      </div>

      {/* Secondary content: demand chart + route insights, full width */}
      <Card style={{ padding: 16 }}>
        <SectionHeader title="Demand vs Completed (Cumulative)" />
        <ResponsiveContainer width="100%" height={200}>
          <ComposedChart data={demandChartData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#94A3B8' }} />
            <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} domain={[0, 110]} />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid var(--border)' }} />
            <Area type="monotone" dataKey="demand" stroke="#94A3B8" strokeDasharray="6 3" fill="none" name="Demand" />
            <Area type="monotone" dataKey="completed" stroke="#8A4931" fill="#8A4931" fillOpacity={0.06} strokeWidth={2} name="Completed" dot={{ r: 3, fill: '#8A4931' }} />
          </ComposedChart>
        </ResponsiveContainer>
      </Card>
      <MapInsightsPanel scenarioWarnings={scenario.warnings} />
    </div>
  );
}
