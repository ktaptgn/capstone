import { useEffect } from 'react';
import { AlertTriangle, CheckCircle, Pause, XCircle } from 'lucide-react';
import { usePmOrders } from '../../lib/usePmOrders';
import { decideOrder, seedOrdersIfEmpty, type OrderStatus } from '../../lib/pmSyncBus';

const SEED_ORDERS = [
  {
    id: 'EX-001',
    truckId: 'T07',
    pmType: '긴급 타이어 교체',
    reason: 'FL 타이어 HI 32% — 즉시 교체 필요',
    priority: 'URGENT' as const,
    requestedAt: '11:32',
    estimatedDuration: '2h 30m',
    origin: 'dashboard' as const,
  },
  {
    id: 'EX-002',
    truckId: 'T03',
    pmType: '서스펜션 추가 점검',
    reason: '운행 중 이상 진동 감지, HI 58%',
    priority: 'HIGH' as const,
    requestedAt: '11:45',
    estimatedDuration: '1h 20m',
    origin: 'dashboard' as const,
  },
];

export default function ExceptionalPMOrders() {
  const orders = usePmOrders();

  // Seed demo orders once if the shared store is empty.
  useEffect(() => {
    seedOrdersIfEmpty(SEED_ORDERS);
  }, []);

  const handleDecision = (orderId: string, decision: OrderStatus) => {
    decideOrder(orderId, decision, 'pm');
  };

  const pendingOrders = orders.filter((o) => o.status === 'requested');
  const decidedOrders = orders.filter((o) => o.status !== 'requested');

  if (orders.length === 0) return null;

  return (
    <div className="px-4 space-y-2.5">
      <h3 className="text-sm font-semibold text-text-main flex items-center gap-1.5">
        <AlertTriangle size={14} className="text-red-500" />
        긴급 PM 요청
        {pendingOrders.length > 0 && (
          <span className="ml-1 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
            {pendingOrders.length}
          </span>
        )}
      </h3>

      {/* Pending orders */}
      {pendingOrders.map((order) => (
        <div
          key={order.id}
          className="bg-white rounded-xl p-3 shadow-sm border-l-4 border border-red-400"
          style={{ borderLeftColor: order.priority === 'URGENT' ? '#DC2626' : '#F59E0B' }}
        >
          <div className="flex items-start justify-between mb-2">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-text-main">{order.truckId}</span>
                <span
                  className="text-[9px] font-bold px-1.5 py-0.5 rounded-full"
                  style={{
                    background: order.priority === 'URGENT' ? '#FEE2E2' : '#FEF3C7',
                    color: order.priority === 'URGENT' ? '#DC2626' : '#D97706',
                  }}
                >
                  {order.priority}
                </span>
                {order.origin === 'dashboard' && (
                  <span className="text-[8px] font-semibold px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-600">
                    관제 요청
                  </span>
                )}
              </div>
              <div className="text-[11px] font-medium text-text-main mt-0.5">{order.pmType}</div>
              <div className="text-[10px] text-text-sub mt-0.5">{order.reason}</div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-text-sub">{order.requestedAt}</div>
              <div className="text-[10px] text-text-sub">예상 {order.estimatedDuration}</div>
            </div>
          </div>

          {/* 3-button decision row */}
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => handleDecision(order.id, 'approved')}
              className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg text-[11px] font-bold text-white transition-colors"
              style={{ background: '#16A34A' }}
            >
              <CheckCircle size={13} />
              승인
            </button>
            <button
              onClick={() => handleDecision(order.id, 'hold')}
              className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg text-[11px] font-bold text-white transition-colors"
              style={{ background: '#D97706' }}
            >
              <Pause size={13} />
              보류
            </button>
            <button
              onClick={() => handleDecision(order.id, 'rejected')}
              className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg text-[11px] font-bold text-white transition-colors"
              style={{ background: '#DC2626' }}
            >
              <XCircle size={13} />
              거절
            </button>
          </div>
        </div>
      ))}

      {/* Decided orders */}
      {decidedOrders.map((order) => {
        const d = order.status;
        const decisionLabel = d === 'approved' ? '승인됨' : d === 'hold' ? '보류됨' : '거절됨';
        const decisionColor =
          d === 'approved' ? '#16A34A' : d === 'hold' ? '#D97706' : '#DC2626';
        const decisionBg =
          d === 'approved' ? '#F0FDF4' : d === 'hold' ? '#FFFBEB' : '#FEF2F2';

        return (
          <div
            key={order.id}
            className="rounded-xl p-3 border"
            style={{ background: decisionBg, borderColor: `${decisionColor}30` }}
          >
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-text-main">{order.truckId}</span>
                <span className="text-[11px] text-text-sub ml-2">{order.pmType}</span>
                {order.decidedBy === 'dashboard' && (
                  <span className="text-[8px] font-semibold px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-600 ml-2">
                    관제 결정
                  </span>
                )}
              </div>
              <span
                className="text-[10px] font-bold px-2 py-0.5 rounded-full"
                style={{ background: decisionColor, color: '#fff' }}
              >
                {decisionLabel}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
