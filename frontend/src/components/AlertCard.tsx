import { AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react';
import StatusBadge from './StatusBadge';

interface AlertCardProps {
  alert: {
    alert_id: number;
    alert_type: string;
    alert_severity: string;
    message: string;
    created_at: string;
    is_active: boolean;
  };
  onResolve?: (id: number) => void;
}

const severityIcons = {
  critical: AlertTriangle,
  warning: AlertCircle,
  info: Info,
};

const severityColors = {
  critical: 'text-red-500 bg-red-50 dark:bg-red-900/20',
  warning: 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20',
  info: 'text-blue-500 bg-blue-50 dark:bg-blue-900/20',
};

export default function AlertCard({ alert, onResolve }: AlertCardProps) {
  const Icon = severityIcons[alert.alert_severity as keyof typeof severityIcons] || Info;
  const colorClass = severityColors[alert.alert_severity as keyof typeof severityColors] || severityColors.info;

  return (
    <div className={`rounded-lg p-4 border ${alert.is_active ? 'border-gray-200 dark:border-gray-700' : 'border-gray-100 dark:border-gray-800 opacity-60'}`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${colorClass}`}>
          <Icon size={18} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <StatusBadge status={alert.alert_severity} />
            <span className="text-xs text-gray-400">{alert.alert_type}</span>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300">{alert.message}</p>
          <p className="text-xs text-gray-400 mt-2">
            {new Date(alert.created_at).toLocaleString()}
          </p>
        </div>
        {alert.is_active && onResolve && (
          <button
            onClick={() => onResolve(alert.alert_id)}
            className="p-1.5 text-gray-400 hover:text-emerald-500 transition-colors"
            title="Resolve"
          >
            <CheckCircle size={18} />
          </button>
        )}
      </div>
    </div>
  );
}
