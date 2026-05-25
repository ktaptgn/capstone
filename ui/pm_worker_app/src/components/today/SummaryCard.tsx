import { ClipboardList, Loader, AlertTriangle } from 'lucide-react';

interface SummaryCardProps {
  total: number;
  inProgress: number;
  critical: number;
}

export default function SummaryCard({ total, inProgress, critical }: SummaryCardProps) {
  return (
    <div className="mx-4 bg-white rounded-xl p-4 shadow-sm border border-border">
      <h2 className="text-sm font-semibold text-text-main mb-3">Today PM Summary</h2>
      <div className="flex justify-around">
        <div className="flex flex-col items-center gap-1">
          <div className="w-10 h-10 rounded-full bg-sanguine-soft flex items-center justify-center">
            <ClipboardList size={18} className="text-sanguine" />
          </div>
          <span className="text-lg font-bold text-text-main">{total}</span>
          <span className="text-[10px] text-text-sub">Today PM</span>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="w-10 h-10 rounded-full bg-purple-50 flex items-center justify-center">
            <Loader size={18} className="text-pm-progress" />
          </div>
          <span className="text-lg font-bold text-text-main">{inProgress}</span>
          <span className="text-[10px] text-text-sub">In Progress</span>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center">
            <AlertTriangle size={18} className="text-critical" />
          </div>
          <span className="text-lg font-bold text-text-main">{critical}</span>
          <span className="text-[10px] text-text-sub">Critical</span>
        </div>
      </div>
    </div>
  );
}
