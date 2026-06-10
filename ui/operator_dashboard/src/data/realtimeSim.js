/**
 * Front-end rule engine for the Realtime Simulation mode.
 *
 * A sim clock advances in ticks; every KPI drifts toward the *active heuristic's*
 * steady-state target. Operator actions (switch heuristic, send a risk truck to
 * PM, issue a dispatch order) apply immediate, decaying effects on top — so the
 * operator sees cause→effect in real time without any backend.
 */

export const FLEET_SIZE = 25;
export const TICK_MIN = 10;          // sim minutes advanced per tick
export const SHIFT_START_MIN = 6 * 60; // 06:00

/** Steady-state KPI targets per heuristic (the sim drifts toward these). */
export const HEURISTIC_TARGETS = {
  H1: { demandFulfillment: 92, fleetHI: 77, riskTrucks: 5, throughput: 112, costRate: 1.30 },
  H2: { demandFulfillment: 76, fleetHI: 90, riskTrucks: 1, throughput: 88, costRate: 1.16 },
  H3: { demandFulfillment: 84, fleetHI: 86, riskTrucks: 2, throughput: 98, costRate: 1.00 },
  H4: { demandFulfillment: 88, fleetHI: 84, riskTrucks: 3, throughput: 105, costRate: 1.10 },
};

export const HEURISTIC_LABEL = {
  H1: 'Production / Bottleneck',
  H2: 'Reliability / PM',
  H3: 'Cost-weighted',
  H4: 'Adaptive Network Flow',
};

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const lerp = (a, b, t) => a + (b - a) * t;

export function fmtClock(min) {
  const m = ((min % 1440) + 1440) % 1440;
  const h = Math.floor(m / 60);
  const mm = Math.floor(m % 60);
  return `${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
}

export function createInitialState(heuristic = 'H3') {
  const t = HEURISTIC_TARGETS[heuristic];
  return {
    clock: SHIFT_START_MIN,
    activeHeuristic: heuristic,
    kpis: {
      demandFulfillment: t.demandFulfillment,
      fleetHI: t.fleetHI,
      riskTrucks: t.riskTrucks,
      pmQueue: 1,
      throughput: t.throughput,
      costRate: t.costRate,
      cumLoads: 0,
    },
    pmJobs: [],          // active PM jobs: array of remaining minutes (max 2 bays)
    effects: [],         // { kpi, delta, ttl, life }
    log: [{ t: SHIFT_START_MIN, text: `교대 시작 — ${heuristic} 정책으로 운영 개시`, type: 'info' }],
    history: [{ t: SHIFT_START_MIN, demand: t.demandFulfillment, fleetHI: t.fleetHI }],
    actionCount: 0,
  };
}

function pushLog(state, text, type = 'info') {
  state.log = [{ t: state.clock, text, type }, ...state.log].slice(0, 60);
}

function effectSum(effects, kpi) {
  return effects.reduce((s, e) => (e.kpi === kpi ? s + e.delta * (e.ttl / e.life) : s), 0);
}

function tick(prev, dt) {
  const s = {
    ...prev,
    kpis: { ...prev.kpis },
    pmJobs: prev.pmJobs.map((j) => j - dt).filter((j) => j > -1e9),
    effects: prev.effects.map((e) => ({ ...e, ttl: e.ttl - dt })).filter((e) => e.ttl > 0),
    log: prev.log,
    history: prev.history,
  };

  // PM bays: complete finished jobs, then pull from the queue (max 2 bays).
  const finished = s.pmJobs.filter((j) => j <= 0).length;
  s.pmJobs = s.pmJobs.filter((j) => j > 0);
  for (let i = 0; i < finished; i++) {
    s.kpis.fleetHI = clamp(s.kpis.fleetHI + 1.6, 0, 100);
    pushLog(s, 'PM 완료 — 정비 차량 복귀, 가용 +1', 'good');
  }
  while (s.pmJobs.length < 2 && s.kpis.pmQueue > 0) {
    s.kpis.pmQueue -= 1;
    s.pmJobs.push(70 + Math.random() * 50);
  }

  const target = HEURISTIC_TARGETS[s.activeHeuristic];
  const k = s.kpis;
  const r = clamp(dt / 90, 0, 0.5); // drift rate

  const pmActive = s.pmJobs.length;
  const inPM = pmActive + k.pmQueue;
  const availability = clamp((FLEET_SIZE - inPM) / (FLEET_SIZE - 2), 0.4, 1.05);

  // Drift toward heuristic targets, modulated by current availability.
  k.fleetHI = clamp(lerp(k.fleetHI, target.fleetHI, r) + effectSum(s.effects, 'fleetHI') * 0.04, 40, 100);
  k.riskTrucks = clamp(lerp(k.riskTrucks, target.riskTrucks, r * 0.7) + effectSum(s.effects, 'riskTrucks') * 0.04, 0, 12);
  k.throughput = clamp(lerp(k.throughput, target.throughput * availability, r) + effectSum(s.effects, 'throughput') * 0.05, 40, 140);
  k.demandFulfillment = clamp(
    lerp(k.demandFulfillment, target.demandFulfillment * clamp(availability, 0.7, 1), r) + effectSum(s.effects, 'demandFulfillment') * 0.05,
    30, 100,
  );
  k.costRate = clamp(lerp(k.costRate, target.costRate, r) + effectSum(s.effects, 'costRate') * 0.04, 0.7, 2);
  k.cumLoads += (k.throughput * dt) / 60;

  // Occasional organic risk → PM demand when reliability is stretched.
  if (k.riskTrucks > target.riskTrucks + 2 && k.pmQueue + pmActive < 4 && Math.random() < 0.18) {
    k.pmQueue += 1;
    k.riskTrucks = clamp(k.riskTrucks - 1, 0, 12);
    pushLog(s, '자동 감지: 위험 차량 1대 PM 대기열 편입', 'warn');
  }

  s.clock = prev.clock + dt;

  // Sample history roughly every 30 sim-min.
  const lastT = s.history[s.history.length - 1]?.t ?? -999;
  if (s.clock - lastT >= 30) {
    s.history = [...s.history, { t: s.clock, demand: Math.round(k.demandFulfillment), fleetHI: Math.round(k.fleetHI) }].slice(-80);
  }

  return s;
}

function addEffect(state, kpi, delta, life) {
  state.effects = [...state.effects, { kpi, delta, ttl: life, life }];
}

export function simReducer(state, action) {
  switch (action.type) {
    case 'TICK':
      return tick(state, action.dt ?? TICK_MIN);

    case 'SET_HEURISTIC': {
      if (action.id === state.activeHeuristic) return state;
      const s = { ...state, activeHeuristic: action.id, kpis: { ...state.kpis }, effects: [...state.effects] };
      pushLog(s, `정책 전환: ${state.activeHeuristic} → ${action.id} (${HEURISTIC_LABEL[action.id]})`, 'info');
      return s;
    }

    case 'PM_DISPATCH': {
      const s = { ...state, kpis: { ...state.kpis }, effects: [...state.effects] };
      if (s.kpis.riskTrucks <= 0) {
        pushLog(s, '지시 무시: 위험 차량이 없습니다', 'warn');
        return s;
      }
      s.kpis.riskTrucks -= 1;
      s.kpis.pmQueue += 1;
      s.actionCount += 1;
      pushLog(s, '운영자 지시: 위험 차량 1대 PM Bay 투입', 'action');
      return s;
    }

    case 'DISPATCH_PRODUCTION': {
      const s = { ...state, kpis: { ...state.kpis }, effects: [...state.effects] };
      addEffect(s, 'demandFulfillment', 7, 180);
      addEffect(s, 'throughput', 10, 180);
      addEffect(s, 'fleetHI', -4, 300);
      s.actionCount += 1;
      pushLog(s, '운영자 지시: 긴급 증차 — 가동 우선 (처리량↑, 건전성↓)', 'action');
      return s;
    }

    case 'DISPATCH_RELIEVE': {
      const s = { ...state, kpis: { ...state.kpis }, effects: [...state.effects] };
      addEffect(s, 'costRate', -0.12, 220);
      addEffect(s, 'demandFulfillment', 3, 160);
      addEffect(s, 'throughput', 4, 200);
      s.actionCount += 1;
      pushLog(s, '운영자 지시: 경로 재배분 — 혼잡 완화 (비용↓, 흐름 개선)', 'action');
      return s;
    }

    case 'RESET':
      return createInitialState(action.id ?? state.activeHeuristic);

    default:
      return state;
  }
}
