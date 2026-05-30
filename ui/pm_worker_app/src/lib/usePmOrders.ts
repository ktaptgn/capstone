import { useEffect, useState } from 'react';
import { getOrders, subscribe, type PMWorkOrder } from './pmSyncBus';

// Live view of the shared PM work-order list. Re-renders whenever any
// tab/window (dashboard or PM app) on this origin mutates an order.
export function usePmOrders(): PMWorkOrder[] {
  const [orders, setOrders] = useState<PMWorkOrder[]>(() => getOrders());
  useEffect(() => subscribe(setOrders), []);
  return orders;
}
