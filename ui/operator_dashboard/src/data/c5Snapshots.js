export async function loadJson(path) {
  try {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

export async function loadDashboardSnapshots() {
  const [policyComparison, sampleLog, workOrders] = await Promise.all([
    loadJson('/c5_1/policy_comparison.json'),
    loadJson('/c5_1/sample_log.json'),
    loadJson('/c5_1/work_orders.json'),
  ]);

  return { policyComparison, sampleLog, workOrders };
}

function average(values) {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + Number(value || 0), 0) / values.length;
}

export function mapPolicyComparison(rows, fallbackPolicies) {
  if (!Array.isArray(rows) || rows.length === 0) return fallbackPolicies;

  const byPolicy = rows.reduce((acc, row) => {
    acc[row.policy_id] = acc[row.policy_id] || [];
    acc[row.policy_id].push(row);
    return acc;
  }, {});

  const bestCost = Math.min(...Object.values(byPolicy).map(items => average(items.map(item => item.total_cost))));

  return Object.entries(byPolicy).map(([policyId, items], index) => {
    const fallback = fallbackPolicies.find(policy => policy.id === policyId) || fallbackPolicies[index] || {};
    const totalCost = average(items.map(item => item.total_cost));
    return {
      ...fallback,
      id: policyId,
      name: fallback.name || policyId,
      color: fallback.color || ['#8A4931', '#2563EB', '#7C3AED', '#16A34A', '#D97706'][index % 5],
      demandFulfill: Number((average(items.map(item => item.demand_fulfillment_rate)) * 100).toFixed(1)),
      pmCost: Number(average(items.map(item => item.pm_cost)).toFixed(2)),
      downtime: Number(average(items.map(item => item.avg_queue_time)).toFixed(2)),
      failures: Number(average(items.map(item => item.unmet_demand)).toFixed(0)),
      totalCost: Number(totalCost.toFixed(2)),
      completedLoads: Number(average(items.map(item => item.completed_loads)).toFixed(0)),
      unmetDemand: Number(average(items.map(item => item.unmet_demand)).toFixed(0)),
      active: totalCost === bestCost,
      planned: false,
      useCase: fallback.useCase || 'Official C5.1 policy sweep result',
      strength: fallback.strength || 'Generated from official C5.1 KPI summary',
      weakness: fallback.weakness || 'Interpret against scenario assumptions only',
    };
  });
}
