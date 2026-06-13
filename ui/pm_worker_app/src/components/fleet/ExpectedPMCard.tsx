import { Clock, Wrench } from 'lucide-react';
import type { DerivedExpectedPM } from '../../policies/types';

interface ExpectedPMCardProps {
  expectedPM: DerivedExpectedPM;
}

export default function ExpectedPMCard({ expectedPM }: ExpectedPMCardProps) {
  return (
    <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
      <h3 className="text-sm font-semibold text-text-main mb-2 flex items-center gap-1.5">
        <Clock size={14} className="text-sanguine" />
        예상 PM
      </h3>
      <div className="space-y-1.5">
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-text-sub w-24">PM 예정:</span>
          <span className="text-xs font-semibold text-sanguine-dark">{expectedPM.expectedPmTime}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-text-sub w-24">예상 소요시간:</span>
          <span className="text-xs font-medium text-text-main">{expectedPM.estimatedDuration}</span>
        </div>
        <div className="flex items-start gap-2 mt-1">
          <Wrench size={12} className="text-text-sub mt-0.5 shrink-0" />
          <span className="text-[11px] text-text-sub">{expectedPM.reason}</span>
        </div>
        <div className="text-[9px] text-text-sub/60 mt-1">
          Policy 기준: {expectedPM.sourcePolicy}
        </div>
      </div>
    </div>
  );
}
