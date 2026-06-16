/**
 * C5.4 — Joint PM-scheduling + Dispatch benchmark (in-lab, not an official C5.1 ranking).
 *
 * Source of truth: docs/source/07_C5_4_RESULTS.md
 *   Environment: 25-truck C5 mine + C6 routes A/B/C; 3-component HI (tire/engine/brake),
 *   Gamma-frailty wear heterogeneity + C6 sensor noise. Decision target = JOINT PM-scheduling
 *   + dispatch. Objective = total TCO (pm + cm + downtime + degradation + unmet).
 *   30 held-out seeds × 365 days per regime. Lower TCO is better.
 *
 * Policies are PM-family × dispatch-family pairs:
 *   H0     calendar       + route-blind   (baseline)
 *   H_TIME operating-hours+ route-blind
 *   H1     CBM(HI)        + health
 *   H2     risk-priority  + risk-aware
 *   H3     cost-value     + value
 *   H4     flow/backpres. + capacity
 */

export const C5_4_META = {
  seeds: 30,
  days: 365,
  trucks: 25,
  components: ['tire', 'engine', 'brake'],
  objective: 'Total TCO = PM + CM + 다운타임 + 열화 + 미충족 비용',
  basisKo: '인-랩 벤치마크 (30 시드 × 365일, held-out)',
};

export const C5_4_POLICIES = {
  H0:     { id: 'H0-α',   name: 'Calendar + Route-blind',        pm: '고정 달력 주기 PM',     dispatch: '경로 무시 배차',   family: 'blind',       color: '#64748B' },
  H_TIME: { id: 'H0-β',   name: 'Operating-hours + Route-blind', pm: '가동시간 기준 PM',      dispatch: '경로 무시 배차',   family: 'blind',       color: '#94A3B8' },
  H1:     { id: 'H1',     name: 'CBM + Health',                  pm: '상태기반(HI 임계) PM',  dispatch: '건전성 기반 배차', family: 'state-aware', color: '#2563EB' },
  H2:     { id: 'H2',     name: 'Risk + Risk-aware',             pm: '위험점수 우선 PM',      dispatch: '위험회피 배차',    family: 'state-aware', color: '#7C3AED' },
  H3:     { id: 'H3',     name: 'Cost-value + Value',            pm: '비용가치 기반 PM',      dispatch: '가치 기반 배차',   family: 'state-aware', color: '#16A34A' },
  H4:     { id: 'H4',     name: 'Flow + Capacity',               pm: '흐름/백프레셔 PM',      dispatch: '용량 기반 배차',   family: 'state-aware', color: '#0891B2' },
};

export const FAMILY_LABEL = {
  blind: '시간 주기',
  'state-aware': '상태기반',
};

/** Per-regime aggregate KPIs (mean over 30 seeds), highest→lowest TCO rank. */
export const C5_4_REGIMES = [
  {
    id: 'heterogeneous_condition',
    label: '표준 (heterogeneous)',
    best: 'H2',
    headlineImprovementPct: 40.4,
    desc: '기본 마모 이질성(Gamma frailty) 조건 — 신뢰성이 재량적 효율 레버인 환경.',
    rows: [
      { policy: 'H2',     tco: 22367.1, pmVisits: 3070, pmComps: 3082, cmPerRun: 0.1,   fulfil: 1.000, endHI: 0.321, downHrs: 10901 },
      { policy: 'H1',     tco: 22385.6, pmVisits: 3071, pmComps: 3082, cmPerRun: 0.0,   fulfil: 1.000, endHI: 0.335, downHrs: 10912 },
      { policy: 'H3',     tco: 23675.1, pmVisits: 3183, pmComps: 3269, cmPerRun: 0.0,   fulfil: 1.000, endHI: 0.727, downHrs: 11552 },
      { policy: 'H4',     tco: 23740.3, pmVisits: 3196, pmComps: 3289, cmPerRun: 0.1,   fulfil: 1.000, endHI: 0.741, downHrs: 11575 },
      { policy: 'H_TIME', tco: 36693.7, pmVisits: 1588, pmComps: 4764, cmPerRun: 66.4,  fulfil: 1.000, endHI: 0.833, downHrs: 18176 },
      { policy: 'H0',     tco: 37547.9, pmVisits: 1594, pmComps: 4782, cmPerRun: 95.9,  fulfil: 1.000, endHI: 0.838, downHrs: 18572 },
    ],
  },
  {
    id: 'high_stress',
    label: '고스트레스 (high_stress)',
    best: 'H1',
    headlineImprovementPct: 24.9,
    desc: '마모·위험 가속 조건 — 모든 정책이 PM을 늘려야 하고 고장 경로가 활성화.',
    rows: [
      { policy: 'H1',     tco: 32564.6, pmVisits: 3922, pmComps: 4013, cmPerRun: 2.4,   fulfil: 1.000, endHI: 0.317, downHrs: 15759 },
      { policy: 'H2',     tco: 32584.2, pmVisits: 3927, pmComps: 4012, cmPerRun: 3.6,   fulfil: 1.000, endHI: 0.302, downHrs: 15768 },
      { policy: 'H3',     tco: 33689.7, pmVisits: 3651, pmComps: 4130, cmPerRun: 13.3,  fulfil: 1.000, endHI: 0.717, downHrs: 16260 },
      { policy: 'H4',     tco: 33807.0, pmVisits: 3615, pmComps: 4145, cmPerRun: 17.4,  fulfil: 1.000, endHI: 0.719, downHrs: 16302 },
      { policy: 'H_TIME', tco: 42519.7, pmVisits: 1456, pmComps: 4368, cmPerRun: 256.4, fulfil: 1.000, endHI: 0.652, downHrs: 20297 },
      { policy: 'H0',     tco: 43361.6, pmVisits: 1460, pmComps: 4380, cmPerRun: 276.7, fulfil: 1.000, endHI: 0.715, downHrs: 20676 },
    ],
  },
  {
    id: 'high_demand_high_stress',
    label: '고수요·고스트레스',
    best: 'H1',
    headlineImprovementPct: 17.0,
    desc: '수요 > 경로 용량 — 병목이 정비가 아닌 처리량(충족률 0.934)으로 이동.',
    rows: [
      { policy: 'H1',     tco: 47630.8, pmVisits: 3615, pmComps: 4308, cmPerRun: 44.1,  fulfil: 0.934, endHI: 0.275, downHrs: 17272 },
      { policy: 'H2',     tco: 47654.6, pmVisits: 3674, pmComps: 4300, cmPerRun: 46.4,  fulfil: 0.934, endHI: 0.262, downHrs: 17288 },
      { policy: 'H3',     tco: 48046.9, pmVisits: 3380, pmComps: 4382, cmPerRun: 42.4,  fulfil: 0.934, endHI: 0.647, downHrs: 17469 },
      { policy: 'H4',     tco: 48070.8, pmVisits: 3297, pmComps: 4374, cmPerRun: 48.2,  fulfil: 0.934, endHI: 0.646, downHrs: 17461 },
      { policy: 'H_TIME', tco: 56673.4, pmVisits: 1456, pmComps: 4368, cmPerRun: 346.2, fulfil: 0.934, endHI: 0.579, downHrs: 21354 },
      { policy: 'H0',     tco: 57397.1, pmVisits: 1460, pmComps: 4380, cmPerRun: 360.1, fulfil: 0.934, endHI: 0.621, downHrs: 21687 },
    ],
  },
];

/** Identical best→worst order across all three regimes (only the within-pair flips). */
export const C5_4_RANKING_KO = 'H1 ≈ H2  <  H3 ≈ H4  <  H0-β  <  H0-α  (세 조건 모두 동일)';

export const C5_4_NOTES = [
  '통합 상태기반 PM+배차(H1 CBM·H2 위험)가 시간 주기 PM(H0 달력·H_TIME 가동시간) 대비 TCO를 40.4% / 24.9% / 17.0% 절감하며, 세 조건 모두 30/30 시드에서 우위입니다.',
  'H1·H2는 거의 동일한 신호(관측 HI vs 위험점수)로 PM을 트리거하므로 차이가 센서노이즈 수준(<0.1%)입니다. 방어되는 명제는 "상태기반 ≫ 시간 주기".',
  '시간 주기 기준선은 두 축에서 동시에 손해 — (1) 과정비: 고정 주기로 전차량 정비(부품 PM ≈ 방문의 3배), 종료시 과정비(endHI 0.84). (2) 꼬리 미보호: 무거운 방문이 PM Bay 2개를 포화시켜 빠른 마모 트럭을 못 잡고 고장 → CM 66~96 → 257~360/run, 그중 ~66%가 타이어.',
  '상태기반은 약 2배 많은 "짧고 표적화된" PM(≈1부품, 타이어 집중)으로 Bay 용량에 맞추고 트럭을 임계까지 운용(endHI 0.32)하여 고장 ~0(표준)/≤7(스트레스)을 달성 — PM 비용도 오히려 더 적습니다.',
  'H3·H4(2군)는 시간 주기보다 우수하나 트리거가 더 많은 마모를 허용해 스트레스에서 고장 꼬리가 생깁니다(CM 13→42, 17→48). 종료 HI가 높음(0.65~0.74).',
  '스트레스가 커질수록 우위가 축소(40%→25%→17%)됩니다. 고수요 극단에선 병목이 처리량(충족률 0.934)이라 H1/H2 vs H3/H4 격차가 <1%로 좁혀집니다.',
];

export const C5_4_LIMITATIONS = [
  '인-랩 벤치마크이며 공식 정책 랭킹이 아닙니다.',
  'TCO는 정규화/리포트 값으로, 비용 단위 가정에 의존합니다.',
  'endHI는 종료시점 스냅샷입니다 — 상태기반의 낮은 값(0.32)은 임계 부근 운용이라는 의도된 동작이며 건강 악화가 아닙니다.',
  '시간 주기는 steelmanned(최단 주기)이며, 주기 민감도(3→8)는 민감도 분석에서 robust로 확인됩니다.',
  '비극단 조건에서 충족률=1.000이므로 TCO 격차는 전부 "정비 효율"이며 생산 손실이 아닙니다.',
];

/** % TCO improvement vs the H0 baseline within a regime (positive = cheaper than H0). */
export function improvementVsH0(regime) {
  const h0 = regime.rows.find((r) => r.policy === 'H0');
  const base = h0 ? h0.tco : null;
  return regime.rows.map((r) => ({
    ...r,
    improvementPct: base ? ((base - r.tco) / base) * 100 : 0,
  }));
}
