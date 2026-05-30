/**
 * Heuristic-based annual simulation data generator.
 * Produces 365 days of truck animation / HI / production / cost values
 * using deterministic pseudo-random seeded by day-of-year.
 */

function seededRandom(seed) {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

const FISCAL_YEAR_START = new Date('2025-07-01');
const TOTAL_TRUCKS = 25;
const BASE_DAILY_DEMAND = 100; // loads
const BASE_PM_COST = 12.4;    // M KRW
const BASE_TOTAL_COST = 38.6; // M KRW

/**
 * Generate simulation snapshot for a given date.
 * Returns { date, dayOfYear, trucks[], production, cost, fleetHI, ... }
 */
export function generateDaySnapshot(date) {
  const d = new Date(date);
  const dayOfYear = Math.floor((d - FISCAL_YEAR_START) / 86400000);
  const rand = seededRandom(dayOfYear * 31 + 7);

  // Seasonal adjustments (Chilean mine — summer = Dec-Feb, winter = Jun-Aug)
  const month = d.getMonth(); // 0-based
  const isSummer = month >= 10 || month <= 1; // Nov-Feb
  const isWinter = month >= 5 && month <= 7;  // Jun-Aug
  const heatFactor = isSummer ? 1.15 : isWinter ? 0.9 : 1.0;
  const coldStartFactor = isWinter ? 1.08 : 1.0;

  // Fleet HI trends: gradual degradation with periodic PM recovery (every ~30 days)
  const pmCycle = Math.sin((dayOfYear / 28) * Math.PI * 2) * 0.06;
  const degradation = Math.max(0, dayOfYear * 0.0003);
  const baseFleetHI = Math.max(0.55, 0.85 - degradation + pmCycle + (rand() - 0.5) * 0.04);

  // Per-truck HI with variation
  const trucks = [];
  let totalHI = 0;
  let trucksInPM = 0;
  let riskTrucks = 0;
  for (let i = 1; i <= TOTAL_TRUCKS; i++) {
    const truckRand = seededRandom(dayOfYear * 100 + i);
    const truckHI = Math.max(0.30, Math.min(1.0,
      baseFleetHI + (truckRand() - 0.5) * 0.2
    ));
    const isInPM = truckHI < 0.5 || (truckRand() < 0.12);
    const isRunning = !isInPM && truckHI > 0.35;
    const status = isInPM ? 'pm' : truckHI < 0.6 ? 'warning' : isRunning ? 'running' : 'standby';

    if (isInPM) trucksInPM++;
    if (truckHI < 0.6) riskTrucks++;
    totalHI += truckHI;

    trucks.push({
      id: `T${String(i).padStart(2, '0')}`,
      healthIndex: Math.round(truckHI * 100),
      status,
      speed: isRunning ? 18 + Math.round(truckRand() * 12) : 0,
    });
  }

  const avgFleetHI = totalHI / TOTAL_TRUCKS;
  const availableTrucks = TOTAL_TRUCKS - trucksInPM;

  // Production: proportional to available trucks × HI × heat adjustment
  const prodFactor = (availableTrucks / TOTAL_TRUCKS) * avgFleetHI * (1 / heatFactor);
  const completedLoads = Math.round(BASE_DAILY_DEMAND * prodFactor * (0.92 + rand() * 0.12));
  const demandFulfillment = Math.round((completedLoads / BASE_DAILY_DEMAND) * 100);

  // Costs: PM cost rises with more trucks in PM; total cost includes production penalties
  const pmCost = +(BASE_PM_COST * (1 + trucksInPM * 0.15) * coldStartFactor * (0.9 + rand() * 0.2)).toFixed(1);
  const totalCost = +(BASE_TOTAL_COST * (1 + (1 - prodFactor) * 0.3) * coldStartFactor * (0.92 + rand() * 0.16)).toFixed(1);

  return {
    date: `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`,
    dayOfYear,
    trucks,
    fleetHI: Math.round(avgFleetHI * 100),
    availableTrucks,
    trucksInPM,
    riskTrucks,
    completedLoads,
    dailyDemand: BASE_DAILY_DEMAND,
    demandFulfillment,
    pmCostMKRW: pmCost,
    totalCostMKRW: totalCost,
    temperature: isSummer ? 32 + Math.round(rand() * 8) : isWinter ? 5 + Math.round(rand() * 12) : 18 + Math.round(rand() * 10),
    shift: 'A',
  };
}

/**
 * Generate full fiscal year data (365 snapshots).
 */
export function generateAnnualData() {
  const snapshots = [];
  for (let i = 0; i < 365; i++) {
    const date = new Date(FISCAL_YEAR_START);
    date.setDate(date.getDate() + i);
    snapshots.push(generateDaySnapshot(date));
  }
  return snapshots;
}

/**
 * Format date for display: "2026.05.29"
 */
export function formatDate(d) {
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
}
