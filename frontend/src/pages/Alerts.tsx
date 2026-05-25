import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RefreshCw } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import AlertCard from '../components/AlertCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { alertsApi } from '../services/alerts';

export default function Alerts() {
  const queryClient = useQueryClient();

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsApi.list({}).then(r => r.data.data),
  });

  const resolveMutation = useMutation({
    mutationFn: (id: number) => alertsApi.resolve(id, { resolution_notes: 'Resolved from UI' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  });

  const generateMutation = useMutation({
    mutationFn: () => alertsApi.generate(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  });

  if (isLoading) return <LoadingSpinner />;

  const activeAlerts = (alerts || []).filter((a: any) => a.is_active);
  const resolvedAlerts = (alerts || []).filter((a: any) => !a.is_active);

  return (
    <div>
      <PageHeader
        title="Alerts"
        subtitle={`${activeAlerts.length} active alerts`}
        actions={
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw size={16} className={generateMutation.isPending ? 'animate-spin' : ''} />
            Scan & Generate
          </button>
        }
      />

      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Active ({activeAlerts.length})</h3>
          {activeAlerts.length === 0 ? (
            <p className="text-sm text-gray-500 py-4">No active alerts</p>
          ) : (
            <div className="space-y-3">
              {activeAlerts.map((alert: any) => (
                <AlertCard key={alert.alert_id} alert={alert} onResolve={resolveMutation.mutate} />
              ))}
            </div>
          )}
        </div>

        {resolvedAlerts.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Resolved ({resolvedAlerts.length})</h3>
            <div className="space-y-3">
              {resolvedAlerts.map((alert: any) => (
                <AlertCard key={alert.alert_id} alert={alert} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
