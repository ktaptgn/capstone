const logInput = document.querySelector("#logInput");
const playButton = document.querySelector("#playButton");
const pauseButton = document.querySelector("#pauseButton");
const frameSlider = document.querySelector("#frameSlider");
const truckLayer = document.querySelector("#truckLayer");
const policyLabel = document.querySelector("#policyLabel");
const dailyDemand = document.querySelector("#dailyDemand");
const completedLoads = document.querySelector("#completedLoads");
const fulfillment = document.querySelector("#fulfillment");
const availableTrucks = document.querySelector("#availableTrucks");
const pmCost = document.querySelector("#pmCost");

let records = [];
let frame = 0;
let timer = null;

const positions = {
  Yard: { left: 24, top: 75 },
  "PM Bay": { left: 22, top: 68 },
  "Crusher 1": { left: 78, top: 30 },
  "Crusher 2": { left: 74, top: 68 },
  Road: { left: 48, top: 48 },
};

function positionFor(record) {
  if (record.location in positions) return positions[record.location];
  if (record.destination in positions) return positions[record.destination];
  return positions.Road;
}

function stateClass(record) {
  return `state-${String(record.truck_state || "standby").toLowerCase()}`;
}

function renderFrame(index) {
  if (!records.length) return;
  frame = Math.max(0, Math.min(index, records.length - 1));
  const current = records[frame];
  const seen = new Map();

  for (let i = 0; i <= frame; i += 1) {
    seen.set(records[i].truck_id, records[i]);
  }

  truckLayer.innerHTML = "";
  Array.from(seen.values()).forEach((record, offset) => {
    const truck = document.createElement("div");
    const pos = positionFor(record);
    const pmDueClass = Number(record.pm_due_hours) <= 12 ? " pm-due" : "";
    truck.className = `truck ${stateClass(record)}${pmDueClass}`;
    truck.textContent = record.truck_id;
    truck.style.left = `calc(${pos.left}% + ${(offset % 3) * 18}px)`;
    truck.style.top = `calc(${pos.top}% + ${(offset % 2) * 14}px)`;
    truckLayer.appendChild(truck);
  });

  const demand = Number(current.daily_demand) || 0;
  const completed = Number(current.completed_loads) || 0;
  dailyDemand.textContent = demand.toFixed(0);
  completedLoads.textContent = completed.toFixed(0);
  fulfillment.textContent = demand ? `${Math.min(100, (completed / demand) * 100).toFixed(1)}%` : "100%";
  availableTrucks.textContent = Number(current.available_trucks || 0).toFixed(0);
  pmCost.textContent = Number(current.pm_cost || 0).toFixed(2);
  frameSlider.value = String(frame);
}

function play() {
  if (timer || records.length === 0) return;
  timer = window.setInterval(() => {
    if (frame >= records.length - 1) {
      pause();
      return;
    }
    renderFrame(frame + 1);
  }, 240);
}

function pause() {
  window.clearInterval(timer);
  timer = null;
}

logInput.addEventListener("change", async (event) => {
  pause();
  const file = event.target.files?.[0];
  if (!file) return;
  const payload = JSON.parse(await file.text());
  records = Array.isArray(payload) ? payload : payload.records || [];
  frameSlider.max = String(Math.max(records.length - 1, 0));
  frameSlider.value = "0";
  policyLabel.textContent = records.length
    ? `${payload.policy_id || records[0].policy_id} / seed ${payload.seed ?? "n/a"} / ${records.length} frames`
    : "No records found in log.";
  renderFrame(0);
});

frameSlider.addEventListener("input", (event) => {
  pause();
  renderFrame(Number(event.target.value));
});

playButton.addEventListener("click", play);
pauseButton.addEventListener("click", pause);
