// Scenario presets for the Overview page. Selecting one overrides the headline
// KPI cards and injects scenario-specific map warnings (proxy/mock data).

export const OVERVIEW_SCENARIOS = [
  {
    id: 'normal',
    label: 'Normal',
    banner: '기준 운영 상태 — H3 권고 적용',
    kpi: {},
    warnings: [],
  },
  {
    id: 'high_demand',
    label: 'High Demand',
    banner: '수요 급증 — 가동 우선, PM 지연 리스크 상승',
    kpi: { demandFulfillment: 72, riskTrucks: 6, trucksInPM: 4, activePM: 2, queuedPM: 2 },
    warnings: [{ label: '수요 미달', detail: '목표 대비 -12%p', severity: 'high' }],
  },
  {
    id: 'road_risk',
    label: 'Road Risk',
    banner: '고위험 경로 활성 — 충돌·노면 마모 경보',
    kpi: { riskTrucks: 7, pmCostMKRW: 15.1, totalCostMKRW: 42.8 },
    warnings: [{ label: '경로 위험 확대', detail: '고위험 구간 차량 3대 근접', severity: 'high' }],
  },
  {
    id: 'pm_bottleneck',
    label: 'PM Bay Bottleneck',
    banner: 'PM Bay 병목 — 대기열 적체, 가동률 하락',
    kpi: { trucksInPM: 6, activePM: 2, queuedPM: 4, availableTrucks: 15 },
    warnings: [{ label: 'PM 큐 적체', detail: '대기 4대 · Bay 2/2 사용', severity: 'warning' }],
  },
  {
    id: 'tire_failure',
    label: 'Tire Failure Event',
    banner: '타이어 고장 다발 — 긴급 교체 수요 급증',
    kpi: { riskTrucks: 8, criticalTireCount: 5, pmCostMKRW: 16.7 },
    warnings: [{ label: '타이어 고장 다발', detail: '임계 타이어 5건 (교체 필요)', severity: 'high' }],
  },
];
