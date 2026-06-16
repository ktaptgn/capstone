import { useReducer, useEffect, useState } from 'react';
import {
  Play, Pause, RotateCcw, Wrench, TrendingUp, Shuffle, Gauge, Truck, AlertTriangle, Clock, Activity,
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import Card from '../components/Card';
import SectionHeader from '../components/SectionHeader';
import { policies } from '../data/policies';
import {
  simReducer, createInitialState, fmtClock, TICK_MIN, FLEET_SIZE, HEURISTIC_LABEL,
} from '../data/realtimeSim';

const POLICY_COLOR = Object.fromEntries(policies.map((p) => [p.id, p.color]));
const HEURISTICS = ['H1', 'H2', 'H3', 'H4'];

const LOG_STYLE = {
  info: { color: '#475569', dot: '#94A3B8' },
  action: { color: '#1D4ED8', dot: '#3B82F6' },
  good: { color: '#15803D', dot: '#22C55E' },
  warn: { color: '#B45309', dot: '#F59E0B' },
};

function hiColor(v) {
  if (v >= 85) return '#16A34A';
  if (v >= 70) return '#F59E0B';
  return '#DC2626';
}

function KpiTile({ icon: Icon, label, value, sub, color = '#1E293B' }) {
  return (
    <Card style={{ padding: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#94A3B8' }}>
        {Icon && <Icon size={14} />}
        <span style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase' }}>{label}</span>
      </div>
      <div style={{ fontSize: 24, fontWeight: 800, color, marginTop: 6 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: '#64748B', marginTop: 2 }}>{sub}</div>}
    </Card>
  );
}

function ActionButton({ icon: Icon, label, desc, color, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        display: 'flex', alignItems: 'center', gap: 12, width: '100%', textAlign: 'left',
        padding: '12px 14px', borderRadius: 10, cursor: 'pointer', fontFamily: 'inherit',
        border: '1px solid #E2E8F0', background: '#fff', transition: 'all 0.12s',
      }}
      onMouseEnter={(e) => { e.currentTarget.style.background = `${color}0C`; e.currentTarget.style.borderColor = `${color}66`; }}
      onMouseLeave={(e) => { e.currentTarget.style.background = '#fff'; e.currentTarget.style.borderColor = '#E2E8F0'; }}
    >
      <div style={{ width: 34, height: 34, borderRadius: 8, background: `${color}14`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
        <Icon size={18} color={color} />
      </div>
      <div>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#1E293B' }}>{label}</div>
        <div style={{ fontSize: 11, color: '#64748B', marginTop: 1 }}>{desc}</div>
      </div>
    </button>
  );
}

export default function RealtimeSimPage() {
  const [state, dispatch] = useReducer(simReducer, 'H3', createInitialState);
  const [running, setRunning] = useState(false);
  const [speed, setSpeed] = useState(2);

  useEffect(() => {
    if (!running) return undefined;
    const iv = setInterval(() => dispatch({ type: 'TICK', dt: TICK_MIN * speed }), 800);
    return () => clearInterval(iv);
  }, [running, speed]);

  const k = state.kpis;
  const policyColor = POLICY_COLOR[state.activeHeuristic] || '#8A4931';
  const pmActive = state.pmJobs.length;
  const pmQueue = Math.round(k.pmQueue);
  const available = FLEET_SIZE - pmActive - pmQueue;

  const chartData = state.history.map((h) => ({ name: fmtClock(h.t), '수요 충족률': h.demand, '평균 HI': h.fleetHI }));

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header / transport */}
      <Card style={{ padding: 18 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: '#1E293B', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Activity size={20} color={policyColor} /> 실시간 시뮬레이션
            </h2>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: '#64748B' }}>
              휴리스틱을 실시간으로 바꾸거나 PM·배차를 지시하면 운영 KPI가 규칙에 따라 즉시 반응합니다.
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 22, fontWeight: 800, color: '#1E293B' }}>
              <Clock size={18} color="#94A3B8" /> {fmtClock(state.clock)}
            </div>
            <div style={{ display: 'flex', gap: 4 }}>
              {[1, 2, 4].map((sp) => (
                <button key={sp} onClick={() => setSpeed(sp)} style={{
                  padding: '6px 10px', borderRadius: 6, border: '1px solid #E2E8F0', cursor: 'pointer', fontFamily: 'inherit',
                  background: speed === sp ? '#1E293B' : '#fff', color: speed === sp ? '#fff' : '#64748B', fontSize: 12, fontWeight: 700,
                }}>{sp}×</button>
              ))}
            </div>
            <button onClick={() => setRunning((r) => !r)} style={{
              display: 'flex', alignItems: 'center', gap: 6, padding: '8px 18px', borderRadius: 8, border: 'none', cursor: 'pointer',
              background: running ? '#B45309' : '#16A34A', color: '#fff', fontWeight: 700, fontSize: 13, fontFamily: 'inherit',
            }}>
              {running ? <Pause size={16} /> : <Play size={16} />}{running ? '일시정지' : '재생'}
            </button>
            <button onClick={() => { setRunning(false); dispatch({ type: 'RESET' }); }} style={{
              display: 'flex', alignItems: 'center', gap: 5, padding: '8px 12px', borderRadius: 8, border: '1px solid #E2E8F0',
              background: '#fff', color: '#334155', fontWeight: 700, fontSize: 13, cursor: 'pointer', fontFamily: 'inherit',
            }}>
              <RotateCcw size={15} /> 리셋
            </button>
          </div>
        </div>

        {/* Active heuristic switch */}
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: 8 }}>활성 휴리스틱 (실시간 전환)</div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {HEURISTICS.map((id) => {
              const active = id === state.activeHeuristic;
              const c = POLICY_COLOR[id];
              return (
                <button key={id} onClick={() => dispatch({ type: 'SET_HEURISTIC', id })} style={{
                  padding: '8px 14px', borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit',
                  border: active ? `2px solid ${c}` : '1px solid #E2E8F0', background: active ? `${c}12` : '#fff',
                  display: 'flex', alignItems: 'center', gap: 8,
                }}>
                  <span style={{ fontSize: 14, fontWeight: 800, color: c }}>{id}</span>
                  <span style={{ fontSize: 11, color: '#64748B' }}>{HEURISTIC_LABEL[id]}</span>
                </button>
              );
            })}
          </div>
        </div>
      </Card>

      {/* Live KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
        <KpiTile icon={Gauge} label="수요 충족률" value={`${Math.round(k.demandFulfillment)}%`} color={k.demandFulfillment >= 85 ? '#16A34A' : k.demandFulfillment >= 75 ? '#F59E0B' : '#DC2626'} sub="목표 대비 처리" />
        <KpiTile icon={Activity} label="평균 건전성(HI)" value={`${Math.round(k.fleetHI)}%`} color={hiColor(k.fleetHI)} sub="전 차량 평균" />
        <KpiTile icon={AlertTriangle} label="위험 차량" value={`${Math.round(k.riskTrucks)}대`} color={k.riskTrucks >= 4 ? '#DC2626' : k.riskTrucks >= 2 ? '#F59E0B' : '#16A34A'} sub="임계 근접" />
        <KpiTile icon={Truck} label="가용 차량" value={`${available} / ${FLEET_SIZE}`} sub={`정비 중 ${pmActive + pmQueue}대`} />
        <KpiTile icon={Wrench} label="PM Bay" value={`${pmActive} / 2`} color={pmActive >= 2 ? '#F59E0B' : '#1E293B'} sub={`대기열 ${pmQueue}대`} />
        <KpiTile icon={TrendingUp} label="처리량" value={`${Math.round(k.throughput)}`} sub="loads / hr" />
        <KpiTile icon={Gauge} label="비용 지수" value={k.costRate.toFixed(2)} color={k.costRate <= 1.05 ? '#16A34A' : k.costRate <= 1.2 ? '#F59E0B' : '#DC2626'} sub="기준 H3 = 1.00" />
        <KpiTile icon={Truck} label="누적 생산" value={`${Math.round(k.cumLoads)}`} sub="loads (교대 누적)" />
      </div>

      {/* Chart + actions + log */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 16 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Card style={{ padding: 18 }}>
            <SectionHeader title="실시간 추이" />
            <ResponsiveContainer width="100%" height={210}>
              <LineChart data={chartData} margin={{ left: 0, right: 12, top: 6, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#94A3B8' }} minTickGap={28} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#94A3B8' }} unit="%" />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line type="monotone" dataKey="수요 충족률" stroke={policyColor} strokeWidth={2.5} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="평균 HI" stroke="#0891B2" strokeWidth={2} strokeDasharray="5 4" dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <Card style={{ padding: 18 }}>
            <SectionHeader title="운영자 지시" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <ActionButton icon={Wrench} color="#7C3AED" label="위험 차량 PM 투입" desc="위험 차량 1대를 PM Bay 대기열로 — 건전성 회복, 가용 일시 감소" onClick={() => dispatch({ type: 'PM_DISPATCH' })} />
              <ActionButton icon={TrendingUp} color="#2563EB" label="긴급 증차 (가동 우선)" desc="처리량·수요 충족률 즉시 상승, 건전성은 점차 하락" onClick={() => dispatch({ type: 'DISPATCH_PRODUCTION' })} />
              <ActionButton icon={Shuffle} color="#0891B2" label="경로 재배분 (혼잡 완화)" desc="흐름 개선으로 비용 지수 하락, 처리량 소폭 개선" onClick={() => dispatch({ type: 'DISPATCH_RELIEVE' })} />
            </div>
          </Card>
        </div>

        {/* Event log */}
        <Card style={{ padding: 18, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <SectionHeader title="이벤트 로그" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2, overflowY: 'auto', maxHeight: 470 }}>
            {state.log.map((entry, i) => {
              const st = LOG_STYLE[entry.type] || LOG_STYLE.info;
              return (
                <div key={`${entry.t}-${i}`} style={{ display: 'flex', gap: 10, padding: '7px 4px', borderBottom: '1px solid #F8FAFC' }}>
                  <span style={{ fontSize: 11, fontVariantNumeric: 'tabular-nums', color: '#94A3B8', fontWeight: 700, flexShrink: 0, width: 38 }}>{fmtClock(entry.t)}</span>
                  <span style={{ width: 7, height: 7, borderRadius: '50%', background: st.dot, flexShrink: 0, marginTop: 5 }} />
                  <span style={{ fontSize: 12, color: st.color, lineHeight: 1.4 }}>{entry.text}</span>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    </div>
  );
}
