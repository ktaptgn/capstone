import { PolicyId } from './types';

export interface PolicyOption {
  id: PolicyId;
  name: string;
  description: string;
}

export const policyList: PolicyOption[] = [
  {
    id: 'baseline',
    name: 'Baseline',
    description: 'Display label for baseline work orders from official snapshots.',
  },
  {
    id: 'h1_production_bottleneck',
    name: 'H1 Bottleneck',
    description: 'Display label for H1 work orders from official snapshots.',
  },
  {
    id: 'h2_reliability_pm',
    name: 'H2 PM Risk',
    description: 'Display label for H2 work orders from official snapshots.',
  },
  {
    id: 'h3_cost_weighted',
    name: 'H3 Cost',
    description: 'Display label for H3 work orders from official snapshots.',
  },
  {
    id: 'h4_network_flow',
    name: 'H4 Flow',
    description: 'Display label for H4 work orders from official snapshots.',
  },
];
