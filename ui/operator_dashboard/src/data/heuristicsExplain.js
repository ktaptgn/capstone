// H0–H4 heuristic explanations for the operator dashboard.
// "Which heuristic recommends the decision, and why" — interpretable summary
// of each policy used in the C5.1 proxy DES comparison.

export const heuristicsExplain = [
  {
    id: 'H0',
    name: 'Periodic PM Baseline (순수 주기 정비)',
    color: '#64748B',
    definition: '트럭 상태와 무관하게 설정된 캘린더 주기에 맞춰 PM을 수행하는 기준선.',
    rule: '트럭별 분산 캘린더 슬롯 도래 시 PM_VEHICLE 수행.',
    benefit: '일정이 단순하고 다른 휴리스틱의 비교 기준이 명확함.',
    weakness: '실제 상태와 수요를 무시해 과잉 정비 가능.',
    kpi: { totalCost: '4,283 CU', demand: '87.0%', downtime: '높음' },
  },
  {
    id: 'H1',
    name: 'Due / Health PM (기본 상태 정비)',
    color: '#2563EB',
    definition: '기존 H0 정책으로, PM due time 또는 HI 임계 도달 시 정비.',
    rule: 'PM due/Truck HI/Tire HI 조건 확인 후 PM, 아니면 기본 배차.',
    benefit: '주기 기준선보다 실제 열화 상태를 반영.',
    weakness: '큐·비용·흐름 최적화 없이 첫 대상 기준으로 결정.',
    kpi: { totalCost: '1,859 CU', demand: '94.7%', downtime: '중간' },
  },
  {
    id: 'H2',
    name: 'HI Threshold PM (상태 기반)',
    color: '#7C3AED',
    definition: '건강지수(HI)가 임계값 아래로 떨어지면 PM을 수행.',
    rule: 'HI < 임계값(예: 60%)이면 해당 트럭 PM 우선 배치.',
    benefit: '실제 상태를 반영해 고장을 사전 예방.',
    weakness: '수요·PM Bay 큐 미고려 → 동시 다발 PM로 병목.',
    kpi: { totalCost: '3,339 CU', demand: '81.5%', downtime: '낮음~중간' },
  },
  {
    id: 'H3',
    name: 'Cost-Demand Balanced (비용·수요 균형)',
    color: '#16A34A',
    definition: '위험·비용·수요를 가중 결합한 점수로 PM 우선순위를 결정.',
    rule: 'score = w₁·위험 + w₂·비용손실 + w₃·수요영향 → 상위부터 PM.',
    benefit: '비용과 수요 충족을 균형 → 현재 KPI 가중치 기준 1위.',
    weakness: '가중치 설정에 민감, 수학적 전역 최적은 아님.',
    kpi: { totalCost: '1,725 CU', demand: '97.1%', downtime: '낮음' },
    best: true,
  },
  {
    id: 'H4',
    name: 'Queue-first + Due PM (큐 우선)',
    color: '#0891B2',
    definition: 'PM Bay 큐 여유를 우선 활용하고 도래분 PM을 함께 처리.',
    rule: 'PM Bay 여유 슬롯이 있을 때 도래/임박 PM을 우선 투입.',
    benefit: 'PM Bay 병목 완화, 가동률(available) 유지에 유리.',
    weakness: '긴급 위험 트럭이 큐 상황에 따라 후순위가 될 수 있음.',
    kpi: { totalCost: '7,063 CU', demand: '49.8%', downtime: '낮음~중간' },
  },
];

export const heuristicsNote =
  '※ KPI 값은 C5.1 proxy DES(동일 환경·시드) 비교의 대표 수치입니다. 실제 Escondida 디지털 트윈이 아니라 열화 인지 기반 의사결정을 보여주는 의사결정 지원 모델입니다.';
