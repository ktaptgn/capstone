import { History } from 'lucide-react';

interface PreviousPMCardProps {
  records: { date: string; type: string; result: string; duration: string }[];
}

export default function PreviousPMCard({ records }: PreviousPMCardProps) {
  return (
    <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
      <h3 className="text-sm font-semibold text-text-main mb-2 flex items-center gap-1.5">
        <History size={14} className="text-sanguine" />
        Previous PM
      </h3>
      {records.length === 0 ? (
        <p className="text-[11px] text-text-sub">No previous PM records</p>
      ) : (
        <div className="space-y-2">
          {records.map((r, i) => (
            <div key={i} className="flex items-center justify-between">
              <div>
                <div className="text-xs font-medium text-text-main">{r.type}</div>
                <div className="text-[10px] text-text-sub">{r.date} · {r.duration}</div>
              </div>
              <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                r.result === 'Completed' ? 'bg-green-50 text-success' : 'bg-yellow-50 text-warning'
              }`}>
                {r.result}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
