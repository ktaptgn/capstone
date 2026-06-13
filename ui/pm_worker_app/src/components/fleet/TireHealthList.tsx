import { getHIColor, getStatusBg } from '../../utils/statusColors';
import type { TireComponent } from '../../policies/types';

interface TireHealthListProps {
  tires: TireComponent[];
}

export default function TireHealthList({ tires }: TireHealthListProps) {
  return (
    <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
      <h3 className="text-sm font-semibold text-text-main mb-2">Tire Health Index</h3>
      <div className="space-y-2">
        {tires.map(tire => (
          <div key={tire.id} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
                style={{ backgroundColor: getHIColor(tire.healthIndex) }}
              >
                {tire.position}
              </div>
              <div>
                <div className="text-xs font-medium text-text-main">{tire.name}</div>
                <div className="text-[10px] text-text-sub">{tire.healthIndex}%</div>
              </div>
            </div>
            <span
              className="text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize"
              style={{
                color: getHIColor(tire.healthIndex),
                backgroundColor: getStatusBg(tire.status),
              }}
            >
              {tire.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
