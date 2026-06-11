/**
 * Story Mode data generator.
 *
 * Given a heuristic policy (H1–H4), produces a step-by-step narrative of a
 * fiscal year: each "beat" is a key event/decision point with a short story,
 * the policy's response, the outcome, and the KPI state at that moment.
 *
 * KPIs are interpolated from a common baseline toward the policy's known annual
 * outcome (from policies.js) plus per-event deltas that give each policy its
 * own character (e.g. H1 chases throughput and pays in failures; H2 protects
 * reliability at the cost of demand).
 */
import { policies } from './policies';

const BASELINE = {
  demandFulfill: 80, // %
  pmCost: 13.5,      // M₩
  downtime: 12,      // hrs
  failures: 0,       // count
  totalCost: 40.0,   // M₩
  fleetHI: 86,       // %
  riskTrucks: 2,     // count
};

/** fleetHI / riskTrucks endpoints aren't in policies.js — define per policy. */
const FINAL_EXTRA = {
  H1: { fleetHI: 76, riskTrucks: 6 },
  H2: { fleetHI: 91, riskTrucks: 1 },
  H3: { fleetHI: 86, riskTrucks: 2 },
  H4: { fleetHI: 84, riskTrucks: 3 },
};

const BEATS = [
  {
    day: 1, dayLabel: 'Day 1', title: '운영 개시', progress: 0,
    scenario: '회계연도 첫날. 25대 트럭이 정상 가동을 시작하고, 선택한 휴리스틱이 배차·PM 의사결정을 전담합니다.',
    event: { label: '운영 개시', severity: 'info' },
  },
  {
    day: 58, dayLabel: 'Day 58', title: '첫 정기 PM 사이클', progress: 0.2,
    scenario: '누적 가동으로 일부 차량의 마모가 임계에 근접했습니다. 첫 대규모 정기 PM 시점이 도래했습니다.',
    event: { label: '정기 PM 도래', severity: 'info' },
  },
  {
    day: 134, dayLabel: 'Day 134', title: '수요 급증', progress: 0.42,
    scenario: '제련소 수요가 평소 대비 +18% 급증했습니다. 가동률과 정비 사이의 트레이드오프가 첨예해집니다.',
    event: { label: '수요 +18% 급증', severity: 'warning' },
  },
  {
    day: 212, dayLabel: 'Day 212', title: '고장 위험 누적', progress: 0.62,
    scenario: '구동계·타이어 위험 지표가 동시에 상승했습니다. 비계획 고장 리스크가 커진 구간입니다.',
    event: { label: '고장 위험 상승', severity: 'high' },
  },
  {
    day: 300, dayLabel: 'Day 300', title: '혹서기 부하', progress: 0.82,
    scenario: '여름 혹서로 냉각계 부하와 타이어 발열이 증가했습니다. 가동 안정성이 시험받습니다.',
    event: { label: '혹서기 환경 스트레스', severity: 'warning' },
  },
  {
    day: 365, dayLabel: 'Day 365', title: '연말 결산', progress: 1,
    scenario: '회계연도가 종료되었습니다. 선택한 휴리스틱의 1년 누적 성과를 결산합니다.',
    event: { label: '연간 결산', severity: 'info' },
  },
];

/** Per-policy decision / outcome lines, indexed by beat. */
const NARR = {
  H1: {
    decision: [
      '가동 우선 원칙으로 전 차량을 즉시 투입합니다. 정비는 최소 필수만 수행합니다.',
      'PM을 짧게 끊어 가동 손실을 억제하고, 일부 정비는 다음 기회로 이월합니다.',
      '수요 급증에 전 차량 풀가동. 정비 이월 폭을 키워 생산을 최대로 끌어올립니다.',
      '위험 신호에도 핵심 차량은 계속 투입해 단기 생산을 우선합니다.',
      '혹서에도 가동률을 유지하지만 구동계 피로가 누적됩니다.',
      '최고 수준의 수요 충족을 달성했으나 고장·다운타임 비용이 동반됩니다.',
    ],
    outcome: [
      '수요 충족률 선두로 출발, 차량 건전성은 서서히 하락합니다.',
      '가동 손실은 최소. 다만 이월 정비가 쌓이기 시작합니다.',
      '수요 충족률 급등(최상위). 위험 차량 수도 함께 증가합니다.',
      '비계획 고장이 발생해 다운타임 비용이 상승합니다.',
      '발열 관련 경미 고장이 추가되고 HI가 더 하락합니다.',
      '처리량은 최대지만 총비용은 정비·고장 비용으로 가장 높습니다.',
    ],
  },
  H2: {
    decision: [
      '신뢰성 우선. 보수적 임계로 PM을 선제 집행합니다.',
      '정기 PM을 충실히 수행하고 위험 차량은 즉시 정비로 돌립니다.',
      '수요가 급증해도 안전 임계를 지켜 위험 차량 투입을 자제합니다.',
      '위험 지표 상승 차량을 모두 사전 정비 — 고장을 원천 차단합니다.',
      '혹서기에 냉각계 점검을 강화해 발열 고장을 예방합니다.',
      '무고장 운영을 달성했으나 수요 충족률은 보수적 수준에 머뭅니다.',
    ],
    outcome: [
      '건전성 최상위로 출발, 수요 충족률은 다소 낮습니다.',
      'PM 비용·다운타임은 높지만 고장 위험이 크게 낮아집니다.',
      '수요 충족률은 정체. 대신 위험 차량이 최소로 유지됩니다.',
      '비계획 고장 0건 유지 — 리스크 관리 측면에서 최상.',
      'HI 거의 손실 없음. 환경 스트레스 영향 최소화.',
      '고장 0건·최고 신뢰성. 수요 충족률은 가장 낮습니다.',
    ],
  },
  H3: {
    decision: [
      '비용 가중 균형. 한계 비용이 낮은 정비부터 선별 집행합니다.',
      '가동 손실과 정비 비용을 비교해 PM 시점을 최적화합니다.',
      '수요 급증분은 여유 차량으로 흡수하되 과투입은 피합니다.',
      '위험 차량 중 비용 대비 효과가 큰 건만 선별 정비합니다.',
      '혹서 영향 차량을 비용 기준으로 우선순위화해 대응합니다.',
      '총비용 최저의 균형 잡힌 결과를 달성합니다.',
    ],
    outcome: [
      '모든 지표가 무난한 중간값에서 출발합니다.',
      'PM 비용이 가장 낮게 관리되고 다운타임도 억제됩니다.',
      '수요 충족률이 견조하게 상승, 위험은 낮게 유지됩니다.',
      '고장은 최소화되고 다운타임 증가도 제한적입니다.',
      'HI 하락이 완만 — 비용 효율적으로 방어합니다.',
      '총 운영비용 최저. 전 지표에서 균형이 가장 우수합니다.',
    ],
  },
  H4: {
    decision: [
      '네트워크 흐름 기반으로 경로·배차를 적응적으로 배분합니다.',
      '혼잡을 예측해 PM 일정을 분산, 대기열 적체를 예방합니다.',
      '수요 급증 시 경로를 재배분해 병목 없이 처리량을 늘립니다.',
      '위험 차량을 흐름에 지장 없는 시점에 정비로 빼냅니다.',
      '혹서기 부하를 경로별로 분산해 국소 과부하를 회피합니다.',
      '대기·혼잡을 최소화하며 높은 처리량을 달성합니다.',
    ],
    outcome: [
      '대기시간·혼잡 지표가 가장 안정적으로 출발합니다.',
      '정비 분산으로 PM 다운타임이 평탄하게 관리됩니다.',
      '수요 충족률이 높게 상승하면서 큐 적체는 낮게 유지됩니다.',
      '고장은 소폭 발생하나 흐름 영향은 최소화됩니다.',
      '경로 분산으로 환경 스트레스 영향이 완화됩니다.',
      '혼잡 최소·높은 처리량. 총비용은 중상위 수준입니다.',
    ],
  },
};

/** Per-event KPI deltas (on top of interpolation), resolved per policy. */
const EVENT_DELTAS = [
  {},
  { downtime: 1 },
  {
    demandFulfill: { H1: 4, H2: -3, H3: 1, H4: 3 },
    riskTrucks: { H1: 1, H2: 0, H3: 0, H4: 1 },
  },
  {
    riskTrucks: { H1: 2, H2: 0, H3: 1, H4: 1 },
    failures: { H1: 1, H2: 0, H3: 0, H4: 1 },
    downtime: { H1: 2, H2: 1, H3: 1, H4: 1 },
  },
  { fleetHI: { H1: -3, H2: -1, H3: -2, H4: -2 } },
  {},
];

const smooth = (t) => t * t * (3 - 2 * t);
const lerp = (a, b, t) => a + (b - a) * t;
const round1 = (v) => Math.round(v * 10) / 10;

function resolveDelta(delta, policyId) {
  const out = {};
  for (const [k, v] of Object.entries(delta || {})) {
    out[k] = typeof v === 'object' ? (v[policyId] ?? 0) : v;
  }
  return out;
}

function kpisAt(policyId, beatIndex) {
  const final = policies.find((p) => p.id === policyId);
  const extra = FINAL_EXTRA[policyId] || FINAL_EXTRA.H3;
  const beat = BEATS[beatIndex];
  const e = smooth(beat.progress);
  const d = resolveDelta(EVENT_DELTAS[beatIndex], policyId);

  const k = {
    demandFulfill: lerp(BASELINE.demandFulfill, final.demandFulfill, e) + (d.demandFulfill || 0),
    pmCost: lerp(BASELINE.pmCost, final.pmCost, e) + (d.pmCost || 0),
    downtime: lerp(BASELINE.downtime, final.downtime, e) + (d.downtime || 0),
    totalCost: lerp(BASELINE.totalCost, final.totalCost, e) + (d.totalCost || 0),
    failures: Math.round(lerp(BASELINE.failures, final.failures, e) + (d.failures || 0)),
    fleetHI: lerp(BASELINE.fleetHI, extra.fleetHI, e) + (d.fleetHI || 0),
    riskTrucks: Math.round(lerp(BASELINE.riskTrucks, extra.riskTrucks, e) + (d.riskTrucks || 0)),
  };

  // Final beat reflects the policy's published annual numbers exactly.
  if (beatIndex === BEATS.length - 1) {
    k.demandFulfill = final.demandFulfill;
    k.pmCost = final.pmCost;
    k.downtime = final.downtime;
    k.totalCost = final.totalCost;
    k.failures = final.failures;
    k.fleetHI = extra.fleetHI;
    k.riskTrucks = extra.riskTrucks;
  }

  return {
    demandFulfill: Math.max(0, Math.round(k.demandFulfill)),
    pmCost: round1(k.pmCost),
    downtime: Math.max(0, Math.round(k.downtime)),
    totalCost: round1(k.totalCost),
    failures: Math.max(0, k.failures),
    fleetHI: Math.max(0, Math.round(k.fleetHI)),
    riskTrucks: Math.max(0, k.riskTrucks),
  };
}

/** Build the full story (array of steps) for a policy. */
export function buildStory(policyId) {
  const policy = policies.find((p) => p.id === policyId) || policies[0];
  const id = policy.id;
  const narr = NARR[id] || NARR.H3;

  const steps = BEATS.map((beat, i) => ({
    index: i,
    day: beat.day,
    dayLabel: beat.dayLabel,
    title: beat.title,
    scenario: beat.scenario,
    event: beat.event,
    decision: narr.decision[i],
    outcome: narr.outcome[i],
    kpis: kpisAt(id, i),
  }));

  // Final verdict line summarising the whole run.
  const verdict = {
    H1: '결론: 생산 최우선. 수요 충족률은 최고지만 고장·다운타임 비용이 가장 큽니다. 수요 폭증기 단기 운영에 적합.',
    H2: '결론: 신뢰성 최우선. 무고장·최고 건전성을 달성하나 수요 충족률은 보수적. 고장 리스크가 큰 환경에 적합.',
    H3: '결론: 비용 균형 최적. 총 운영비용이 가장 낮고 전 지표가 균형적. 평상시 기본 정책으로 권장.',
    H4: '결론: 흐름 적응. 혼잡·대기를 최소화하며 높은 처리량 확보. 경로 혼잡이 잦은 환경에 적합.',
  }[id];

  return { policy, steps, verdict };
}

export const STORY_KPI_META = [
  { key: 'demandFulfill', label: '수요 충족률', unit: '%', betterHigh: true },
  { key: 'fleetHI', label: '평균 건전성(HI)', unit: '%', betterHigh: true },
  { key: 'pmCost', label: 'PM 비용', unit: 'M₩', betterHigh: false },
  { key: 'downtime', label: '다운타임', unit: 'h', betterHigh: false },
  { key: 'failures', label: '비계획 고장', unit: '건', betterHigh: false },
  { key: 'riskTrucks', label: '위험 차량', unit: '대', betterHigh: false },
  { key: 'totalCost', label: '총 운영비용', unit: 'M₩', betterHigh: false },
];
