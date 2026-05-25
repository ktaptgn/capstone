export const alerts = [
  { id:"ALT001", message:"T07 front-left tire HI at 32% — Critical", status:"critical", timestamp:"8m ago" },
  { id:"ALT002", message:"Crusher 1 queue increasing (wait: 12 min)", status:"warning", timestamp:"2m ago" },
  { id:"ALT003", message:"PM Bay 1 occupied for 45 min (T07 tire PM)", status:"in-progress", timestamp:"5m ago" },
  { id:"ALT004", message:"T03 HI dropped below 60% threshold", status:"warning", timestamp:"15m ago" },
];

export const recommendedActions = [
  { id:1, text:"Send T07 to PM Bay — Tire HI critical (32%)", status:"critical" },
  { id:2, text:"Keep T03 running until 14:00 — PM at scheduled time", status:"warning" },
  { id:3, text:"Hold T12 in standby for PM queue smoothing", status:"standby" },
];
