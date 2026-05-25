import { AlertTriangle, CheckCircle, Info, AlertCircle } from 'lucide-react';
import type { AlertItem } from '../../policies/types';

interface AlertsScreenProps {
  alerts: AlertItem[];
}

function getAlertIcon(type: string) {
  switch (type) {
    case 'critical': return <AlertTriangle size={16} className="text-critical" />;
    case 'warning': return <AlertCircle size={16} className="text-warning" />;
    case 'completed': return <CheckCircle size={16} className="text-success" />;
    default: return <Info size={16} className="text-blue-500" />;
  }
}

function getAlertBorder(type: string) {
  switch (type) {
    case 'critical': return 'border-l-critical';
    case 'warning': return 'border-l-warning';
    case 'completed': return 'border-l-success';
    default: return 'border-l-blue-400';
  }
}

export default function AlertsScreen({ alerts }: AlertsScreenProps) {
  const sorted = [...alerts].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return (
    <div className="flex-1 overflow-y-auto pb-4 space-y-2 px-4">
      <h2 className="text-sm font-semibold text-text-main">Alerts</h2>
      {sorted.map(alert => (
        <div
          key={alert.id}
          className={`bg-white rounded-xl p-3 shadow-sm border border-border border-l-4 ${getAlertBorder(alert.type)} ${
            !alert.read ? '' : 'opacity-60'
          }`}
        >
          <div className="flex items-start gap-2">
            <div className="mt-0.5">{getAlertIcon(alert.type)}</div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-text-main">{alert.title}</span>
                {!alert.read && <span className="w-2 h-2 rounded-full bg-sanguine" />}
              </div>
              <p className="text-[11px] text-text-sub mt-1">{alert.message}</p>
              <span className="text-[9px] text-text-sub/60 mt-1 block">
                {new Date(alert.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
