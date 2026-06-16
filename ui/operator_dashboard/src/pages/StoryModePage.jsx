import { useState, useEffect, useMemo } from 'react';
import { Play, Pause, ChevronLeft, ChevronRight, RotateCcw, Flag } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import Card from '../components/Card';
import SectionHeader from '../components/SectionHeader';
import { policies } from '../data/policies';
import { buildStory, STORY_KPI_META } from '../data/storyMode';

const SEV = {
  info: { bg: '#EFF6FF', fg: '#1D4ED8', dot: '#3B82F6' },
  warning: { bg: '#FFFBEB', fg: '#B45309', dot: '#F59E0B' },
  high: { bg: '#FEF2F2', fg: '#B91C1C', dot: '#EF4444' },
};

const fmt = (v, unit) => (unit === 'M₩' ? `₩${v}M` : unit === '%' ? `${v}%` : `${v}${unit}`);

function PolicyPicker({ selected, onSelect }) {
  return (
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
      {policies.map((p) => {
        const active = p.id === selected;
        return (
          <button
            key={p.id}
            onClick={() => onSelect(p.id)}
            style={{
              padding: '10px 14px', borderRadius: 10, cursor: 'pointer', fontFamily: 'inherit',
              border: active ? `2px solid ${p.color}` : '1px solid #E2E8F0',
              background: active ? `${p.color}10` : '#fff', minWidth: 150, textAlign: 'left',
              transition: 'all 0.15s',
            }}
          >
            <div style={{ fontSize: 15, fontWeight: 800, color: p.color }}>{p.id}</div>
            <div style={{ fontSize: 11, color: '#64748B', marginTop: 2 }}>{p.name}</div>
          </button>
        );
      })}
    </div>
  );
}

function KpiDelta({ meta, value, prev }) {
  const delta = prev == null ? 0 : value - prev;
  const improved = meta.betterHigh ? delta > 0 : delta < 0;
  const color = delta === 0 ? '#94A3B8' : improved ? '#16A34A' : '#DC2626';
  const arrow = delta > 0 ? '▲' : delta < 0 ? '▼' : '–';
  return (
    <div style={{ border: '1px solid #E2E8F0', borderRadius: 10, padding: 12, background: '#fff' }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase' }}>{meta.label}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color: '#1E293B', marginTop: 4 }}>{fmt(value, meta.unit)}</div>
      <div style={{ fontSize: 11, fontWeight: 700, color, marginTop: 2 }}>
        {arrow} {delta > 0 ? '+' : ''}{Math.round(delta * 10) / 10}{meta.unit === '%' ? '%p' : ''}
      </div>
    </div>
  );
}

export default function StoryModePage() {
  const [policyId, setPolicyId] = useState('H3');
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);

  const story = useMemo(() => buildStory(policyId), [policyId]);
  const steps = story.steps;
  const last = steps.length - 1;
  const cur = steps[step];
  const prev = step > 0 ? steps[step - 1] : null;
  const isFinal = step === last;

  // Reset to start whenever the policy changes
  useEffect(() => { setStep(0); setPlaying(false); }, [policyId]);

  // Auto-play
  useEffect(() => {
    if (!playing) return;
    if (step >= last) { setPlaying(false); return; }
    const t = setTimeout(() => setStep((s) => Math.min(s + 1, last)), 2600);
    return () => clearTimeout(t);
  }, [playing, step, last]);

  const chartData = steps.slice(0, step + 1).map((s) => ({
    name: s.dayLabel,
    '수요 충족률': s.kpis.demandFulfill,
    '평균 HI': s.kpis.fleetHI,
  }));

  const sev = SEV[cur.event?.severity] || SEV.info;

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 18 }}>
      {/* Header + policy picker */}
      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16, flexWrap: 'wrap' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: '#1E293B' }}>스토리 모드</h2>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: '#64748B' }}>
              휴리스틱을 정책으로 선택하면 1년 운영을 단계별 이벤트로 따라가며 진행 상황과 결과를 확인합니다.
            </p>
          </div>
        </div>
        <div style={{ marginTop: 16 }}>
          <PolicyPicker selected={policyId} onSelect={setPolicyId} />
        </div>
      </Card>

      {/* Timeline */}
      <Card style={{ padding: '18px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {steps.map((s, i) => {
            const done = i <= step;
            const isCur = i === step;
            return (
              <div key={s.index} style={{ display: 'flex', alignItems: 'center', flex: i < last ? 1 : 0 }}>
                <button
                  onClick={() => { setStep(i); setPlaying(false); }}
                  title={s.title}
                  style={{
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
                    background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', padding: 0,
                  }}
                >
                  <div style={{
                    width: isCur ? 22 : 16, height: isCur ? 22 : 16, borderRadius: '50%',
                    background: done ? story.policy.color : '#E2E8F0',
                    border: isCur ? `3px solid ${story.policy.color}55` : 'none',
                    transition: 'all 0.2s',
                  }} />
                  <span style={{ fontSize: 10, fontWeight: isCur ? 800 : 600, color: isCur ? '#1E293B' : '#94A3B8', whiteSpace: 'nowrap' }}>
                    {s.dayLabel}
                  </span>
                </button>
                {i < last && (
                  <div style={{ flex: 1, height: 3, margin: '0 6px', marginBottom: 16, borderRadius: 2, background: i < step ? story.policy.color : '#E2E8F0' }} />
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Main: narrative + KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 18 }}>
        <Card style={{ padding: 22, borderLeft: `4px solid ${sev.dot}` }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: sev.bg, color: sev.fg, padding: '3px 10px', borderRadius: 999, fontSize: 11, fontWeight: 800 }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: sev.dot }} />
            {cur.event?.label}
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginTop: 12 }}>
            <span style={{ fontSize: 13, fontWeight: 800, color: story.policy.color }}>{cur.dayLabel}</span>
            <h3 style={{ margin: 0, fontSize: 20, fontWeight: 800, color: '#1E293B' }}>{cur.title}</h3>
          </div>
          <p style={{ fontSize: 14, color: '#475569', lineHeight: 1.6, marginTop: 10 }}>{cur.scenario}</p>

          <div style={{ marginTop: 16, padding: 14, borderRadius: 10, background: `${story.policy.color}0A`, border: `1px solid ${story.policy.color}33` }}>
            <div style={{ fontSize: 11, fontWeight: 800, color: story.policy.color, textTransform: 'uppercase', letterSpacing: 0.5 }}>
              {story.policy.id} 정책의 결정
            </div>
            <p style={{ fontSize: 13.5, color: '#334155', lineHeight: 1.6, margin: '6px 0 0' }}>{cur.decision}</p>
          </div>

          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 11, fontWeight: 800, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5 }}>결과</div>
            <p style={{ fontSize: 13.5, color: '#334155', lineHeight: 1.6, margin: '6px 0 0' }}>{cur.outcome}</p>
          </div>

          {isFinal && (
            <div style={{ marginTop: 16, padding: 14, borderRadius: 10, background: '#F0FDF4', border: '1px solid #BBF7D0', display: 'flex', gap: 10 }}>
              <Flag size={18} color="#16A34A" style={{ flexShrink: 0, marginTop: 1 }} />
              <span style={{ fontSize: 13.5, color: '#166534', fontWeight: 600, lineHeight: 1.6 }}>{story.verdict}</span>
            </div>
          )}
        </Card>

        <Card style={{ padding: 18 }}>
          <SectionHeader title="현재 시점 KPI" />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            {STORY_KPI_META.map((m) => (
              <KpiDelta key={m.key} meta={m} value={cur.kpis[m.key]} prev={prev ? prev.kpis[m.key] : null} />
            ))}
          </div>
        </Card>
      </div>

      {/* Trajectory chart */}
      <Card style={{ padding: 18 }}>
        <SectionHeader title="진행 추이 (수요 충족률 · 평균 HI)" />
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData} margin={{ left: 4, right: 16, top: 8, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748B' }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#94A3B8' }} unit="%" />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line type="monotone" dataKey="수요 충족률" stroke={story.policy.color} strokeWidth={2.5} dot={{ r: 3 }} isAnimationActive={false} />
            <Line type="monotone" dataKey="평균 HI" stroke="#0891B2" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="5 4" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Controls */}
      <Card style={{ padding: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 13, fontWeight: 700, color: '#334155' }}>
            단계 {step + 1} / {steps.length} · {cur.title}
          </span>
          <div style={{ display: 'flex', gap: 8 }}>
            <CtrlButton onClick={() => { setStep(0); setPlaying(false); }} disabled={step === 0} icon={RotateCcw} label="처음" />
            <CtrlButton onClick={() => { setStep((s) => Math.max(0, s - 1)); setPlaying(false); }} disabled={step === 0} icon={ChevronLeft} label="이전" />
            <button
              onClick={() => setPlaying((p) => !p)}
              disabled={isFinal}
              style={{
                display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 8, cursor: isFinal ? 'not-allowed' : 'pointer',
                border: 'none', background: isFinal ? '#E2E8F0' : story.policy.color, color: isFinal ? '#94A3B8' : '#fff',
                fontWeight: 700, fontSize: 13, fontFamily: 'inherit',
              }}
            >
              {playing ? <Pause size={16} /> : <Play size={16} />}
              {playing ? '일시정지' : '자동 재생'}
            </button>
            <CtrlButton onClick={() => { setStep((s) => Math.min(last, s + 1)); setPlaying(false); }} disabled={isFinal} icon={ChevronRight} label="다음" iconRight />
          </div>
        </div>
      </Card>
    </div>
  );
}

function CtrlButton({ onClick, disabled, icon: Icon, label, iconRight }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        display: 'flex', alignItems: 'center', gap: 5, padding: '8px 14px', borderRadius: 8,
        border: '1px solid #E2E8F0', background: '#fff', color: disabled ? '#CBD5E1' : '#334155',
        cursor: disabled ? 'not-allowed' : 'pointer', fontWeight: 700, fontSize: 13, fontFamily: 'inherit',
      }}
    >
      {!iconRight && <Icon size={15} />}
      {label}
      {iconRight && <Icon size={15} />}
    </button>
  );
}
