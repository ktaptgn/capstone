import { Clock, Calendar, History, Loader } from 'lucide-react';
import type { WorkRecords } from '../../policies/types';

interface WorkRecordsScreenProps {
  workRecords: WorkRecords;
}

export default function WorkRecordsScreen({ workRecords }: WorkRecordsScreenProps) {
  const resultStyle = (result: string) => {
    if (result === 'completed') return 'bg-green-50 text-success';
    if (result === 'warning') return 'bg-yellow-50 text-warning';
    return 'bg-gray-50 text-text-sub';
  };

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

      {/* In Progress */}
      <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
        <h3 className="text-sm font-semibold text-text-main mb-2 flex items-center gap-1.5">
          <Loader size={14} className="text-pm-progress" />
          진행 중
        </h3>
        <div className="space-y-2">
          {workRecords.inProgress.map(item => (
            <div key={item.truckId} className="flex items-center justify-between bg-purple-50/50 rounded-lg p-2">
              <div>
                <div className="text-xs font-medium text-text-main">{item.truckId} — {item.pmType}</div>
                <div className="text-[10px] text-text-sub">시작 {item.startedAt} · 경과 {item.elapsed}</div>
              </div>
              <div className="w-12">
                <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-pm-progress rounded-full" style={{ width: `${item.progress}%` }} />
                </div>
                <div className="text-[9px] text-pm-progress text-right mt-0.5">{item.progress}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Planned Today */}
      <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
        <h3 className="text-sm font-semibold text-text-main mb-2 flex items-center gap-1.5">
          <Calendar size={14} className="text-sanguine" />
          오늘 예정
        </h3>
        <div className="space-y-2">
          {workRecords.plannedToday.map((item, i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                <Clock size={12} className="text-text-sub" />
                <span className="text-xs font-mono text-sanguine-dark w-10">{item.time}</span>
              </div>
              <span className="text-xs text-text-main font-medium">{item.truckId}</span>
              <span className="text-[11px] text-text-sub">{item.type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Last 7 Days */}
      <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
        <h3 className="text-sm font-semibold text-text-main mb-2 flex items-center gap-1.5">
          <History size={14} className="text-sanguine" />
          최근 7일
        </h3>
        <div className="space-y-2">
          {workRecords.last7Days.map(record => (
            <div key={record.id} className="flex items-center justify-between">
              <div>
                <div className="text-xs font-medium text-text-main">{record.truckId} — {record.type}</div>
                <div className="text-[10px] text-text-sub">{record.date} · {record.duration}</div>
                {record.note && <div className="text-[10px] text-warning">{record.note}</div>}
              </div>
              <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full capitalize ${resultStyle(record.result)}`}>
                {record.result === 'completed' ? '작업 완료' : record.result === 'warning' ? '주의' : record.result}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
