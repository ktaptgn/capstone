export const scenarioDefaults = {
  demandLevel: "Normal",
  pmBayCapacity: 2,
  roadRisk: "Normal",
  policy: "H3",
  shift: "Day"
};

export const scenarioBaseline = {
  demandFulfill: 84, pmCost: 12.4, downtime: 8, availTrucks: 18, riskTrucks: 1, totalCost: 38.6
};

export const scenarioResults = {
  "Low-H1": { demandFulfill:96, pmCost:10.2, downtime:6, availTrucks:22, riskTrucks:1, totalCost:28.4 },
  "Low-H2": { demandFulfill:88, pmCost:14.8, downtime:14, availTrucks:19, riskTrucks:0, totalCost:30.2 },
  "Low-H3": { demandFulfill:92, pmCost:8.6, downtime:5, availTrucks:21, riskTrucks:1, totalCost:24.8 },
  "Low-H4": { demandFulfill:94, pmCost:9.8, downtime:6, availTrucks:22, riskTrucks:1, totalCost:26.2 },
  "Normal-H1": { demandFulfill:92, pmCost:18.6, downtime:14, availTrucks:20, riskTrucks:3, totalCost:48.2 },
  "Normal-H2": { demandFulfill:76, pmCost:22.4, downtime:22, availTrucks:16, riskTrucks:0, totalCost:44.8 },
  "Normal-H3": { demandFulfill:84, pmCost:12.4, downtime:8, availTrucks:18, riskTrucks:1, totalCost:38.6 },
  "Normal-H4": { demandFulfill:88, pmCost:15.2, downtime:10, availTrucks:19, riskTrucks:2, totalCost:42.1 },
  "High-H1": { demandFulfill:78, pmCost:24.6, downtime:18, availTrucks:16, riskTrucks:5, totalCost:62.8 },
  "High-H2": { demandFulfill:64, pmCost:28.2, downtime:28, availTrucks:12, riskTrucks:0, totalCost:58.4 },
  "High-H3": { demandFulfill:72, pmCost:18.8, downtime:12, availTrucks:15, riskTrucks:3, totalCost:52.6 },
  "High-H4": { demandFulfill:76, pmCost:20.4, downtime:14, availTrucks:16, riskTrucks:4, totalCost:55.2 },
};

export const scenarioRecommendations = {
  Low: { policy:"H3", reason:"Low demand allows cost optimization — H3 minimizes total cost while meeting targets." },
  Normal: { policy:"H3", reason:"H3 provides the best balance of cost, PM coverage, and throughput under normal demand." },
  High: { policy:"H1", reason:"High demand requires maximum truck availability — H1 prioritizes throughput to meet targets." },
};
