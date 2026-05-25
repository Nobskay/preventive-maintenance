import { useQuery } from '@tanstack/react-query';
import {
  Cpu, AlertTriangle, Clock, Activity,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import KPICard from '../components/KPICard';
import HealthBar from '../components/HealthBar';
import StatusBadge from '../components/StatusBadge';
import AlertCard from '../components/AlertCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { dashboardApi } from '../services/dashboard';
import { alertsApi } from '../services/alerts';

const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#6b7280'];

export default function Dashboard() {
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => dashboardApi.getSummary().then(r => r.data.data),
  });

  const { data: healthData } = useQuery({
    queryKey: ['machine-health'],
    queryFn: () => dashboardApi.getMachineHealth().then(r => r.data.data),
  });

  const { data: trends } = useQuery({
    queryKey: ['downtime-trends'],
    queryFn: () => dashboardApi.getDowntimeTrends(30).then(r => r.data.data),
  });

  const { data: alerts } = useQuery({
    queryKey: ['active-alerts'],
    queryFn: () => alertsApi.list({ active_only: true, limit: 5 }).then(r => r.data.data),
  });

  if (loadingSummary) return <LoadingSpinner />;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Plant overview and maintenance status</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KPICard
          title="Total Machines"
          value={summary?.total_machines || 0}
          subtitle={`${summary?.active_machines || 0} active`}
          icon={Cpu}
          color="blue"
        />
        <KPICard
          title="Active Alerts"
          value={summary?.active_alerts || 0}
          subtitle={`${summary?.critical_alerts || 0} critical`}
          icon={AlertTriangle}
          color={summary?.critical_alerts ? 'red' : 'emerald'}
        />
        <KPICard
          title="Avg MTBF"
          value={`${summary?.avg_mtbf?.toFixed(0) || 0}h`}
          subtitle="Mean time between failures"
          icon={Clock}
          color="blue"
        />
        <KPICard
          title="Avg Availability"
          value={`${summary?.avg_availability?.toFixed(1) || 0}%`}
          subtitle="Machine uptime"
          icon={Activity}
          color="emerald"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Machine Health Table */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Machine Health</h3>
          <div className="space-y-4">
            {(healthData || []).map((machine: any) => (
              <div key={machine.machine_id} className="flex items-center gap-4">
                <div className="w-40 truncate">
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{machine.machine_name}</span>
                </div>
                <div className="flex-1">
                  <HealthBar percent={machine.overall_health_percent} status={machine.overall_health_status} />
                </div>
                <StatusBadge status={machine.overall_health_status} />
                <span className="text-xs text-gray-400 w-16 text-right">{machine.active_alerts} alerts</span>
              </div>
            ))}
          </div>
        </div>

        {/* Alert Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Alert Distribution</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: 'Critical', value: summary?.critical_alerts || 0 },
                    { name: 'Warning', value: summary?.warning_alerts || 0 },
                    { name: 'Other', value: (summary?.active_alerts || 0) - (summary?.critical_alerts || 0) - (summary?.warning_alerts || 0) },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  dataKey="value"
                >
                  {COLORS.map((color, i) => (
                    <Cell key={i} fill={color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-2">
            <span className="flex items-center gap-1 text-xs"><span className="w-2 h-2 rounded-full bg-red-500" />Critical</span>
            <span className="flex items-center gap-1 text-xs"><span className="w-2 h-2 rounded-full bg-yellow-500" />Warning</span>
          </div>
        </div>
      </div>

      {/* Downtime Trends & Recent Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Downtime Trends (30 days)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="total_downtime_hours" fill="#6b7280" name="Total" radius={[4, 4, 0, 0]} />
                <Bar dataKey="unplanned_downtime_hours" fill="#ef4444" name="Unplanned" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Alerts</h3>
          <div className="space-y-3 max-h-80 overflow-auto">
            {(alerts || []).map((alert: any) => (
              <AlertCard key={alert.alert_id} alert={alert} />
            ))}
            {(!alerts || alerts.length === 0) && (
              <p className="text-sm text-gray-500 text-center py-4">No active alerts</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
