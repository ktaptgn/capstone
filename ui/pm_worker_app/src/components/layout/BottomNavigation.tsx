import { ClipboardList, Truck, FileText, Bell } from 'lucide-react';

export type TabId = 'today' | 'fleet' | 'records' | 'alerts';

interface BottomNavigationProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

const tabs: { id: TabId; label: string; Icon: typeof ClipboardList }[] = [
  { id: 'today', label: 'Today PM', Icon: ClipboardList },
  { id: 'fleet', label: 'Fleet', Icon: Truck },
  { id: 'records', label: 'Records', Icon: FileText },
  { id: 'alerts', label: 'Alerts', Icon: Bell },
];

export default function BottomNavigation({ activeTab, onTabChange }: BottomNavigationProps) {
  return (
    <div className="bg-white border-t border-border flex items-center justify-around py-2">
      {tabs.map(({ id, label, Icon }) => {
        const active = activeTab === id;
        return (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={`flex flex-col items-center gap-0.5 px-3 py-1 transition-colors ${
              active ? 'text-sanguine' : 'text-text-sub'
            }`}
          >
            <Icon size={20} strokeWidth={active ? 2.5 : 1.5} />
            <span className={`text-[10px] ${active ? 'font-semibold' : ''}`}>{label}</span>
          </button>
        );
      })}
    </div>
  );
}
