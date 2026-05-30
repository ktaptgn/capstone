import type {
  C5OperationMap3DData,
  Facility3D,
  Route3D,
  Vec3,
} from './map3dTypes';

const DEFAULT_STATUS_COLORS: Record<string, string> = {
  NORMAL: '#94A3B8',
  ACTIVE: '#8A4931',
  WARNING: '#F59E0B',
  CRITICAL: '#DC2626',
  HIGH: '#DC2626',
  'IN-PROGRESS': '#7C3AED',
  IN_PROGRESS: '#7C3AED',
  STANDBY: '#6B7280',
};

function normalizeStatus(status?: string): string {
  return String(status || 'normal').trim().toUpperCase().replace(/\s+/g, '_');
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function getStatusColor(
  status: string,
  statusColorMap: Record<string, string> = {},
): string {
  const normalized = normalizeStatus(status);
  return statusColorMap[normalized] || DEFAULT_STATUS_COLORS[normalized] || '#6B7280';
}

export function getFacilityColor(status?: string, riskLevel?: string): string {
  const normalizedRisk = normalizeStatus(riskLevel);
  const normalizedStatus = normalizeStatus(status);

  if (normalizedRisk === 'HIGH' || normalizedStatus === 'CRITICAL') return '#F8E7E7';
  if (normalizedRisk === 'WARNING' || normalizedStatus === 'WARNING') return '#FFF3D2';
  if (normalizedStatus === 'IN-PROGRESS' || normalizedStatus === 'IN_PROGRESS') return '#EFE9FF';
  if (normalizedStatus === 'STANDBY') return '#EEF1F5';
  if (normalizedStatus === 'ACTIVE') return '#F1E4DC';
  return '#F8FAFC';
}

export function getFacilityAccentColor(status?: string, riskLevel?: string): string {
  if (normalizeStatus(riskLevel) === 'HIGH') return '#DC2626';
  return getStatusColor(status || riskLevel || 'normal', {});
}

export function getRouteColor(riskLevel: string, kind?: string): string {
  if (kind === 'conveyor_feed') return '#475569';
  if (kind === 'service_road') return '#64748B';
  if (riskLevel === 'high') return '#DC2626';
  if (riskLevel === 'warning') return '#F59E0B';
  return '#334155';
}

export function getCubeSize(facility: Facility3D): number {
  const rawSize = Math.max(
    facility.size?.width ?? 12,
    facility.size?.depth ?? 12,
    facility.size?.height ?? 8,
  ) * 0.35;
  return clamp(rawSize || 10, 6, 28);
}

export function getRouteMidpoint(route: Route3D): Vec3 {
  if (!route.points.length) return { x: 0, y: 0, z: 0 };
  if (route.points.length === 1) return route.points[0];

  const midpointIndex = Math.floor((route.points.length - 1) / 2);
  const current = route.points[midpointIndex];
  const next = route.points[midpointIndex + 1] || current;
  return {
    x: (current.x + next.x) / 2,
    y: (current.y + next.y) / 2,
    z: (current.z + next.z) / 2,
  };
}

export function findTargetPosition(
  targetId: string,
  data: C5OperationMap3DData,
): Vec3 | null {
  const truck = data.truckFrames.find((item) => item.truck_id === targetId);
  if (truck) return truck.position;

  const facility = data.facilities.find((item) => item.id === targetId);
  if (facility) return facility.position;

  const queueArea = data.queueAreas.find((item) => item.id === targetId);
  if (queueArea) return queueArea.position;

  const route = data.routes.find((item) => item.id === targetId);
  if (route) return getRouteMidpoint(route);

  return null;
}

export function getTruckHIColor(truckHI: number, truckState: string): string {
  if (truckState === 'STANDBY' || truckHI >= 0.95) return '#3B82F6';
  if (truckHI >= 0.7) return '#22C55E';
  if (truckHI >= 0.5) return '#F97316';
  return '#EF4444';
}

export function getQueueRatioColor(ratio: number): string {
  if (ratio <= 0.25) return '#3B82F6';
  if (ratio <= 0.5) return '#22C55E';
  if (ratio <= 0.75) return '#F97316';
  return '#EF4444';
}
