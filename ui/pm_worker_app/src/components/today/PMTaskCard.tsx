import { Clock, Play } from 'lucide-react';
import { getPriorityColor, getPriorityBg } from '../../utils/statusColors';
import type { DerivedPMTask } from '../../policies/types';

interface PMTaskCardProps {
  task: DerivedPMTask;
}

export default function PMTaskCard({ task }: PMTaskCardProps) {
  const priorityLabel = task.priority === 'in-progress' ? 'In Progress' : task.priority.charAt(0).toUpperCase() + task.priority.slice(1);

  return (
    <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold text-text-main">{task.truckId}</span>
          <span
            className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
            style={{
              color: getPriorityColor(task.priority),
              backgroundColor: getPriorityBg(task.priority),
            }}
          >
            {priorityLabel}
          </span>
        </div>
        {task.priority !== 'in-progress' && (
          <button className="w-7 h-7 rounded-full bg-sanguine flex items-center justify-center">
            <Play size={12} className="text-white ml-0.5" />
          </button>
        )}
      </div>
      <div className="flex items-center gap-3 text-[11px] text-text-sub">
        <div className="flex items-center gap-1">
          <Clock size={12} />
          <span>PM Due: {task.pmDue}</span>
        </div>
        <span>·</span>
        <span>Est. {task.estimatedDuration}</span>
      </div>
      <div className="mt-1.5 text-[11px] text-text-sub">{task.reason}</div>
    </div>
  );
}
