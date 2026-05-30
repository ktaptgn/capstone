import { useMemo, useState } from 'react';
import { Clock, Calendar, History, Loader, ChevronDown, ChevronUp } from 'lucide-react';
import type { WorkRecords } from '../../policies/types';
import { getPMAlias } from '../../utils/pmAliases';

interface WorkRecordsScreenProps {
  workRecords: WorkRecords;
}

export default function WorkRecordsScreen({ workRecords }: WorkRecordsScreenProps) {
  const [expandedTruck, setExpandedTruck] = useState<string | null>(null);

  const resultStyle = (result: string) => {
    if (result === 'completed' || result === 'Completed') return 'bg-green-50 text-success';
    if (result === 'warning') return 'bg-yellow-50 text-warning';
    return 'bg-gray-50 text-text-sub';
  };

  const resultLabel = (result: string) => {
    if (result === 'completed' || result === 'Completed') return '완료';
    if (result === 'warning') return '주의';
    return result;
  };

  // Group planned today + in progress by truck (with deduplication)
  const todayByTruck = useMemo(() => {
    const map = new Map<string, {
      inProgress: WorkRecords['inProgress'];
      planned: WorkRecords['plannedToday'];
    }>();

    // Dedup in-progress: same truckId + pmType = duplicate
    const seenIP = new Set<string>();
    for (const item of workRecords.inProgress) {
      const key = `${item.truckId}::${item.pmType}`;
      if (seenIP.has(key)) continue;
      seenIP.add(key);
      const entry = map.get(item.truckId) || { inProgress: [], planned: [] };
      entry.inProgress.push(item);
      map.set(item.truckId, entry);
    }

    // Dedup planned: same truckId + type = duplicate
    const seenPlanned = new Set<string>();
    for (const item of workRecords.plannedToday) {
      const key = `${item.truckId}::${item.type}`;
      if (seenPlanned.has(key)) continue;
      seenPlanned.add(key);
      const entry = map.get(item.truckId) || { inProgress: [], planned: [] };
      entry.planned.push(item);
      map.set(item.truckId, entry);
    }

    return Array.from(map.entries()).sort((a, b) => a[0].localeCompare(b[0]));
  }, [workRecords.inProgress, workRecords.plannedToday]);

  const toggleTruck = (truckId: string) => {
    setExpandedTruck((prev) => (prev === truckId ? null : truckId));
  };

  const previousPM = workRecords.previousPMByTruck || {};

  return (
    <div className="flex-1 overflow-y-auto pb-4 space-y-3 px-4">
      {/* Summary */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-border">
        <h2 className="text-sm font-semibold text-text-main mb-3">Work Order 기록</h2>
        <div className="flex justify-around">
          <div className="flex flex-col items-center gap-1">
            <span className="text-lg font-bold text-text-main">{workRecords.summary.last7Days}</span>
            <span className="text-[10px] text-text-sub">최근 7일</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <span className="text-lg font-bold text-pm-progress">{workRecords.summary.inProgress}</span>
            <span className="text-[10px] text-text-sub">진행 중</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <span className="text-lg font-bold text-sanguine">{workRecords.summary.plannedToday}</span>
            <span className="text-[10px] text-text-sub">오늘 예정</span>
          </div>
        </div>
      </div>

      {/* 오늘 예정 — Grouped by truck */}
      <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
        <h3 className="text-sm font-semibold text-text-main mb-2 flex items-center gap-1.5">
          <Calendar size={14} className="text-sanguine" />
          오늘 예정 (트럭별)
        </h3>

        <div className="space-y-2">
          {todayByTruck.map(([truckId, data]) => {
            const isExpanded = expandedTruck === truckId;
            const truckHistory = previousPM[truckId] || [];
            const totalItems = data.inProgress.length + data.planned.length;

            return (
              <div key={truckId} className="border border-border rounded-lg overflow-hidden">
                {/* Truck header — tap to expand */}
                <button
                  onClick={() => toggleTruck(truckId)}
                  className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-sanguine">{truckId}</span>
                    <span className="text-[10px] text-text-sub">{totalItems}건</span>
                    {data.inProgress.length > 0 && (
                      <span className="text-[9px] font-bold text-pm-progress bg-purple-50 px-1.5 py-0.5 rounded-full">
                        진행 중 {data.inProgress.length}
                      </span>
                    )}
                  </div>
                  {isExpanded ? (
                    <ChevronUp size={14} className="text-text-sub" />
                  ) : (
                    <ChevronDown size={14} className="text-text-sub" />
                  )}
                </button>

                {/* Summary row (always visible) */}
                <div className="px-3 py-1.5">
                  {data.inProgress.map((item) => (
                    <div key={`ip-${item.truckId}-${item.pmType}`} className="flex items-center gap-2 py-0.5">
                      <Loader size={10} className="text-pm-progress animate-spin" />
                      <span className="text-[11px] font-medium text-text-main">
                        {getPMAlias(item.pmType)}
                      </span>
                      <span className="text-[10px] text-text-sub ml-auto">{item.progress}%</span>
                    </div>
                  ))}
                  {data.planned.map((item, i) => (
                    <div key={`pl-${truckId}-${i}`} className="flex items-center gap-2 py-0.5">
                      <Clock size={10} className="text-text-sub" />
                      <span className="text-[11px] font-medium text-text-main">
                        {getPMAlias(item.type)}
                      </span>
                      <span className="text-[10px] text-sanguine-dark font-mono ml-auto">{item.time}</span>
                    </div>
                  ))}
                </div>

                {/* Expanded: detail + past PM history */}
                {isExpanded && (
                  <div className="border-t border-border px-3 py-2 bg-white space-y-2">
                    {/* In-progress detail */}
                    {data.inProgress.map((item) => (
                      <div key={`det-${item.truckId}-${item.pmType}`} className="bg-purple-50/50 rounded-lg p-2">
                        <div className="text-xs font-medium text-text-main">
                          {getPMAlias(item.pmType)}
                        </div>
                        <div className="text-[10px] text-text-sub mt-0.5">
                          시작 {item.startedAt} · 경과 {item.elapsed}
                        </div>
                        <div className="mt-1.5">
                          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-pm-progress rounded-full"
                              style={{ width: `${item.progress}%` }}
                            />
                          </div>
                          <div className="text-[9px] text-pm-progress text-right mt-0.5">
                            {item.progress}%
                          </div>
                        </div>
                      </div>
                    ))}

                    {/* Planned detail */}
                    {data.planned.map((item, i) => (
                      <div key={`pdet-${truckId}-${i}`} className="flex items-center gap-3 py-1">
                        <Clock size={12} className="text-text-sub" />
                        <span className="text-xs font-mono text-sanguine-dark w-12">{item.time}</span>
                        <span className="text-[11px] text-text-main">{getPMAlias(item.type)}</span>
                      </div>
                    ))}

                    {/* Past PM history */}
                    {truckHistory.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-border">
                        <div className="text-[10px] font-semibold text-text-sub mb-1.5 flex items-center gap-1">
                          <History size={10} />
                          과거 PM 이력
                        </div>
                        {truckHistory.map((pm, i) => (
                          <div
                            key={`hist-${truckId}-${i}`}
                            className="flex items-center justify-between py-1"
                          >
                            <div>
                              <span className="text-[11px] text-text-main">{getPMAlias(pm.type)}</span>
                              <span className="text-[10px] text-text-sub ml-2">{pm.date}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] text-text-sub">{pm.duration}</span>
                              <span
                                className={`text-[9px] font-medium px-1.5 py-0.5 rounded-full ${resultStyle(pm.result)}`}
                              >
                                {resultLabel(pm.result)}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {todayByTruck.length === 0 && (
            <div className="text-center text-text-sub text-xs py-4">
              오늘 예정된 작업이 없습니다.
            </div>
          )}
        </div>
      </div>

      {/* Last 7 Days */}
      <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
        <h3 className="text-sm font-semibold text-text-main mb-2 flex items-center gap-1.5">
          <History size={14} className="text-sanguine" />
          최근 7일
        </h3>
        <div className="space-y-2">
          {workRecords.last7Days.map((record) => (
            <div key={record.id} className="flex items-center justify-between">
              <div>
                <div className="text-xs font-medium text-text-main">
                  {record.truckId} — {getPMAlias(record.type)}
                </div>
                <div className="text-[10px] text-text-sub">
                  {record.date} · {record.duration}
                </div>
                {record.note && (
                  <div className="text-[10px] text-warning">{record.note}</div>
                )}
              </div>
              <span
                className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${resultStyle(record.result)}`}
              >
                {resultLabel(record.result)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
