import { useEffect } from 'react';
import { AlertTriangle, CheckCircle, Play, Pause, XCircle, Clock, MessageSquare } from 'lucide-react';
import { usePmOrders } from '../../lib/usePmOrders';
import { seedOrdersIfEmpty, workerAction, type PMWorkOrder, type WorkerAction } from '../../lib/pmSyncBus';

const SEED_ORDERS = [
  {
    id: 'WO-T07',
    truckId: 'T07',
    pmType: '긴급 타이어 교체',
    reason: 'FL 타이어 HI 32% 임계 — 파손 위험. H3가 교체 우선으로 판단.',
    priority: 'URGENT' as const,
    requestedAt: '11:32',
    estimatedDuration: '2h 30m',
    origin: 'dashboard' as const,
    status: 'approved' as const,
    decidedBy: 'dashboard' as const,
    truckHI: 41, tireHI: 61, minTireHI: 32, riskScore: 92,
    recommendedAction: 'Replace' as const, policy: 'H3',
  },
  {
    id: 'WO-T03',
    truckId: 'T03',
    pmType: '서스펜션 점검',
    reason: 'HI 60% 임계 하회 + 운행 중 이상 진동 감지.',
    priority: 'HIGH' as const,
    requestedAt: '11:45',
    estimatedDuration: '1h 20m',
    origin: 'dashboard' as const,
    status: 'approved' as const,
    decidedBy: 'dashboard' as const,
    truckHI: 58, tireHI: 64, minTireHI: 54, riskScore: 71,
    recommendedAction: 'Inspect' as const, policy: 'H3',
  },
];

const STATUS_META: Record<string, { label: string; color: string; bg: string }> = {
  requested:   { label: '신규 지시', color: '#2563EB', bg: '#EFF6FF' },
  approved:    { label: '승인 · 접수 대기', color: '#2563EB', bg: '#EFF6FF' },
  accepted:    { label: '접수됨', color: '#0891B2', bg: '#ECFEFF' },
  in_progress: { label: '작업 중', color: '#7C3AED', bg: '#F5F3FF' },
  completed:   { label: '완료', color: '#16A34A', bg: '#F0FDF4' },
  delayed:     { label: '지연', color: '#D97706', bg: '#FFFBEB' },
  rejected:    { label: '거절', color: '#DC2626', bg: '#FEF2F2' },
};

const ACTION_META: Record<string, { ko: string; color: string }> = {
  Inspect:  { ko: '점검', color: '#2563EB' },
  Repair:   { ko: '수리', color: '#D97706' },
  Replace:  { ko: '교체', color: '#DC2626' },
  Cooldown: { ko: '냉각', color: '#0891B2' },
  Hold:     { ko: '보류', color: '#6B7280' },
};

function nextActions(status: string): { action: WorkerAction; label: string; color: string; icon: typeof Play }[] {
  switch (status) {
    case 'requested':
    case 'approved':
      return [
        { action: 'accept', label: '접수', color: '#16A34A', icon: CheckCircle },
        { action: 'reject', label: '거절', color: '#DC2626', icon: XCircle },
      ];
    case 'accepted':
      return [
        { action: 'start', label: '작업 시작', color: '#7C3AED', icon: Play },
        { action: 'delay', label: '지연', color: '#D97706', icon: Pause },
        { action: 'reject', label: '거절', color: '#DC2626', icon: XCircle },
      ];
    case 'in_progress':
      return [
        { action: 'complete', label: '완료', color: '#16A34A', icon: CheckCircle },
        { action: 'delay', label: '지연', color: '#D97706', icon: Pause },
      ];
    case 'delayed':
      return [
        { action: 'start', label: '작업 재개', color: '#7C3AED', icon: Play },
        { action: 'reject', label: '거절', color: '#DC2626', icon: XCircle },
      ];
    default:
      return [];
  }
}

// Orders that belong in the field inbox: anything except operator-side hold,
// and except orders the operator rejected before dispatch.
function isFieldOrder(o: PMWorkOrder): boolean {
  if (o.status === 'hold') return false;
  if (o.status === 'rejected' && o.decidedBy === 'dashboard') return false;
  return true;
}

function HIChip({ label, value }: { label: string; value: number | null | undefined }) {
  if (value === null || value === undefined) return null;
  const color = value < 40 ? '#DC2626' : value < 60 ? '#F59E0B' : value < 75 ? '#F97316' : '#16A34A';
  return (
    <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded" style={{ background: `${color}15`, color }}>
      {label} {value}%
    </span>
  );
}

export default function ExceptionalPMOrders() {
  const allOrders = usePmOrders();

  useEffect(() => {
    seedOrdersIfEmpty(SEED_ORDERS);
  }, []);

  const orders = allOrders.filter(isFieldOrder);
  const active = orders.filter(o => !['completed', 'rejected'].includes(o.status));
  const done = orders.filter(o => ['completed', 'rejected'].includes(o.status));

  if (orders.length === 0) return null;

  const renderCard = (order: PMWorkOrder) => {
    const sm = STATUS_META[order.status] || STATUS_META.requested;
    const am = order.recommendedAction ? ACTION_META[order.recommendedAction] : null;
    const actions = nextActions(order.status);
    return (
      <div
        key={order.id}
        className="bg-white rounded-xl p-3 shadow-sm border"
        style={{ borderColor: `${sm.color}30`, borderLeft: `4px solid ${sm.color}` }}
      >
        <div className="flex items-start justify-between mb-1.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-bold text-text-main">{order.truckId}</span>
            <span
              className="text-[9px] font-bold px-1.5 py-0.5 rounded-full"
              style={{
                background: order.priority === 'URGENT' ? '#FEE2E2' : order.priority === 'HIGH' ? '#FEF3C7' : '#F1F5F9',
                color: order.priority === 'URGENT' ? '#DC2626' : order.priority === 'HIGH' ? '#D97706' : '#64748B',
              }}
            >
              {order.priority}
            </span>
            {am && (
              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: `${am.color}15`, color: am.color }}>
                {order.recommendedAction} · {am.ko}
              </span>
            )}
            {order.origin === 'dashboard' && (
              <span className="text-[8px] font-semibold px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-600">관제 지시</span>
            )}
          </div>
          <span className="text-[9px] font-bold px-2 py-0.5 rounded-full" style={{ background: sm.bg, color: sm.color }}>
            {sm.label}
          </span>
        </div>

        <div className="text-[11px] font-medium text-text-main">{order.pmType}</div>
        <div className="text-[10px] text-text-sub mt-0.5">{order.reason}</div>

        {/* HI values + meta */}
        <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
          <HIChip label="Truck" value={order.truckHI} />
          <HIChip label="Tire" value={order.tireHI} />
          <HIChip label="min" value={order.minTireHI} />
          {order.riskScore != null && (
            <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">Risk {order.riskScore}</span>
          )}
          <span className="text-[9px] text-text-sub flex items-center gap-0.5">
            <Clock size={9} /> {order.requestedAt} · 예상 {order.estimatedDuration}
          </span>
          {order.policy && <span className="text-[9px] text-text-sub">· {order.policy}</span>}
        </div>

        {/* Operator message */}
        {order.operatorMessage && (
          <div className="flex items-start gap-1 mt-1.5 text-[10px] text-sanguine bg-sanguine-soft/40 rounded px-2 py-1">
            <MessageSquare size={11} className="mt-0.5 shrink-0" />
            <span>관제: {order.operatorMessage}</span>
          </div>
        )}

        {/* Worker lifecycle actions */}
        {actions.length > 0 && (
          <div className="flex gap-2 mt-2">
            {actions.map(a => {
              const Icon = a.icon;
              return (
                <button
                  key={a.action}
                  onClick={() => workerAction(order.id, a.action)}
                  className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-[11px] font-bold text-white transition-colors"
                  style={{ background: a.color }}
                >
                  <Icon size={12} />
                  {a.label}
                </button>
              );
            })}
          </div>
        )}
        {order.status !== 'requested' && order.decidedBy === 'pm' && order.decidedAt && (
          <div className="text-[9px] text-text-sub mt-1.5 text-right">현장 처리 {order.decidedAt}</div>
        )}
      </div>
    );
  };

  return (
    <div className="px-4 space-y-2.5">
      <h3 className="text-sm font-semibold text-text-main flex items-center gap-1.5">
        <AlertTriangle size={14} className="text-red-500" />
        PM 작업 지시함
        {active.length > 0 && (
          <span className="ml-1 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">{active.length}</span>
        )}
      </h3>

      {active.map(renderCard)}

      {done.length > 0 && (
        <>
          <div className="text-[10px] font-semibold text-text-sub pt-1">처리 완료</div>
          {done.map(renderCard)}
        </>
      )}
    </div>
  );
}
