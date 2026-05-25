import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Wrench, RefreshCw } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { dashboardApi } from '../services/dashboard';

export default function Recommendations() {
  const queryClient = useQueryClient();

  const { data: recommendations, isLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => dashboardApi.getRecommendations().then(r => r.data.data),
  });

  const generateMutation = useMutation({
    mutationFn: () => dashboardApi.generateRecommendations(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['recommendations'] }),
  });

  if (isLoading) return <LoadingSpinner />;

  const urgencyOrder = { immediate: 0, urgent: 1, high: 2, medium: 3, low: 4 };
  const sorted = [...(recommendations || [])].sort((a: any, b: any) =>
    (urgencyOrder[a.urgency as keyof typeof urgencyOrder] ?? 5) - (urgencyOrder[b.urgency as keyof typeof urgencyOrder] ?? 5)
  );

  return (
    <div>
      <PageHeader
        title="Maintenance Recommendations"
        subtitle={`${sorted.length} recommendations`}
        actions={
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw size={16} className={generateMutation.isPending ? 'animate-spin' : ''} />
            Generate
          </button>
        }
      />

      <div className="space-y-3">
        {sorted.map((rec: any) => (
          <div key={rec.recommendation_id} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${
                  rec.urgency === 'immediate' ? 'bg-red-50 text-red-500' :
                  rec.urgency === 'urgent' ? 'bg-orange-50 text-orange-500' :
                  rec.urgency === 'high' ? 'bg-yellow-50 text-yellow-500' :
                  'bg-blue-50 text-blue-500'
                }`}>
                  <Wrench size={18} />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <StatusBadge status={rec.urgency} />
                    <span className="text-xs text-gray-400">{rec.recommendation_type}</span>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{rec.description}</p>
                  <div className="flex gap-4 mt-2 text-xs text-gray-400">
                    {rec.estimated_cost && <span>Est. cost: ${rec.estimated_cost}</span>}
                    {rec.estimated_duration_hours && <span>Duration: {rec.estimated_duration_hours}h</span>}
                  </div>
                </div>
              </div>
              <StatusBadge status={rec.status} />
            </div>
          </div>
        ))}
        {sorted.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-8">No recommendations. Click "Generate" to scan components.</p>
        )}
      </div>
    </div>
  );
}
