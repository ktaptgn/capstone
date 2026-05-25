export const dashboardKpis = {
  demandFulfillment: 84,
  completedLoads: 84,
  dailyDemand: 100,
  availableTrucks: 18,
  totalTrucks: 25,
  trucksInPM: 3,
  activePM: 2,
  queuedPM: 1,
  pmCostMKRW: 12.4,
  totalCostMKRW: 38.6,
  riskTrucks: 4,
  criticalTireCount: 2,
  currentPolicy: "H3",
  shift: "A",
  date: "2026.05.18",
  temperature: 34,
  alertCount: 3,
  demandTrend: {
    hours: ["06:00","07:00","08:00","09:00","10:00","11:00","12:00","13:00","14:00"],
    demand: [10,22,34,44,56,66,78,88,100],
    completed: [10,21,33,42,53,63,74,82,84]
  },
  truckStatusDistribution: { running: 14, standby: 4, pm: 3, warning: 2, critical: 2 },
  pmBayStatus: [
    { bay: "Bay 1", truckId: "T07", type: "Tire PM", remaining: "45 min", progress: 55 },
    { bay: "Bay 2", truckId: "T15", type: "Inspection", remaining: "20 min", progress: 70 }
  ],
  pmBayQueue: ["T03", "T12"]
};
