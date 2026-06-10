import { useState } from 'react';
import { CheckCircle, PauseCircle, XCircle, MessageSquare, Send, Gauge, BookOpen } from 'lucide-react';
import Card from './Card';
import SectionHeader from './SectionHeader';
import { usePmOrders } from '../lib/usePmOrders';
import { publishOrder } from '../lib/pmSyncBus';
import { recommendedPolicy, pmRecommendations, actionMeta, riskColor, hiColor } from '../data/pmRecommendations';

const LIFECYCLE_LABEL = {
  requested: '현장 전송됨 · 작업자 확인 대기',
  approved: '승인 · 현장 전송됨',
  accepted: '작업자 접수됨',
  in_progress: '작업 진행 중',
  completed: '작업 완료',
  delayed: '작업 지연됨',
  rejected: '작업자 거절',
  hold: '보류됨',
};
const LIFECYCLE_COLOR = {
  requested: '#2563EB', approved: '#16A34A', accepted: '#0891B2',
  in_progress: '#7C3AED', completed: '#16A34A', delayed: '#D97706',
  rejected: '#DC2626', hold: '#6B7280',
};

function MiniStat({ label, value, color }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      <span style={{ fontSize: 9, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>{label}</span>
      <span style={{ fontSize: 14, fontWeight: 800, color: color || 'var(--text-main)' }}>{value}</span>
    </div>
  );
}

export default function DecisionRecommendationPanel({ onDecision, onShowHeuristics }) {
  const orders = usePmOrders();
  const orderByTruck = new Map(orders.map(o => [o.truckId, o]));
  const [composerFor, setComposerFor] = useState(null);
  const [messageText, setMessageText] = useState('');

  const upsertOrder = (rec, status, extra = {}) => {
    const existing = orderByTruck.get(rec.truckId);
    publishOrder({
      id: `WO-${rec.truckId}`,
      truckId: rec.truckId,
      pmType: rec.pmType,
      reason: rec.reason,
      priority: rec.priority,
      estimatedDuration: rec.expectedDuration,
      status,
      origin: 'dashboard',
      decidedBy: 'dashboard',
      decidedAt: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
      truckHI: rec.truckHI,
      tireHI: rec.tireHI,
      minTireHI: rec.minTireHI,
      riskScore: rec.riskScore,
      recommendedAction: rec.recommendedAction,
      policy: rec.heuristic,
      operatorMessage: extra.operatorMessage ?? existing?.operatorMessage ?? null,
    });
  };

  const handleApprove = (rec) => {
    upsertOrder(rec, 'approved');
    if (onDecision) onDecision(rec.truckId, `${rec.truckId} ${rec.pmType} (${rec.recommendedAction})`, 'approved');
  };
  const handleHold = (rec) => {
    upsertOrder(rec, 'hold');
    if (onDecision) onDecision(rec.truckId, `${rec.truckId} ${rec.pmType} (${rec.recommendedAction})`, 'hold');
  };
  const handleReject = (rec) => {
    upsertOrder(rec, 'rejected');
    if (onDecision) onDecision(rec.truckId, `${rec.truckId} ${rec.pmType} (${rec.recommendedAction})`, 'rejected');
  };
  const handleSendMessage = (rec) => {
    const msg = messageText.trim();
    if (!msg) return;
    const existing = orderByTruck.get(rec.truckId);
    // Keep current status if order exists, else send as a new incoming request.
    upsertOrder(rec, existing?.status || 'requested', { operatorMessage: msg });
    setComposerFor(null);
    setMessageText('');
  };

  const btn = (bg, border) => ({
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4,
    padding: '6px 10px', borderRadius: 7, border: border || 'none',
    fontSize: 11, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit',
    color: border ? 'var(--text-sub)' : '#fff', background: bg,
  });

  return (
    <Card style={{ padding: 20 }}>
      {/* Header: recommended policy */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
        <div>
          <SectionHeader title="Decision Recommendation" />
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
            현재 정책 휴리스틱이 권고하는 PM 의사결정 — 승인 시 PM 작업자 앱으로 작업 지시가 전송됩니다.
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700 }}>추천 정책</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
              {recommendedPolicy.candidates.map(p => {
                const isBest = p === recommendedPolicy.best;
                return (
                  <span key={p} style={{
                    fontSize: isBest ? 13 : 11, fontWeight: 800,
                    padding: isBest ? '3px 9px' : '2px 6px', borderRadius: 6,
                    background: isBest ? '#16A34A' : 'var(--divider)',
                    color: isBest ? '#fff' : 'var(--text-muted)',
                    border: isBest ? 'none' : '1px solid var(--border)',
                  }}>{p}</span>
                );
              })}
            </div>
          </div>
          <button onClick={onShowHeuristics} style={{
            display: 'flex', alignItems: 'center', gap: 6, padding: '8px 12px', borderRadius: 8,
            border: '1px solid #8A4931', background: 'var(--primary-soft)', color: '#8A4931',
            fontSize: 12, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit',
          }}>
            <BookOpen size={14} /> H0–H4 설명
          </button>
        </div>
      </div>

      <div style={{
        fontSize: 11, color: '#166534', background: '#F0FDF4', border: '1px solid #BBF7D0',
        borderRadius: 8, padding: '8px 12px', marginBottom: 16,
      }}>
        <strong>{recommendedPolicy.label}</strong> · {recommendedPolicy.basis}
        <span style={{ color: '#92400E', marginLeft: 8 }}>※ {recommendedPolicy.note}</span>
      </div>

      {/* Recommendation rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {pmRecommendations.map(rec => {
          const am = actionMeta[rec.recommendedAction];
          const order = orderByTruck.get(rec.truckId);
          const decided = order && order.decidedBy === 'dashboard'
            ? order.status : null;
          return (
            <div key={rec.id} style={{
              border: '1px solid var(--border)', borderRadius: 10, padding: 12,
              borderLeft: `4px solid ${riskColor(rec.riskScore)}`,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                {/* Left: truck + action + stats */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 16, fontWeight: 800, color: 'var(--text-main)' }}>{rec.truckId}</span>
                    <span style={{
                      fontSize: 9, fontWeight: 800, padding: '2px 6px', borderRadius: 4,
                      background: rec.priority === 'URGENT' ? '#FEE2E2' : rec.priority === 'HIGH' ? '#FEF3C7' : 'var(--divider)',
                      color: rec.priority === 'URGENT' ? '#DC2626' : rec.priority === 'HIGH' ? '#D97706' : 'var(--text-muted)',
                    }}>{rec.priority}</span>
                    <span style={{
                      fontSize: 11, fontWeight: 800, padding: '3px 8px', borderRadius: 6,
                      background: am.bg, color: am.color, border: `1px solid ${am.color}30`,
                    }}>{rec.recommendedAction} · {am.ko}</span>
                  </div>
                  <MiniStat label="Truck HI" value={`${rec.truckHI}%`} color={hiColor(rec.truckHI)} />
                  <MiniStat label="Tire HI" value={`${rec.tireHI}%`} color={hiColor(rec.tireHI)} />
                  <MiniStat label="min Tire" value={`${rec.minTireHI}%`} color={hiColor(rec.minTireHI)} />
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <span style={{ fontSize: 9, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Risk</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 3, fontSize: 14, fontWeight: 800, color: riskColor(rec.riskScore) }}>
                      <Gauge size={12} /> {rec.riskScore}
                    </span>
                  </div>
                  <MiniStat label="예상 PM" value={rec.expectedDuration} />
                </div>

                {/* Right: action buttons */}
                <div style={{ display: 'flex', gap: 6 }}>
                  <button style={btn('#16A34A')} onClick={() => handleApprove(rec)}><CheckCircle size={13} /> Approve PM</button>
                  <button style={btn('#D97706')} onClick={() => handleHold(rec)}><PauseCircle size={13} /> Hold</button>
                  <button style={btn('#DC2626')} onClick={() => handleReject(rec)}><XCircle size={13} /> Reject</button>
                  <button style={btn('var(--bg-card)', '1px solid var(--border)')} onClick={() => { setComposerFor(composerFor === rec.id ? null : rec.id); setMessageText(''); }}>
                    <MessageSquare size={13} /> Send Message
                  </button>
                </div>
              </div>

              {/* Reason */}
              <div style={{ fontSize: 11, color: 'var(--text-sub)', marginTop: 8, lineHeight: 1.5 }}>
                <strong style={{ color: 'var(--text-body)' }}>근거({rec.heuristic}):</strong> {rec.reason}
              </div>

              {/* Decision result + live field status */}
              {decided && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
                  <span style={{
                    fontSize: 10, fontWeight: 800, padding: '3px 8px', borderRadius: 6,
                    background: `${LIFECYCLE_COLOR[decided]}18`, color: LIFECYCLE_COLOR[decided],
                  }}>
                    관제 결정: {decided === 'approved' ? '승인' : decided === 'hold' ? '보류' : decided === 'rejected' ? '거절' : decided}
                  </span>
                  {order && order.status !== 'hold' && order.status !== 'rejected' && (
                    <span style={{ fontSize: 10, color: LIFECYCLE_COLOR[order.status], fontWeight: 700 }}>
                      → 현장: {LIFECYCLE_LABEL[order.status]}
                      {order.decidedBy === 'pm' && order.decidedAt ? ` (${order.decidedAt})` : ''}
                    </span>
                  )}
                </div>
              )}
              {order?.operatorMessage && (
                <div style={{ fontSize: 10, color: '#8A4931', marginTop: 4 }}>
                  ✉ 작업자에게 전송: “{order.operatorMessage}”
                </div>
              )}

              {/* Message composer */}
              {composerFor === rec.id && (
                <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
                  <input
                    value={messageText}
                    onChange={e => setMessageText(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') handleSendMessage(rec); }}
                    placeholder={`${rec.truckId} 작업자에게 보낼 메시지...`}
                    autoFocus
                    style={{
                      flex: 1, padding: '7px 10px', borderRadius: 7, border: '1px solid var(--border)',
                      fontSize: 12, fontFamily: 'inherit', color: 'var(--text-body)', background: 'var(--bg-page)',
                    }}
                  />
                  <button style={btn('#8A4931')} onClick={() => handleSendMessage(rec)}><Send size={13} /> 전송</button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
