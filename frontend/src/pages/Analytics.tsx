import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend } from 'recharts';
import PageHeader from '../components/PageHeader';
import LoadingSpinner from '../components/LoadingSpinner';
import { dashboardApi } from '../services/dashboard';

export default function Analytics() {
  const { data: kpis, isLoading } = useQuery({
    queryKey: ['all-kpis'],
    queryFn: () => dashboardApi.getAllKPIs().then(r => r.data.data),
  });

  const { data: trends } = useQuery({
    queryKey: ['downtime-trends-90'],
    queryFn: () => dashboardApi.getDowntimeTrends(90).then(r => r.data.data),
  });

  if (isLoading) return <LoadingSpinner />;

  return (
    <div>
      <PageHeader title="Analytics" subtitle="Reliability metrics and trends" />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* MTBF by Machine */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">MTBF by Machine (hours)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={kpis || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="machine_name" tick={{ fontSize: 10 }} width={120} />
                <Tooltip />
                <Bar dataKey="mtbf_hours" fill="#10b981" name="MTBF (hours)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Availability */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Machine Availability (%)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={kpis || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="machine_name" tick={{ fontSize: 10 }} width={120} />
                <Tooltip />
                <Bar dataKey="availability_percent" fill="#3b82f6" name="Availability %" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Downtime Trends */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Downtime Trends (90 days)</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="total_downtime_hours" stroke="#6b7280" name="Total Downtime" strokeWidth={2} />
              <Line type="monotone" dataKey="unplanned_downtime_hours" stroke="#ef4444" name="Unplanned" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* KPI Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Machine KPI Summary</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Machine</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">MTBF</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">MTTR</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Availability</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Failures</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uptime</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Downtime</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {(kpis || []).map((kpi: any) => (
                <tr key={kpi.machine_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{kpi.machine_name}</td>
                  <td className="px-4 py-3 text-sm">{kpi.mtbf_hours ? `${kpi.mtbf_hours.toFixed(0)}h` : 'N/A'}</td>
                  <td className="px-4 py-3 text-sm">{kpi.mttr_hours ? `${kpi.mttr_hours.toFixed(1)}h` : 'N/A'}</td>
                  <td className="px-4 py-3 text-sm">
                    <span className={kpi.availability_percent >= 95 ? 'text-emerald-600' : kpi.availability_percent >= 85 ? 'text-yellow-600' : 'text-red-600'}>
                      {kpi.availability_percent?.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">{kpi.total_failures}</td>
                  <td className="px-4 py-3 text-sm">{kpi.total_uptime_hours?.toFixed(0)}h</td>
                  <td className="px-4 py-3 text-sm">{kpi.total_downtime_hours?.toFixed(0)}h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
