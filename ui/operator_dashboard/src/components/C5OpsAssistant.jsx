import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Bot, User } from 'lucide-react';
import { dashboardKpis } from '../data/dashboardKpis';
import { policies } from '../data/policies';
import { priorityActions } from '../data/priorityActions';

const KPI_KEYWORDS = ['kpi', '요약', '운영 현황', '수요 충족률', '가용 트럭', 'pm 비용', '총 비용', '현재 상태', '운영 상태', '현황', 'summary', 'status'];
const POLICY_KEYWORDS = ['정책', 'policy', 'h1', 'h2', 'h3', 'h4', '비교', '추천', '왜', '장단점', 'comparison', 'recommend'];
const ACTION_KEYWORDS = ['우선 조치', 'action', '먼저', '해야 할 일', 'priority', '운영자', '조치', '리스크', 'risk', '뭐부터', '무엇부터'];

function matchIntent(input) {
  const lower = input.toLowerCase().trim();
  for (const kw of ACTION_KEYWORDS) { if (lower.includes(kw)) return 'actions'; }
  for (const kw of POLICY_KEYWORDS) { if (lower.includes(kw)) return 'policy'; }
  for (const kw of KPI_KEYWORDS) { if (lower.includes(kw)) return 'kpi'; }
  return 'unknown';
}

function buildKpiResponse() {
  const d = dashboardKpis;
  return {
    title: '현재 KPI 요약',
    rows: [
      { label: '수요 충족률', value: `${d.demandFulfillment}%`, color: '#8A4931' },
      { label: '완료 운반량', value: `${d.completedLoads} / ${d.dailyDemand}` },
      { label: '가용 트럭', value: `${d.availableTrucks} / ${d.totalTrucks}`, color: '#16A34A' },
      { label: 'PM 중 트럭', value: `${d.trucksInPM}대`, color: '#7C3AED' },
      { label: 'PM 비용', value: `M₩${d.pmCostMKRW}` },
      { label: '총 운영비용', value: `M₩${d.totalCostMKRW}` },
      { label: '주의 필요 트럭', value: `${d.riskTrucks}대`, color: '#DC2626' },
      { label: 'Critical Tire', value: `${d.criticalTireCount}개`, color: '#DC2626' },
    ],
    footer: '현재 C5 시뮬레이션 mock data 기준입니다.',
  };
}

function buildPolicyResponse() {
  const active = policies.find(p => p.active);
  const h1h4 = policies.filter(p => !p.planned);
  return {
    title: '정책 비교 요약',
    recommendation: {
      id: active.id,
      name: active.name,
      reasons: [
        `Total Cost: M₩${active.totalCost}`,
        `Demand Fulfillment: ${active.demandFulfill}%`,
        `Failure Count: ${active.failures}`,
        'PM 비용과 생산 성능의 균형이 가장 좋음',
      ],
    },
    summaries: h1h4.map(p => ({
      id: p.id,
      text: p.useCase,
      active: p.active,
    })),
    footer: '현재 입력 조건 기준으로 H3가 가장 균형적입니다. 운영자는 PM Bay 상태와 수요 조건을 함께 확인해야 합니다.',
  };
}

function buildActionsResponse() {
  return {
    title: '운영자 우선 조치',
    actions: priorityActions.map(a => ({
      rank: a.rank,
      action: a.actionKr,
      details: [a.reasonKr, a.riskKr],
    })),
    footer: '현재 C5 시뮬레이션 mock data 기준입니다.',
  };
}

function KpiMessage({ data }) {
  return (
    <div>
      <div style={{ fontWeight: 700, fontSize: 13, color: '#7C2D12', marginBottom: 8 }}>[{data.title}]</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {data.rows.map((r, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, padding: '3px 0', borderBottom: '1px solid #F1F5F9' }}>
            <span style={{ color: '#64748B' }}>{r.label}</span>
            <span style={{ fontWeight: 600, color: r.color || '#1E293B' }}>{r.value}</span>
          </div>
        ))}
      </div>
      <div style={{ fontSize: 10, color: '#94A3B8', marginTop: 8, fontStyle: 'italic' }}>{data.footer}</div>
    </div>
  );
}

function PolicyMessage({ data }) {
  return (
    <div>
      <div style={{ fontWeight: 700, fontSize: 13, color: '#7C2D12', marginBottom: 8 }}>[{data.title}]</div>
      <div style={{ background: '#F3E7E2', borderRadius: 8, padding: 10, marginBottom: 8 }}>
        <div style={{ fontSize: 11, color: '#94A3B8', fontWeight: 600 }}>현재 추천 정책</div>
        <div style={{ fontSize: 14, fontWeight: 700, color: '#7C2D12', marginTop: 2 }}>{data.recommendation.id} {data.recommendation.name}</div>
        <div style={{ marginTop: 6 }}>
          {data.recommendation.reasons.map((r, i) => (
            <div key={i} style={{ fontSize: 11, color: '#334155', paddingLeft: 8, position: 'relative' }}>
              <span style={{ position: 'absolute', left: 0 }}>-</span> {r}
            </div>
          ))}
        </div>
      </div>
      <div style={{ fontSize: 12, fontWeight: 600, color: '#1E293B', marginBottom: 4 }}>정책별 요약:</div>
      {data.summaries.map(s => (
        <div key={s.id} style={{ fontSize: 11, color: '#334155', padding: '2px 0' }}>
          <span style={{ fontWeight: 600, color: s.active ? '#8A4931' : '#334155' }}>{s.id}</span>: {s.text}
        </div>
      ))}
      <div style={{ fontSize: 10, color: '#94A3B8', marginTop: 8, fontStyle: 'italic' }}>{data.footer}</div>
    </div>
  );
}

function ActionsMessage({ data }) {
  const rankColors = ['#DC2626', '#F59E0B', '#6B7280'];
  const rankBgs = ['#FEF2F2', '#FFFBEB', '#F9FAFB'];
  return (
    <div>
      <div style={{ fontWeight: 700, fontSize: 13, color: '#7C2D12', marginBottom: 8 }}>[{data.title}]</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {data.actions.map((a, i) => (
          <div key={a.rank} style={{ background: rankBgs[i], borderRadius: 8, padding: 10, borderLeft: `3px solid ${rankColors[i]}` }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: '#1E293B' }}>
              {a.rank}. {a.action}
            </div>
            {a.details.map((d, j) => (
              <div key={j} style={{ fontSize: 11, color: '#64748B', paddingLeft: 14, marginTop: 2 }}>- {d}</div>
            ))}
          </div>
        ))}
      </div>
      <div style={{ fontSize: 10, color: '#94A3B8', marginTop: 8, fontStyle: 'italic' }}>{data.footer}</div>
    </div>
  );
}

function UnknownMessage() {
  return (
    <div>
      <div style={{ fontSize: 12, color: '#334155', marginBottom: 4 }}>
        이 Assistant는 현재 <strong>KPI 요약</strong>, <strong>정책 비교 요약</strong>, <strong>운영자 우선 조치 3개</strong>만 답변합니다.
      </div>
      <div style={{ fontSize: 11, color: '#94A3B8', fontStyle: 'italic' }}>
        This assistant only supports KPI summary, policy comparison, and priority actions.
      </div>
    </div>
  );
}

function AssistantMessage({ intent }) {
  switch (intent) {
    case 'kpi': return <KpiMessage data={buildKpiResponse()} />;
    case 'policy': return <PolicyMessage data={buildPolicyResponse()} />;
    case 'actions': return <ActionsMessage data={buildActionsResponse()} />;
    default: return <UnknownMessage />;
  }
}

const CHIPS = [
  { label: '현재 KPI 요약', intent: 'kpi' },
  { label: '정책 비교 요약', intent: 'policy' },
  { label: '우선 조치 3개', intent: 'actions' },
];

export default function C5OpsAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  function handleSend(text, intent) {
    const userText = text || input.trim();
    if (!userText) return;
    const resolvedIntent = intent || matchIntent(userText);
    setMessages(prev => [
      ...prev,
      { role: 'user', text: userText },
      { role: 'assistant', intent: resolvedIntent },
    ]);
    setInput('');
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button onClick={() => setIsOpen(true)} style={{
          position: 'fixed', bottom: 24, right: 24, zIndex: 1000,
          width: 56, height: 56, borderRadius: '50%', border: 'none', cursor: 'pointer',
          background: '#8A4931', color: '#fff',
          boxShadow: '0 4px 16px rgba(138, 73, 49, 0.35)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'transform 0.2s, box-shadow 0.2s',
        }}
        onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.08)'; e.currentTarget.style.boxShadow = '0 6px 20px rgba(138, 73, 49, 0.45)'; }}
        onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = '0 4px 16px rgba(138, 73, 49, 0.35)'; }}
        >
          <MessageCircle size={24} />
        </button>
      )}

      {/* Panel */}
      {isOpen && (
        <div style={{
          position: 'fixed', bottom: 0, right: 0, zIndex: 1000,
          width: 400, maxWidth: '34vw', height: '100vh',
          background: '#fff', borderLeft: '1px solid #E2E8F0',
          boxShadow: '-4px 0 24px rgba(0,0,0,0.08)',
          display: 'flex', flexDirection: 'column',
          animation: 'slideIn 0.25s ease-out',
        }}>
          {/* Header */}
          <div style={{
            padding: '16px 20px', borderBottom: '1px solid #E2E8F0',
            background: '#8A4931', color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            flexShrink: 0,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%', background: 'rgba(255,255,255,0.2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Bot size={20} color="#fff" />
              </div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700 }}>C5 Ops Assistant</div>
                <div style={{ fontSize: 10, opacity: 0.8 }}>KPI · Policy · Actions only</div>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} style={{
              background: 'rgba(255,255,255,0.15)', border: 'none', borderRadius: 6,
              width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', color: '#fff',
            }}>
              <X size={18} />
            </button>
          </div>

          {/* Messages Area */}
          <div style={{
            flex: 1, overflow: 'auto', padding: 16,
            display: 'flex', flexDirection: 'column', gap: 12,
            background: '#F8FAFC',
          }}>
            {/* Welcome */}
            {messages.length === 0 && (
              <div style={{ textAlign: 'center', padding: '40px 16px' }}>
                <div style={{
                  width: 56, height: 56, borderRadius: '50%', background: '#F3E7E2',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 12px',
                }}>
                  <Bot size={28} color="#8A4931" />
                </div>
                <div style={{ fontSize: 15, fontWeight: 700, color: '#1E293B', marginBottom: 4 }}>
                  C5 Ops Assistant
                </div>
                <div style={{ fontSize: 12, color: '#64748B', marginBottom: 4 }}>
                  Ask about KPI summary, policy comparison, or priority actions.
                </div>
                <div style={{ fontSize: 11, color: '#94A3B8' }}>
                  KPI 요약, 정책 비교, 우선 조치만 답변합니다.
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                gap: 8,
              }}>
                {msg.role === 'assistant' && (
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%', background: '#F3E7E2',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                    marginTop: 2,
                  }}>
                    <Bot size={14} color="#8A4931" />
                  </div>
                )}
                <div style={{
                  maxWidth: '85%', padding: '10px 14px', borderRadius: 12,
                  background: msg.role === 'user' ? '#8A4931' : '#fff',
                  color: msg.role === 'user' ? '#fff' : '#334155',
                  fontSize: 12, lineHeight: 1.5,
                  border: msg.role === 'assistant' ? '1px solid #E2E8F0' : 'none',
                  boxShadow: msg.role === 'assistant' ? '0 1px 3px rgba(0,0,0,0.04)' : 'none',
                }}>
                  {msg.role === 'user' ? msg.text : <AssistantMessage intent={msg.intent} />}
                </div>
                {msg.role === 'user' && (
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%', background: '#E2E8F0',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                    marginTop: 2,
                  }}>
                    <User size={14} color="#64748B" />
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Chips */}
          <div style={{
            padding: '8px 16px', borderTop: '1px solid #F1F5F9',
            display: 'flex', gap: 6, flexWrap: 'wrap', background: '#fff',
          }}>
            {CHIPS.map(chip => (
              <button key={chip.intent} onClick={() => handleSend(chip.label, chip.intent)} style={{
                padding: '6px 12px', borderRadius: 16,
                border: '1px solid #E7D0C6', background: '#FDF8F6',
                fontSize: 11, fontWeight: 600, color: '#8A4931',
                cursor: 'pointer', whiteSpace: 'nowrap',
                fontFamily: 'inherit',
                transition: 'background 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.background = '#F3E7E2'}
              onMouseLeave={e => e.currentTarget.style.background = '#FDF8F6'}
              >
                {chip.label}
              </button>
            ))}
          </div>

          {/* Input */}
          <div style={{
            padding: '12px 16px', borderTop: '1px solid #E2E8F0', background: '#fff',
            display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0,
          }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="질문을 입력하세요..."
              style={{
                flex: 1, padding: '10px 14px', borderRadius: 8,
                border: '1px solid #E2E8F0', fontSize: 12,
                outline: 'none', fontFamily: 'inherit',
                background: '#F8FAFC',
              }}
              onFocus={e => e.currentTarget.style.borderColor = '#8A4931'}
              onBlur={e => e.currentTarget.style.borderColor = '#E2E8F0'}
            />
            <button onClick={() => handleSend()} style={{
              width: 38, height: 38, borderRadius: 8, border: 'none',
              background: input.trim() ? '#8A4931' : '#E2E8F0',
              color: input.trim() ? '#fff' : '#94A3B8',
              cursor: input.trim() ? 'pointer' : 'default',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'background 0.15s',
            }}>
              <Send size={16} />
            </button>
          </div>
        </div>
      )}

      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </>
  );
}
