export const policies = [
  { id:"H1", name:"Production / Bottleneck", demandFulfill:92, pmCost:18.6, downtime:14, failures:3, totalCost:48.2, strength:"Highest throughput stability", weakness:"Higher failure risk", color:"#2563EB", active:false, planned:false, useCase:"High demand / throughput priority" },
  { id:"H2", name:"Reliability / PM", demandFulfill:76, pmCost:22.4, downtime:22, failures:0, totalCost:44.8, strength:"Lowest failure risk", weakness:"Higher PM downtime", color:"#7C3AED", active:false, planned:false, useCase:"High failure risk environment" },
  { id:"H3", name:"Cost-weighted", demandFulfill:84, pmCost:12.4, downtime:8, failures:1, totalCost:38.6, strength:"Best total cost balance", weakness:"Moderate on all individual metrics", color:"#8A4931", active:true, planned:false, useCase:"Normal demand / balanced cost" },
  { id:"H4", name:"Adaptive Network Flow", demandFulfill:88, pmCost:15.2, downtime:10, failures:2, totalCost:42.1, strength:"Best queue/congestion reduction", weakness:"Complex parameter tuning", color:"#0891B2", active:false, planned:false, useCase:"Congested routes / queue issues" },
];
