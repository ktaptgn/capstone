import { Bell, Thermometer, Moon, Sun } from 'lucide-react';

interface TopAppBarProps {
  unreadAlerts: number;
  onAlertClick: () => void;
  darkMode?: boolean;
  onDarkModeToggle?: () => void;
  versions?: string[];
  selectedVersion?: string;
  onVersionChange?: (v: string) => void;
}

export default function TopAppBar({
  unreadAlerts,
  onAlertClick,
  darkMode = false,
  onDarkModeToggle,
  versions = [],
  selectedVersion,
  onVersionChange,
}: TopAppBarProps) {
  return (
    <div className="bg-sanguine text-white px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div>
          <div className="text-xs opacity-80">근무조 A</div>
          <div className="text-sm font-semibold">2026.05.18</div>
        </div>
      </div>
      {versions.length > 0 && (
        <div className="flex items-center gap-0.5 bg-white/15 rounded-full p-0.5" title="결과 버전 선택">
          {versions.map(v => {
            const active = v === selectedVersion;
            return (
              <button
                key={v}
                onClick={() => onVersionChange && onVersionChange(v)}
                className={`px-2 py-0.5 rounded-full text-[10px] font-bold transition-colors ${
                  active ? 'bg-white text-sanguine' : 'text-white/80 hover:text-white'
                }`}
              >
                {v}
              </button>
            );
          })}
        </div>
      )}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1 text-sm">
          <Thermometer size={14} />
          <span>34°C</span>
        </div>
        {/* Dark mode toggle */}
        <button
          onClick={onDarkModeToggle}
          className="p-1.5 rounded-lg transition-colors hover:bg-white/20"
          title={darkMode ? '라이트 모드' : '다크 모드'}
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
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
