import { Bell, Thermometer } from 'lucide-react';

interface TopAppBarProps {
  unreadAlerts: number;
  onAlertClick: () => void;
}

export default function TopAppBar({ unreadAlerts, onAlertClick }: TopAppBarProps) {
  return (
    <div className="bg-sanguine text-white px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div>
          <div className="text-xs opacity-80">Shift A</div>
          <div className="text-sm font-semibold">2026.05.18</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1 text-sm">
          <Thermometer size={14} />
          <span>34°C</span>
        </div>
        <button onClick={onAlertClick} className="relative p-1">
          <Bell size={20} />
          {unreadAlerts > 0 && (
            <span className="absolute -top-1 -right-1 bg-critical text-white text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center">
              {unreadAlerts}
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
