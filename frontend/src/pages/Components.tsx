import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import DataTable from '../components/DataTable';
import HealthBar from '../components/HealthBar';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import ComponentForm from '../components/ComponentForm';
import { componentsApi } from '../services/components';
import { Component } from '../types';

export default function Components() {
  const [search, setSearch] = useState('');
  const [machineFilter] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<Component | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: components, isLoading } = useQuery({
    queryKey: ['components', machineFilter],
    queryFn: () => componentsApi.list({ machine_id: machineFilter ? Number(machineFilter) : undefined }).then(r => r.data.data),
  });

  const { data: healthData } = useQuery({
    queryKey: ['components-health', components],
    queryFn: async () => {
      if (!components) return {};
      const results: Record<number, any> = {};
      await Promise.all(
        components.map(async (c: Component) => {
          try {
            const res = await componentsApi.getHealth(c.component_id);
            results[c.component_id] = res.data.data;
          } catch {
            results[c.component_id] = null;
          }
        })
      );
      return results;
    },
    enabled: !!components && components.length > 0,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => componentsApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['components'] }),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => componentsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['components'] });
      setShowCreate(false);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Failed to create component';
      setFormError(typeof message === 'string' ? message : JSON.stringify(message));
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => componentsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['components'] });
      setEditing(null);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Failed to update component';
      setFormError(typeof message === 'string' ? message : JSON.stringify(message));
    },
  });

  const filtered = (components || []).filter((c: Component) =>
    c.component_name.toLowerCase().includes(search.toLowerCase()) ||
    c.component_type.toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: 'component_name',
      header: 'Component',
      render: (c: Component) => (
        <div>
          <span className="font-medium text-gray-900 dark:text-white">{c.component_name}</span>
          <p className="text-xs text-gray-400">Machine #{c.machine_id}</p>
        </div>
      ),
    },
    { key: 'component_type', header: 'Type' },
    {
      key: 'health',
      header: 'Health',
      render: (c: Component) => {
        const health = healthData?.[c.component_id];
        if (!health) return <span className="text-gray-400">--</span>;
        return (
          <div className="w-40">
            <HealthBar percent={health.health_percent} status={health.health_status} />
            <p className="text-xs text-gray-400 mt-1">{health.life_consumed_percent?.toFixed(1)}% life consumed</p>
          </div>
        );
      },
    },
    {
      key: 'health_status',
      header: 'Status',
      render: (c: Component) => {
        const health = healthData?.[c.component_id];
        return health ? <StatusBadge status={health.health_status} /> : <span className="text-gray-400">--</span>;
      },
    },
    {
      key: 'lifetime',
      header: 'Lifetime',
      render: (c: Component) => (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {c.lifetime_hours ? `${c.lifetime_hours}h` : ''} {c.lifetime_months ? `/${c.lifetime_months}mo` : ''}
        </span>
      ),
    },
    {
      key: 'sop',
      header: 'SOP',
      render: (c: Component) => <span className="text-xs text-gray-500 max-w-xs truncate block">{c.maintenance_sop || '--'}</span>,
    },
    {
      key: 'replacement_cost',
      header: 'Cost',
      render: (c: Component) => c.replacement_cost ? `$${c.replacement_cost}` : '--',
    },
    {
      key: 'actions',
      header: '',
      render: (c: Component) => (
        <div className="flex gap-3">
          <button
            onClick={(e) => { e.stopPropagation(); setEditing(c); setFormError(null); }}
            className="text-xs text-blue-500 hover:text-blue-700"
          >
            Edit
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(c.component_id); }}
            className="text-xs text-red-500 hover:text-red-700"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  if (isLoading) return <LoadingSpinner />;

  return (
    <div>
      <PageHeader
        title="Components"
        subtitle={`${filtered.length} components tracked`}
        actions={
          <button
            onClick={() => { setShowCreate(true); setFormError(null); }}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <Plus size={16} />
            Add Component
          </button>
        }
      />

      <div className="flex gap-3 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search components..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          />
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filtered}
        emptyMessage="No components found."
      />

      <Modal isOpen={showCreate} onClose={() => { setShowCreate(false); setFormError(null); }} title="Add Component">
        <ComponentForm
          onSubmit={(data) => createMutation.mutate(data)}
          onCancel={() => { setShowCreate(false); setFormError(null); }}
          isLoading={createMutation.isPending}
          error={formError}
        />
      </Modal>

      <Modal isOpen={!!editing} onClose={() => { setEditing(null); setFormError(null); }} title="Edit Component">
        {editing && (
          <ComponentForm
            component={editing}
            onSubmit={(data) => updateMutation.mutate({ id: editing.component_id, data })}
            onCancel={() => { setEditing(null); setFormError(null); }}
            isLoading={updateMutation.isPending}
            error={formError}
          />
        )}
      </Modal>
    </div>
  );
}
