// Decision recommendations surfaced on the operator dashboard.
// These are the heuristic policy's recommended PM actions per truck — the
// "what / which heuristic / why" that the operator approves, holds, or rejects.
//
// Proxy DES decision-support data (not a live Escondida feed).

export const recommendedPolicy = {
  current: 'H3',
  best: 'H3',
  label: 'H3 Cost-Demand Balanced',
  basis: '현재 KPI 가중치(비용·수요·다운타임) 기준 가중 순위 1위',
  note: '수학적 전역 최적 보장 아님 — 현재 KPI 가중치 하의 추천',
  candidates: ['H0', 'H1', 'H2', 'H3', 'H4'],
};

// recommendedAction ∈ Inspect | Repair | Replace | Cooldown | Hold
export const pmRecommendations = [
  {
    id: 'REC-T07',
    truckId: 'T07',
    truckHI: 41,
    tireHI: 61,
    minTireHI: 32,
    riskScore: 92,
    expectedDuration: '2h 30m',
    recommendedAction: 'Replace',
    pmType: '긴급 타이어 교체',
    priority: 'URGENT',
    reason: 'FL 타이어 HI 32% 임계 — 파손 위험. H3가 수요 대비 비용 손실보다 교체 우선으로 판단.',
    heuristic: 'H3',
  },
  {
    id: 'REC-T21',
    truckId: 'T21',
    truckHI: 47,
    tireHI: 55,
    minTireHI: 44,
    riskScore: 80,
    expectedDuration: '1h 40m',
    recommendedAction: 'Repair',
    pmType: '구동부 정비',
    priority: 'HIGH',
    reason: '구동부 HI 47%로 저하, 다운타임 리스크 상승. 비용 가중 하에서 사전 수리가 유리.',
    heuristic: 'H3',
  },
  {
    id: 'REC-T03',
    truckId: 'T03',
    truckHI: 58,
    tireHI: 64,
    minTireHI: 54,
    riskScore: 71,
    expectedDuration: '1h 20m',
    recommendedAction: 'Inspect',
    pmType: '서스펜션 점검',
    priority: 'HIGH',
    reason: 'HI 60% 임계 하회 + 운행 중 이상 진동 감지. 점검으로 원인 확인 후 PM 범위 확정.',
    heuristic: 'H3',
  },
  {
    id: 'REC-T09',
    truckId: 'T09',
    truckHI: 66,
    tireHI: 72,
    minTireHI: 63,
    riskScore: 58,
    expectedDuration: '40m',
    recommendedAction: 'Cooldown',
    pmType: '냉각 후 재투입',
    priority: 'MEDIUM',
    reason: '엔진 온도 상승(고지대·고온). 즉시 PM보다 냉각 대기 후 재투입이 수요 충족에 유리.',
    heuristic: 'H3',
  },
  {
    id: 'REC-T15',
    truckId: 'T15',
    truckHI: 63,
    tireHI: 70,
    minTireHI: 58,
    riskScore: 55,
    expectedDuration: '1h 00m',
    recommendedAction: 'Inspect',
    pmType: '정기 점검',
    priority: 'MEDIUM',
    reason: '정기 점검 도래(캘린더 기준). H3는 큐 여유 시간대에 배치 권고.',
    heuristic: 'H3',
  },
  {
    id: 'REC-T12',
    truckId: 'T12',
    truckHI: 69,
    tireHI: 73,
    minTireHI: 64,
    riskScore: 41,
    expectedDuration: '50m',
    recommendedAction: 'Hold',
    pmType: '대기조 유지',
    priority: 'LOW',
    reason: 'PM 큐 혼잡. 대기조로 보류해 PM Bay 병목을 평활화하는 것이 전체 비용에 유리.',
    heuristic: 'H3',
  },
];

export const actionMeta = {
  Inspect:  { ko: '점검',   color: '#2563EB', bg: '#EFF6FF' },
  Repair:   { ko: '수리',   color: '#D97706', bg: '#FFFBEB' },
  Replace:  { ko: '교체',   color: '#DC2626', bg: '#FEF2F2' },
  Cooldown: { ko: '냉각',   color: '#0891B2', bg: '#ECFEFF' },
  Hold:     { ko: '보류',   color: '#6B7280', bg: '#F9FAFB' },
};

export function riskColor(score) {
  if (score >= 80) return '#DC2626';
  if (score >= 60) return '#F59E0B';
  if (score >= 40) return '#F97316';
  return '#16A34A';
}

export function hiColor(hi) {
  if (hi < 40) return '#DC2626';
  if (hi < 60) return '#F59E0B';
  if (hi < 75) return '#F97316';
  return '#16A34A';
}
