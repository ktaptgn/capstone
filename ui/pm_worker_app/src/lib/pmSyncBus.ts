// Shared PM work-order sync bus (PM worker app side).
// Real-time, backend-free sync with the operator dashboard.
// Requires both apps to be served from the SAME ORIGIN (same host:port).
//
// Transport:
//   - BroadcastChannel: instant push to other tabs/windows on this origin.
//   - localStorage: persistent source of truth + late-join state + cross-tab fallback.
//
// Must stay contract-compatible with the dashboard copy
// (ui/operator_dashboard/src/lib/pmSyncBus.js): same CHANNEL + STORAGE_KEY + shape.

const CHANNEL = 'c5-pm-orders';
const STORAGE_KEY = 'c5_pm_orders_v1';

// Operator-side decisions: requested → approved / hold / rejected.
// Field-worker lifecycle (after approval): accepted → in_progress → completed,
// plus delayed / rejected.
export type OrderStatus =
  | 'requested'
  | 'approved'
  | 'hold'
  | 'rejected'
  | 'accepted'
  | 'in_progress'
  | 'completed'
  | 'delayed';
export type Party = 'dashboard' | 'pm';

export type RecommendedAction = 'Inspect' | 'Repair' | 'Replace' | 'Cooldown' | 'Hold';

export interface PMWorkOrder {
  id: string;
  truckId: string;
  pmType: string;
  reason: string;
  priority: 'URGENT' | 'HIGH' | 'MEDIUM' | 'LOW';
  requestedAt: string;
  estimatedDuration: string;
  status: OrderStatus;
  origin: Party;
  decidedBy: Party | null;
  decidedAt: string | null;
  report: string | null;
  // Decision context carried from the dashboard recommendation:
  truckHI?: number | null;
  tireHI?: number | null;
  minTireHI?: number | null;
  riskScore?: number | null;
  recommendedAction?: RecommendedAction | null;
  policy?: string | null;
  operatorMessage?: string | null;
  createdAt: number;
  updatedAt: number;
}

type Listener = (orders: PMWorkOrder[]) => void;

const subscribers = new Set<Listener>();

let channel: BroadcastChannel | null = null;
if (typeof BroadcastChannel !== 'undefined') {
  channel = new BroadcastChannel(CHANNEL);
  channel.onmessage = () => emitLocal(readStore());
}

if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === STORAGE_KEY) emitLocal(readStore());
  });
}

function readStore(): PMWorkOrder[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as PMWorkOrder[]) : [];
  } catch {
    return [];
  }
}

function writeStore(orders: PMWorkOrder[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(orders));
}

function emitLocal(orders: PMWorkOrder[]) {
  for (const cb of subscribers) cb(orders);
}

function commit(orders: PMWorkOrder[]) {
  writeStore(orders);
  emitLocal(orders);
  if (channel) channel.postMessage({ type: 'sync', at: Date.now() });
}

export function getOrders(): PMWorkOrder[] {
  return readStore();
}

export function subscribe(callback: Listener): () => void {
  subscribers.add(callback);
  return () => {
    subscribers.delete(callback);
  };
}

export interface NewOrderInput {
  id?: string;
  truckId: string;
  pmType: string;
  reason?: string;
  priority?: PMWorkOrder['priority'];
  requestedAt?: string;
  estimatedDuration?: string;
  status?: OrderStatus;
  origin?: Party;
  decidedBy?: Party | null;
  decidedAt?: string | null;
  truckHI?: number | null;
  tireHI?: number | null;
  minTireHI?: number | null;
  riskScore?: number | null;
  recommendedAction?: RecommendedAction | null;
  policy?: string | null;
  operatorMessage?: string | null;
}

export function publishOrder(order: NewOrderInput): PMWorkOrder {
  const orders = readStore();
  const now = Date.now();
  const entry: PMWorkOrder = {
    id: order.id || `WO-${now}-${Math.random().toString(36).slice(2, 6)}`,
    truckId: order.truckId,
    pmType: order.pmType,
    reason: order.reason || '',
    priority: order.priority || 'HIGH',
    requestedAt: order.requestedAt || new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
    estimatedDuration: order.estimatedDuration || '-',
    status: order.status || 'requested',
    origin: order.origin || 'pm',
    decidedBy: order.decidedBy ?? null,
    decidedAt: order.decidedAt ?? null,
    report: null,
    truckHI: order.truckHI ?? null,
    tireHI: order.tireHI ?? null,
    minTireHI: order.minTireHI ?? null,
    riskScore: order.riskScore ?? null,
    recommendedAction: order.recommendedAction ?? null,
    policy: order.policy ?? null,
    createdAt: now,
    updatedAt: now,
  };
  commit([entry, ...orders.filter((o) => o.id !== entry.id)]);
  return entry;
}

export function decideOrder(orderId: string, decision: OrderStatus, decidedBy: Party): void {
  const orders = readStore();
  const now = Date.now();
  const next = orders.map((o) =>
    o.id === orderId
      ? {
          ...o,
          status: decision,
          decidedBy,
          decidedAt: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
          updatedAt: now,
        }
      : o,
  );
  commit(next);
}

export function seedOrdersIfEmpty(seedOrders: NewOrderInput[]): void {
  if (readStore().length > 0) return;
  const now = Date.now();
  const entries: PMWorkOrder[] = seedOrders.map((o, i) => ({
    id: o.id || `WO-seed-${i}`,
    truckId: o.truckId,
    pmType: o.pmType,
    reason: o.reason || '',
    priority: o.priority || 'HIGH',
    requestedAt: o.requestedAt || new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
    estimatedDuration: o.estimatedDuration || '-',
    status: o.status || 'requested',
    origin: o.origin || 'dashboard',
    decidedBy: o.decidedBy ?? null,
    decidedAt: o.decidedAt ?? null,
    report: null,
    truckHI: o.truckHI ?? null,
    tireHI: o.tireHI ?? null,
    minTireHI: o.minTireHI ?? null,
    riskScore: o.riskScore ?? null,
    recommendedAction: o.recommendedAction ?? null,
    policy: o.policy ?? null,
    operatorMessage: o.operatorMessage ?? null,
    createdAt: now - (seedOrders.length - i),
    updatedAt: now - (seedOrders.length - i),
  }));
  commit(entries);
}

// Field-worker lifecycle transition. Maps a worker action to the next status.
export type WorkerAction = 'accept' | 'start' | 'complete' | 'delay' | 'reject';
const WORKER_ACTION_STATUS: Record<WorkerAction, OrderStatus> = {
  accept: 'accepted',
  start: 'in_progress',
  complete: 'completed',
  delay: 'delayed',
  reject: 'rejected',
};

export function workerAction(orderId: string, action: WorkerAction): void {
  decideOrder(orderId, WORKER_ACTION_STATUS[action], 'pm');
}

export function clearOrders(): void {
  commit([]);
}
