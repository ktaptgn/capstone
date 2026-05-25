export const todayPM = [
  { time:"08:00", truckId:"T07", type:"Tire PM", status:"in-progress", duration:"2h" },
  { time:"10:30", truckId:"T15", type:"Inspection", status:"in-progress", duration:"1h 45m" },
  { time:"14:00", truckId:"T03", type:"Preventive PM", status:"standby", duration:"1h 30m" },
  { time:"16:30", truckId:"T12", type:"Tire Check", status:"standby", duration:"1h" },
  { time:"18:00", truckId:"T18", type:"Drive PM", status:"standby", duration:"1h 20m" },
];

export const pmHistory = {
  T07: [
    { date:"05/10", type:"Tire Inspection", result:"completed", duration:"1h 20m" },
    { date:"05/03", type:"Brake Check", result:"completed", duration:"50m" },
    { date:"04/25", type:"Full PM Service", result:"completed", duration:"3h" },
  ],
  T03: [
    { date:"05/08", type:"Preventive PM", result:"completed", duration:"1h 15m" },
    { date:"04/28", type:"Tire Inspection", result:"completed", duration:"1h" },
  ],
  T15: [
    { date:"05/05", type:"Full PM Service", result:"completed", duration:"2h 30m" },
    { date:"04/20", type:"Brake Check", result:"completed", duration:"50m" },
  ],
};
