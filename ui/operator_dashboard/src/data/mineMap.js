export const facilities = [
  { id:"shovel_a", type:"shovel", name:"Shovel A", x:63, y:53, queue:1, status:"normal" },
  { id:"shovel_b", type:"shovel", name:"Shovel B", x:73, y:158, queue:0, status:"normal" },
  { id:"shovel_c", type:"shovel", name:"Shovel C", x:133, y:218, queue:3, status:"warning" },
  { id:"crusher_1", type:"crusher", name:"Crusher 1", x:504, y:202, queue:2, status:"normal" },
  { id:"crusher_2", type:"crusher", name:"Crusher 2", x:584, y:157, queue:0, status:"normal" },
  { id:"pm_bay", type:"pm_bay", name:"PM Bay", x:521, y:45, capacity:2, occupied:2, status:"in-progress" },
  { id:"standby", type:"standby", name:"Standby Area", x:385, y:229, queue:0, status:"standby" },
  { id:"dispatch", type:"dispatch", name:"Dispatch Zone", x:290, y:155, queue:0, status:"normal" },
];

export const routes = [
  { id:"main_road", riskLevel:"normal", path:"M60 95 C120 95, 150 150, 280 155 C380 160, 420 130, 540 115" },
  { id:"branch_shovel_a", riskLevel:"normal", path:"M100 95 L60 55" },
  { id:"branch_shovel_b", riskLevel:"normal", path:"M140 120 L80 155" },
  { id:"branch_shovel_c", riskLevel:"normal", path:"M200 155 L140 210" },
  { id:"branch_crusher_1", riskLevel:"normal", path:"M460 145 L500 195" },
  { id:"branch_crusher_2", riskLevel:"normal", path:"M520 120 L580 155" },
  { id:"branch_pm_bay", riskLevel:"normal", path:"M480 115 L520 55" },
  { id:"high_risk_segment", riskLevel:"high", path:"M380 157 C420 140, 450 130, 480 120" },
];

export const truckMarkers = [
  { truckId:"T01", x:180, y:155, status:"running" },
  { truckId:"T02", x:260, y:120, status:"running" },
  { truckId:"T05", x:350, y:180, status:"running" },
  { truckId:"T09", x:420, y:140, status:"running" },
  { truckId:"T13", x:490, y:195, status:"running" },
  { truckId:"T03", x:145, y:100, status:"warning" },
  { truckId:"T07", x:520, y:60, status:"critical" },
  { truckId:"T12", x:540, y:80, status:"standby" },
  { truckId:"T15", x:500, y:45, status:"in-progress" },
];
