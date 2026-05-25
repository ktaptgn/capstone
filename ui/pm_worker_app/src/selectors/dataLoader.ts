import trucksData from '../data/trucks.json';
import componentHealthData from '../data/component_health.json';
import pmScheduleData from '../data/pm_schedule.json';
import workRecordsData from '../data/work_records.json';
import alertsData from '../data/alerts.json';
import chatbotResponsesData from '../data/chatbot_responses.json';
import type { Truck, ComponentHealth, PMSchedule, WorkRecords, AlertItem, PolicyContext } from '../policies/types';
import type { DerivedExpectedPM, DerivedPMTask, PolicyId } from '../policies/types';

export const trucks: Truck[] = trucksData as Truck[];

export const componentHealth: Record<string, ComponentHealth> = componentHealthData as Record<string, ComponentHealth>;

const rawSchedule = pmScheduleData as PMSchedule;
export const pmSchedule: PMSchedule = {
  ...rawSchedule,
  regularSchedule: rawSchedule.regularSchedule ?? rawSchedule.regularPMSchedule ?? [],
};

export const workRecords: WorkRecords = workRecordsData as WorkRecords;

export const alerts: AlertItem[] = alertsData as AlertItem[];

export const chatbotResponses = chatbotResponsesData as Record<string, {
  truckId: string;
  queries: {
    expectedPmTime: { question: string; questionEn: string; answer: string };
    estimatedDuration: { question: string; questionEn: string; answer: string };
    policyReason: {
      question: string;
      questionEn: string;
      answer: {
        title: string;
        expectedPm: string;
        estimatedDuration: string;
        reasons: string[];
      };
    };
  };
}>;

export function buildPolicyContext(): PolicyContext {
  return { trucks, componentHealth, pmSchedule, workRecords, alerts };
}

interface WorkOrder {
  work_order_id: string;
  source_policy: string;
  seed: number;
  step_idx: number;
  truck_id: string;
  action: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  reason: string;
  estimated_duration_hours: number;
  status: string;
  created_at: string;
}

interface LogRecord {
  truck_id: string;
  truck_state: string;
  location: string;
  action: string;
  reason_code: string;
  truck_hi: number;
  tire_hi: number;
  pm_due_hours: number;
}

interface LogPayload {
  records?: LogRecord[];
}

async function loadJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) return null;
    return await response.json() as T;
  } catch {
    return null;
  }
}

function priorityToTaskPriority(priority: WorkOrder['priority']): DerivedPMTask['priority'] {
  if (priority === 'HIGH') return 'critical';
  if (priority === 'MEDIUM') return 'high';
  return 'medium';
}

function latestByTruck(records: LogRecord[]): Record<string, LogRecord> {
  return records.reduce<Record<string, LogRecord>>((acc, record) => {
    acc[record.truck_id] = record;
    return acc;
  }, {});
}

function buildOfficialContext(workOrders: WorkOrder[], records: LogRecord[]): PolicyContext {
  const latest = latestByTruck(records);
  const officialTrucks: Truck[] = Object.entries(latest).map(([truckId, record]) => ({
    id: truckId,
    healthIndex: Math.round(Number(record.truck_hi ?? 0) * 100),
    status: String(record.truck_state || 'STANDBY').toLowerCase(),
    model: '797F-class',
    pmDue: `${Number(record.pm_due_hours ?? 0).toFixed(0)}h`,
    expectedPmTime: `${Number(record.pm_due_hours ?? 0).toFixed(0)}h`,
    estimatedDuration: `${workOrders.find(order => order.truck_id === truckId)?.estimated_duration_hours ?? 0}h`,
    priority: workOrders.find(order => order.truck_id === truckId)?.priority ?? 'LOW',
    reason: workOrders.find(order => order.truck_id === truckId)?.reason ?? record.reason_code ?? 'C5_1_LOG_SNAPSHOT',
  }));

  const officialComponentHealth = officialTrucks.reduce<Record<string, ComponentHealth>>((acc, truck) => {
    const record = latest[truck.id];
    acc[truck.id] = {
      truckId: truck.id,
      components: [
        {
          id: `${truck.id}-TIRE`,
          name: 'Tire set',
          position: 'all',
          healthIndex: Math.round(Number(record?.tire_hi ?? 0) * 100),
          status: Number(record?.tire_hi ?? 0) < 0.5 ? 'warning' : 'normal',
        },
      ],
    };
    return acc;
  }, {});

  const todayPM = workOrders.map(order => ({
    truckId: order.truck_id,
    priority: priorityToTaskPriority(order.priority),
    priorityLabel: order.priority,
    pmDue: `${latest[order.truck_id]?.pm_due_hours?.toFixed?.(0) ?? 'n/a'}h`,
    estimatedDuration: `${order.estimated_duration_hours}h`,
    reason: order.reason,
    showStart: order.status === 'PENDING',
    inProgress: order.status === 'IN_PROGRESS',
  }));

  return {
    trucks: officialTrucks.length ? officialTrucks : trucks,
    componentHealth: Object.keys(officialComponentHealth).length ? officialComponentHealth : componentHealth,
    pmSchedule: {
      ...pmSchedule,
      todayPM,
      summary: {
        total: todayPM.length,
        inProgress: workOrders.filter(order => order.status === 'IN_PROGRESS').length,
        critical: workOrders.filter(order => order.priority === 'HIGH').length,
      },
      plannedToday: workOrders.map(order => ({
        time: 'C5.1',
        truckId: order.truck_id,
        type: order.action,
      })),
    },
    workRecords: {
      ...workRecords,
      summary: {
        ...workRecords.summary,
        plannedToday: workOrders.length,
      },
      plannedToday: workOrders.map(order => ({
        time: 'C5.1',
        truckId: order.truck_id,
        type: order.action,
      })),
    },
    alerts: workOrders.slice(0, 8).map(order => ({
      id: order.work_order_id,
      type: 'pm',
      title: `${order.priority} PM`,
      message: `${order.truck_id} ${order.action}: ${order.reason}`,
      timestamp: order.created_at,
      truckId: order.truck_id,
      read: false,
    })),
  };
}

export async function loadOfficialPolicyContext(): Promise<PolicyContext | null> {
  const [workOrders, logPayload] = await Promise.all([
    loadJson<WorkOrder[]>('/c5_1/work_orders.json'),
    loadJson<LogPayload>('/c5_1/sample_log.json'),
  ]);
  if (!Array.isArray(workOrders) || workOrders.length === 0) return null;
  const records = Array.isArray(logPayload?.records) ? logPayload.records : [];
  return buildOfficialContext(workOrders, records);
}

export function deriveTodayPMTasksFromSchedule(schedule: PMSchedule, selectedPolicy: PolicyId): DerivedPMTask[] {
  const allowedPriorities: DerivedPMTask['priority'][] = ['critical', 'high', 'medium', 'low', 'in-progress'];
  return (schedule.todayPM || []).map(task => ({
    truckId: task.truckId,
    priority: allowedPriorities.includes(task.priority as DerivedPMTask['priority'])
      ? task.priority as DerivedPMTask['priority']
      : 'medium',
    pmDue: task.pmDue,
    expectedPmTime: task.pmDue,
    estimatedDuration: task.estimatedDuration,
    reason: task.reason,
    sourcePolicy: selectedPolicy,
  }));
}

export function deriveExpectedPMFromContext(
  truckId: string,
  context: PolicyContext,
  selectedPolicy: PolicyId,
): DerivedExpectedPM {
  const task = deriveTodayPMTasksFromSchedule(context.pmSchedule, selectedPolicy).find(item => item.truckId === truckId);
  const truck = context.trucks.find(item => item.id === truckId);
  return {
    expectedPmTime: task?.expectedPmTime ?? truck?.expectedPmTime ?? 'No PM window in current snapshot',
    estimatedDuration: task?.estimatedDuration ?? truck?.estimatedDuration ?? 'n/a',
    reason: task?.reason ?? truck?.reason ?? 'No C5.1 work order reason available',
    sourcePolicy: selectedPolicy,
  };
}
