import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Activity, Clock, AlertTriangle } from 'lucide-react';
import KPICard from '../components/KPICard';
import StatusBadge from '../components/StatusBadge';
import HealthBar from '../components/HealthBar';
import LoadingSpinner from '../components/LoadingSpinner';
import { machinesApi } from '../services/machines';
import { dashboardApi } from '../services/dashboard';

export default function MachineDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const machineId = Number(id);

  const { data: machine, isLoading } = useQuery({
    queryKey: ['machine', machineId],
    queryFn: () => machinesApi.get(machineId).then(r => r.data.data),
    enabled: !!machineId,
  });

  const { data: health } = useQuery({
    queryKey: ['machine-health', machineId],
    queryFn: () => machinesApi.getHealth(machineId).then(r => r.data.data),
    enabled: !!machineId,
  });

  const { data: kpi } = useQuery({
    queryKey: ['machine-kpi', machineId],
    queryFn: () => dashboardApi.getMachineKPI(machineId).then(r => r.data.data),
    enabled: !!machineId,
  });

  if (isLoading) return <LoadingSpinner />;
  if (!machine) return <div>Machine not found</div>;

  return (
    <div>
      <button onClick={() => navigate('/machines')} className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4">
        <ArrowLeft size={16} /> Back to Machines
      </button>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{machine.machine_name}</h1>
          <p className="text-sm text-gray-500">{machine.machine_type} &middot; {machine.manufacturer}</p>
        </div>
        <StatusBadge status={machine.status} size="md" />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KPICard title="MTBF" value={kpi?.mtbf_hours ? `${kpi.mtbf_hours.toFixed(0)}h` : 'N/A'} icon={Clock} color="blue" />
        <KPICard title="MTTR" value={kpi?.mttr_hours ? `${kpi.mttr_hours.toFixed(1)}h` : 'N/A'} icon={Activity} color="yellow" />
        <KPICard title="Availability" value={`${kpi?.availability_percent?.toFixed(1) || 0}%`} icon={Activity} color="emerald" />
        <KPICard title="Failures" value={kpi?.total_failures || 0} subtitle="last 90 days" icon={AlertTriangle} color="red" />
      </div>

      {/* Components Health */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Component Health</h3>
        {(health?.components || []).length === 0 ? (
          <p className="text-sm text-gray-500">No components registered</p>
        ) : (
          <div className="space-y-4">
            {(health?.components || []).map((comp: any) => (
              <div key={comp.component_id} className="flex items-center gap-4 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                <div className="w-48">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{comp.component_name}</p>
                  <p className="text-xs text-gray-400">{comp.component_type}</p>
                </div>
                <div className="flex-1">
                  <HealthBar percent={comp.health_percent} status={comp.health_status} />
                  <p className="text-xs text-gray-400 mt-1">
                    {comp.life_consumed_percent?.toFixed(1)}% consumed · {comp.used_runtime_hours?.toFixed(0)}h since install
                  </p>
                </div>
                <div className="text-right w-32">
                  <StatusBadge status={comp.health_status} />
                  <div className="mt-1"><StatusBadge status={comp.maintenance_due_status} /></div>
                  {comp.remaining_useful_life_hours !== null && (
                    <p className="text-xs text-gray-400 mt-1">{comp.remaining_useful_life_hours.toFixed(0)}h remaining</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Machine Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Details</h3>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Type</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">{machine.machine_type}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Manufacturer</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">{machine.manufacturer}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Installed</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">{new Date(machine.installation_date).toLocaleDateString()}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Schedule</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white capitalize">{machine.operating_schedule}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">KPI Details</h3>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Total Uptime</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">{kpi?.total_uptime_hours?.toFixed(0) || 0}h</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Total Downtime</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">{kpi?.total_downtime_hours?.toFixed(0) || 0}h</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Failure Frequency</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">{kpi?.failure_frequency?.toFixed(2) || 0}/week</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}
