export const priorityActions = [
  {
    rank: 1,
    action: "Send T07 to PM Bay",
    actionKr: "T07을 PM Bay로 이동",
    reason: "Front Left Tire HI 32%, PM Due Now",
    reasonKr: "Front Left Tire HI: 32%, PM Due: Now",
    risk: "tire-related downtime",
    riskKr: "타이어 관련 downtime 위험이 큼",
  },
  {
    rank: 2,
    action: "Check Crusher 1 queue",
    actionKr: "Crusher 1 queue 확인",
    reason: "Current Queue 2",
    reasonKr: "현재 Queue: 2",
    risk: "hauling bottleneck",
    riskKr: "운반 병목 가능성 있음",
  },
  {
    rank: 3,
    action: "Keep T03 PM at 14:00",
    actionKr: "T03 PM 시점 유지",
    reason: "PM queue smoothing",
    reasonKr: "Today 14:00 예정",
    risk: "additional PM Bay congestion",
    riskKr: "PM Bay 대기열을 완화하기 위한 조치",
  },
];
