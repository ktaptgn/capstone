// Heuristic policy definitions — C5.4 Joint PM-scheduling + Dispatch benchmark.
// 6 policies: H0, H_TIME, H1, H2, H3, H4. KPI values from 30-seed × 365-day runs.

export const heuristicsExplain = [
  {
    id: 'H0-α',
    name: 'Calendar + Route-blind (달력 주기 기준선)',
    color: '#64748B',
    definition: '고정 달력 주기에 따라 PM을 수행하고 경로를 무시한 배차를 사용하는 기준선.',
    rule: '캘린더 도래 시 PM 수행, 배차는 경로 무관하게 할당.',
    benefit: '일정이 단순하고 예측 가능. 비교 기준선.',
    weakness: '실제 부품 상태와 수요를 무시. 고장 꼬리 노출(CM ~96/run). 과잉 정비 발생.',
    kpi: { totalCost: '37,548 CU', demand: '100%', cmPerRun: '95.9', endHI: '83.8%' },
  },
  {
    id: 'H0-β',
    name: 'Operating-hours + Route-blind (가동시간 주기)',
    color: '#94A3B8',
    definition: '가동시간 기준으로 PM을 트리거하고 경로 무관 배차를 사용.',
    rule: '누적 가동시간 임계 도달 시 PM 수행, 배차는 경로 무관.',
    benefit: '달력 기준보다 실제 마모를 일부 반영.',
    weakness: 'CM ~66/run으로 고장 꼬리 여전히 큼. 상태기반 대비 TCO 56% 높음.',
    kpi: { totalCost: '36,694 CU', demand: '100%', cmPerRun: '66.4', endHI: '83.3%' },
  },
  {
    id: 'H1',
    name: 'CBM + Health (상태기반 PM + 건전성 배차)',
    color: '#2563EB',
    definition: '부품 HI 임계 도달 시 PM을 트리거하고 건전성 기반으로 배차.',
    rule: 'HI < 임계값 → PM 수행. 배차는 차량 건전성 순위 기반.',
    benefit: '상태기반 정밀 PM + 건전성 배차로 CM≈0. TCO를 H0 대비 40.4% 절감.',
    weakness: '임계 운용으로 종료 HI 낮음(33.5%). 스트레스 환경에서 CM 꼬리 발생 가능.',
    kpi: { totalCost: '22,386 CU', demand: '100%', cmPerRun: '0.0', endHI: '33.5%' },
    best: true,
  },
  {
    id: 'H2',
    name: 'Risk + Risk-aware (위험점수 PM + 위험회피 배차)',
    color: '#7C3AED',
    definition: '위험점수 우선 PM과 위험회피 배차를 결합.',
    rule: '위험점수 높은 트럭 우선 PM. 배차는 위험 회피 경로 할당.',
    benefit: 'H1과 거의 동일한 성능(TCO 차이 <0.1%). 표준 조건 최적 정책.',
    weakness: '임계 운용 구조는 H1과 동일. 신호 차이는 센서노이즈 수준.',
    kpi: { totalCost: '22,367 CU', demand: '100%', cmPerRun: '0.1', endHI: '32.1%' },
  },
  {
    id: 'H3',
    name: 'Cost-value + Value (비용가치 PM + 가치 배차)',
    color: '#16A34A',
    definition: '비용가치 점수로 PM 우선순위를 결정하고 가치 기반으로 배차.',
    rule: 'cost-value 점수 = PM비용 절감 가치. 상위 트럭부터 PM. 배차는 가치 순위.',
    benefit: 'H0 대비 40% 절감. 시간 주기 기준 대비 확실한 우위.',
    weakness: '2군 정책 — H1/H2보다 CM 꼬리 더 큼(스트레스 CM 13/run). 종료 HI 높음.',
    kpi: { totalCost: '23,675 CU', demand: '100%', cmPerRun: '0.0', endHI: '72.7%' },
  },
  {
    id: 'H4',
    name: 'Flow + Capacity (흐름/백프레셔 PM + 용량 배차)',
    color: '#0891B2',
    definition: '흐름·백프레셔 기반 PM과 용량 기반 배차.',
    rule: 'PM Bay 용량·흐름을 반영한 PM 스케줄링. 배차는 용량 기반.',
    benefit: 'H0 대비 37% 절감. H3와 동일 수준의 2군 성능.',
    weakness: '스트레스 환경에서 CM 꼬리 발생(CM 17→48/run). 종료 HI 높음.',
    kpi: { totalCost: '23,740 CU', demand: '100%', cmPerRun: '0.1', endHI: '74.1%' },
  },
];

export const heuristicsNote =
  '※ KPI 값은 표준 조건(heterogeneous regime) 기준 30-seed 평균입니다. 공통 순위: H1 ≈ H2 < H3 ≈ H4 < H0-β < H0-α (세 조건 모두 동일).';
