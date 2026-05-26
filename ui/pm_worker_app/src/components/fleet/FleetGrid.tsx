import { getHIColor } from '../../utils/statusColors';
import type { Truck } from '../../policies/types';

interface FleetGridProps {
  trucks: Truck[];
  selectedTruckId: string;
  onSelectTruck: (id: string) => void;
}

export default function FleetGrid({ trucks, selectedTruckId, onSelectTruck }: FleetGridProps) {
  return (
    <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
      <h3 className="text-sm font-semibold text-text-main mb-2">Truck 현황</h3>
      <div className="grid grid-cols-5 gap-1.5">
        {trucks.map(truck => {
          const selected = truck.id === selectedTruckId;
          return (
            <button
              key={truck.id}
              onClick={() => onSelectTruck(truck.id)}
              className={`relative flex flex-col items-center justify-center py-1.5 rounded-lg text-[10px] transition-all ${
                selected
                  ? 'bg-sanguine text-white ring-2 ring-sanguine ring-offset-1'
                  : 'bg-gray-50 text-text-main hover:bg-gray-100'
              }`}
            >
              <span className="font-bold text-[11px]">{truck.id}</span>
              <span className={`font-semibold ${selected ? 'text-white/90' : ''}`} style={selected ? {} : { color: getHIColor(truck.healthIndex) }}>
                {truck.healthIndex}%
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
