import { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import SummaryCard from './SummaryCard';
import PMTaskCard from './PMTaskCard';
import RegularPMSchedule from './RegularPMSchedule';
import PolicySelector from './PolicySelector';
import ExceptionalPMOrders from './ExceptionalPMOrders';
import type { DerivedPMTask, PolicyId, PMSchedule } from '../../policies/types';

const PAGE_SIZE = 10;

interface TodayPMScreenProps {
  tasks: DerivedPMTask[];
  summary: PMSchedule['summary'];
  pmSchedule: PMSchedule;
  selectedPolicy: PolicyId;
  onPolicyChange: (id: PolicyId) => void;
}

export default function TodayPMScreen({ tasks, summary, pmSchedule, selectedPolicy, onPolicyChange }: TodayPMScreenProps) {
  const regularSchedule = pmSchedule.regularSchedule ?? pmSchedule.regularPMSchedule ?? [];
  const [page, setPage] = useState(0);

  // Deduplicate tasks: same truckId + reason = duplicate → keep first occurrence only
  const uniqueTasks = useMemo(() => {
    const seen = new Set<string>();
    return tasks.filter(task => {
      const key = `${task.truckId}::${task.reason}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [tasks]);

  // Group tasks by truck
  const groupedTasks = useMemo(() => {
    const map = new Map<string, DerivedPMTask[]>();
    for (const task of uniqueTasks) {
      const group = map.get(task.truckId) || [];
      group.push(task);
      map.set(task.truckId, group);
    }
    return Array.from(map.entries()); // [truckId, tasks[]]
  }, [uniqueTasks]);

  // Flatten grouped entries for pagination (each entry = one task)
  const flatEntries = useMemo(() => {
    const result: { truckId: string; task: DerivedPMTask; isGroupHeader: boolean }[] = [];
    for (const [truckId, truckTasks] of groupedTasks) {
      truckTasks.forEach((task, idx) => {
        result.push({ truckId, task, isGroupHeader: idx === 0 });
      });
    }
    return result;
  }, [groupedTasks]);

  const totalPages = Math.max(1, Math.ceil(flatEntries.length / PAGE_SIZE));
  const pageEntries = flatEntries.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  // Group page entries by truck for display
  const pageGroups = useMemo(() => {
    const map = new Map<string, DerivedPMTask[]>();
    for (const entry of pageEntries) {
      const group = map.get(entry.truckId) || [];
      group.push(entry.task);
      map.set(entry.truckId, group);
    }
    return Array.from(map.entries());
  }, [pageEntries]);

  return (
    <div className="flex-1 overflow-y-auto pb-4 space-y-3">
      <SummaryCard total={summary.total} inProgress={summary.inProgress} critical={summary.critical} />

      <PolicySelector selectedPolicy={selectedPolicy} onPolicyChange={onPolicyChange} />

      {/* Exceptional PM Orders (approval/hold/reject) */}
      <ExceptionalPMOrders />

      {/* Priority PM tasks grouped by truck */}
      <div className="px-4 space-y-3">
        <h3 className="text-sm font-semibold text-text-main">우선순위 PM 대상</h3>

        {pageGroups.map(([truckId, truckTasks]) => (
          <div key={truckId} className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-sanguine bg-sanguine/10 px-2 py-0.5 rounded-md">
                {truckId}
              </span>
              <span className="text-[10px] text-text-sub">{truckTasks.length}건</span>
            </div>
            {truckTasks.map((task, idx) => (
              <PMTaskCard key={`${task.truckId}-${idx}`} task={task} />
            ))}
          </div>
        ))}

        {flatEntries.length === 0 && (
          <div className="text-center text-text-sub text-xs py-6">
            현재 PM 대상 장비가 없습니다.
          </div>
        )}
      </div>

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-1">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="p-1.5 rounded-lg border border-border text-text-sub disabled:opacity-30 hover:bg-gray-50 transition-colors"
          >
            <ChevronLeft size={16} />
          </button>
          <span className="text-xs text-text-sub font-medium">
            {page + 1} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page === totalPages - 1}
            className="p-1.5 rounded-lg border border-border text-text-sub disabled:opacity-30 hover:bg-gray-50 transition-colors"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      )}

      <div className="px-4 space-y-3">
        <RegularPMSchedule regularSchedule={regularSchedule} thisWeekPM={pmSchedule.thisWeekPM} />
      </div>
    </div>
  );
}
