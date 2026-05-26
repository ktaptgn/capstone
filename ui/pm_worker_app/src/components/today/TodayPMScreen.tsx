import SummaryCard from './SummaryCard';
import PMTaskCard from './PMTaskCard';
import RegularPMSchedule from './RegularPMSchedule';
import PolicySelector from './PolicySelector';
import type { DerivedPMTask, PolicyId, PMSchedule } from '../../policies/types';

interface TodayPMScreenProps {
  tasks: DerivedPMTask[];
  summary: PMSchedule['summary'];
  pmSchedule: PMSchedule;
  selectedPolicy: PolicyId;
  onPolicyChange: (id: PolicyId) => void;
}

export default function TodayPMScreen({ tasks, summary, pmSchedule, selectedPolicy, onPolicyChange }: TodayPMScreenProps) {
  const regularSchedule = pmSchedule.regularSchedule ?? pmSchedule.regularPMSchedule ?? [];

  return (
    <div className="flex-1 overflow-y-auto pb-4 space-y-3">
      <SummaryCard total={summary.total} inProgress={summary.inProgress} critical={summary.critical} />

      <PolicySelector selectedPolicy={selectedPolicy} onPolicyChange={onPolicyChange} />

      <div className="px-4 space-y-2.5">
        <h3 className="text-sm font-semibold text-text-main">우선순위 PM 대상</h3>
        {tasks.map(task => (
          <PMTaskCard key={task.truckId} task={task} />
        ))}
      </div>

      <div className="px-4 space-y-3">
        <RegularPMSchedule regularSchedule={regularSchedule} thisWeekPM={pmSchedule.thisWeekPM} />
      </div>
    </div>
  );
}
