import { Calendar, RotateCcw } from 'lucide-react';
import type { RegularScheduleItem, ThisWeekPMDay } from '../../policies/types';

interface RegularPMScheduleProps {
  regularSchedule: RegularScheduleItem[];
  thisWeekPM: ThisWeekPMDay[];
}

export default function RegularPMSchedule({ regularSchedule, thisWeekPM }: RegularPMScheduleProps) {
  return (
    <>
      <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
        <h3 className="text-sm font-semibold text-text-main mb-3 flex items-center gap-1.5">
          <Calendar size={14} className="text-sanguine" />
          This Week PM
        </h3>
        <div className="flex justify-between">
          {thisWeekPM.map(day => (
            <div key={day.day} className="flex flex-col items-center gap-1">
              <span className={`text-[10px] font-medium ${day.isToday ? 'text-sanguine' : 'text-text-sub'}`}>
                {day.day}
              </span>
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold ${
                  day.isToday
                    ? 'bg-sanguine text-white'
                    : day.trucks.length > 0
                    ? 'bg-sanguine-soft text-sanguine'
                    : 'bg-gray-50 text-text-sub'
                }`}
              >
                {day.trucks.length || '-'}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
        <h3 className="text-sm font-semibold text-text-main mb-3 flex items-center gap-1.5">
          <RotateCcw size={14} className="text-sanguine" />
          Regular PM Schedule
        </h3>
        <div className="space-y-2.5">
          {regularSchedule.map(item => (
            <div key={item.label} className="flex items-center justify-between">
              <div>
                <div className="text-xs font-medium text-text-main">{item.label}</div>
                <div className="text-[10px] text-text-sub">{item.cycle} · {item.next}</div>
              </div>
              <span className="text-[10px] text-text-sub bg-gray-50 px-2 py-0.5 rounded-full">{item.truckCount}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
