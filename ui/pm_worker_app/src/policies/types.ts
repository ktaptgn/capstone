export type PolicyId =
  | "baseline"
  | "h1_production_bottleneck"
  | "h2_reliability_pm"
  | "h3_cost_weighted"
  | "h4_network_flow";

export interface Truck {
  id: string;
  healthIndex: number;
  status: string;
  model: string;
  pmDue: string;
  expectedPmTime: string;
  estimatedDuration: string;
  priority: string;
  reason: string;
}

export interface TireComponent {
  id: string;
  name: string;
  position: string;
  healthIndex: number;
  status: string;
}

export interface ComponentHealth {
  truckId: string;
  components: TireComponent[];
  otherComponents?: { id: string; name: string; healthIndex: number; status: string }[];
}

export interface PMScheduleItem {
  truckId: string;
  priority: string;
  priorityLabel: string;
  pmDue: string;
  estimatedDuration: string;
  reason: string;
  showStart: boolean;
  inProgress: boolean;
}

export interface RegularScheduleItem {
  label: string;
  cycle: string;
  next: string;
  truckCount: string;
}

export interface ThisWeekPMDay {
  day: string;
  trucks: string[];
  isToday: boolean;
}

export interface PMSchedule {
  todayPM: PMScheduleItem[];
  summary: { total: number; inProgress: number; critical: number };
  thisWeekPM: ThisWeekPMDay[];
  regularSchedule?: RegularScheduleItem[];
  regularPMSchedule?: RegularScheduleItem[];
  plannedToday: { time: string; truckId: string; type: string }[];
}

export interface WorkRecordEntry {
  id: string;
  date: string;
  truckId: string;
  type: string;
  result: string;
  duration: string;
  note?: string;
}

export interface InProgressWork {
  truckId: string;
  pmType: string;
  startedAt: string;
  elapsed: string;
  progress: number;
}

export interface WorkRecords {
  summary: { last7Days: number; inProgress: number; plannedToday: number };
  inProgress: InProgressWork[];
  plannedToday: { time: string; truckId: string; type: string }[];
  last7Days: WorkRecordEntry[];
  previousPMByTruck: Record<string, { date: string; type: string; result: string; duration: string }[]>;
}

export interface AlertItem {
  id: string;
  type: string;
  title: string;
  message: string;
  timestamp: string;
  truckId: string;
  read: boolean;
}

export interface PolicyContext {
  trucks: Truck[];
  componentHealth: Record<string, ComponentHealth>;
  pmSchedule: PMSchedule;
  workRecords: WorkRecords;
  alerts: AlertItem[];
}

export interface DerivedPMTask {
  truckId: string;
  priority: "critical" | "high" | "medium" | "low" | "in-progress";
  pmDue: string;
  expectedPmTime: string;
  estimatedDuration: string;
  reason: string;
  sourcePolicy: PolicyId;
}

export interface DerivedExpectedPM {
  expectedPmTime: string;
  estimatedDuration: string;
  reason: string;
  sourcePolicy: PolicyId;
}
