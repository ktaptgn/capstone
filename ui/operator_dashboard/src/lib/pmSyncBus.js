// Shared PM work-order sync bus.
// Real-time, backend-free sync between the operator dashboard and the PM worker app.
// Requires both apps to be served from the SAME ORIGIN (same host:port).
//
// Transport:
//   - BroadcastChannel: instant push to other tabs/windows on this origin.
//   - localStorage: persistent source of truth + late-join state + cross-tab fallback.
//
// The dashboard (JS) and PM app (TS) each bundle their own copy of this module,
// but they share the same channel name + storage key, so they interoperate.

const CHANNEL = 'c5-pm-orders';
const STORAGE_KEY = 'c5_pm_orders_v1';

// Operator decisions: 'requested' | 'approved' | 'hold' | 'rejected'
// Field-worker lifecycle: 'accepted' | 'in_progress' | 'completed' | 'delayed' | 'rejected'
// origin / decidedBy: 'dashboard' | 'pm'
// recommendedAction: 'Inspect' | 'Repair' | 'Replace' | 'Cooldown' | 'Hold'

const subscribers = new Set();

let channel = null;
if (typeof BroadcastChannel !== 'undefined') {
  channel = new BroadcastChannel(CHANNEL);
  channel.onmessage = () => emitLocal(readStore());
}

if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === STORAGE_KEY) emitLocal(readStore());
  });
}

function readStore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeStore(orders) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(orders));
}

function emitLocal(orders) {
  for (const cb of subscribers) cb(orders);
}

// Persist + notify local subscribers + push to other tabs.
function commit(orders) {
  writeStore(orders);
  emitLocal(orders);
  if (channel) channel.postMessage({ type: 'sync', at: Date.now() });
}

export function getOrders() {
  return readStore();
}

export function subscribe(callback) {
  subscribers.add(callback);
  return () => subscribers.delete(callback);
}

// Create a new PM work order (status defaults to 'requested').
export function publishOrder(order) {
  const orders = readStore();
  const now = Date.now();
  const entry = {
    id: order.id || `WO-${now}-${Math.random().toString(36).slice(2, 6)}`,
    truckId: order.truckId,
    pmType: order.pmType,
    reason: order.reason || '',
    priority: order.priority || 'HIGH',
    requestedAt: order.requestedAt || new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
    estimatedDuration: order.estimatedDuration || '-',
    status: order.status || 'requested',
    origin: order.origin || 'dashboard',
    decidedBy: order.decidedBy || null,
    decidedAt: order.decidedAt || null,
    report: order.report || null,
    truckHI: order.truckHI ?? null,
    tireHI: order.tireHI ?? null,
    minTireHI: order.minTireHI ?? null,
    riskScore: order.riskScore ?? null,
    recommendedAction: order.recommendedAction ?? null,
    policy: order.policy ?? null,
    operatorMessage: order.operatorMessage ?? null,
    createdAt: now,
    updatedAt: now,
  };
  commit([entry, ...orders.filter((o) => o.id !== entry.id)]);
  return entry;
}

// Apply a decision (approved / hold / rejected) to an existing order.
export function decideOrder(orderId, decision, decidedBy) {
  const orders = readStore();
  const now = Date.now();
  const next = orders.map((o) =>
    o.id === orderId
      ? {
          ...o,
          status: decision,
          decidedBy: decidedBy || o.decidedBy || 'dashboard',
          decidedAt: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
          updatedAt: now,
        }
      : o,
  );
  commit(next);
}

// Seed initial demo orders only if the store is currently empty (idempotent).
export function seedOrdersIfEmpty(seedOrders) {
  if (readStore().length > 0) return;
  const now = Date.now();
  const entries = seedOrders.map((o, i) => ({
    reason: '',
    priority: 'HIGH',
    estimatedDuration: '-',
    status: 'requested',
    origin: 'dashboard',
    decidedBy: null,
    decidedAt: null,
    report: null,
    ...o,
    requestedAt: o.requestedAt || new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
    createdAt: now - (seedOrders.length - i),
    updatedAt: now - (seedOrders.length - i),
  }));
  commit(entries);
}

export function clearOrders() {
  commit([]);
}
