interface HealthBarProps {
  percent: number;
  status?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function HealthBar({ percent, status, showLabel = true, size = 'md' }: HealthBarProps) {
  const getColor = () => {
    if (status === 'CRITICAL' || percent >= 90) return 'bg-red-500';
    if (status === 'WARNING' || percent >= 80) return 'bg-yellow-500';
    return 'bg-emerald-500';
  };

  const heightClass = size === 'sm' ? 'h-1.5' : size === 'lg' ? 'h-4' : 'h-2.5';

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between mb-1">
          <span className="text-xs text-gray-500">Health</span>
          <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
            {percent.toFixed(1)}%
          </span>
        </div>
      )}
      <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full ${heightClass}`}>
        <div
          className={`${heightClass} rounded-full transition-all ${getColor()}`}
          style={{ width: `${Math.min(percent, 100)}%` }}
        />
      </div>
    </div>
  );
}
