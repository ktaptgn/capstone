import { policyList } from '../../policies/policyRegistry';
import type { PolicyId } from '../../policies/types';

interface PolicySelectorProps {
  selectedPolicy: PolicyId;
  onPolicyChange: (id: PolicyId) => void;
}

export default function PolicySelector({ selectedPolicy, onPolicyChange }: PolicySelectorProps) {
  return (
    <div className="px-4 py-2">
      <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
        {policyList.map(p => {
          const active = selectedPolicy === p.id;
          return (
            <button
              key={p.id}
              onClick={() => onPolicyChange(p.id)}
              className={`px-2.5 py-1 rounded-full text-[11px] font-medium whitespace-nowrap transition-all ${
                active
                  ? 'bg-sanguine text-white'
                  : 'bg-white text-text-sub border border-border hover:border-sanguine/40'
              }`}
            >
              {p.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}
