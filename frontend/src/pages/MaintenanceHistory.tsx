import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Search } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import MaintenanceEventForm from '../components/MaintenanceEventForm';
import { maintenanceApi } from '../services/maintenance';
import { MaintenanceEvent } from '../types';

export default function MaintenanceHistory() {
  const [search, setSearch] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<MaintenanceEvent | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: events, isLoading } = useQuery({
    queryKey: ['maintenance-events'],
    queryFn: () => maintenanceApi.list({ limit: 500 }).then(r => r.data.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => maintenanceApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-events'] });
      setShowCreate(false);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Failed to create maintenance event';
      setFormError(typeof message === 'string' ? message : JSON.stringify(message));
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => maintenanceApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-events'] });
      setEditing(null);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Failed to update maintenance event';
      setFormError(typeof message === 'string' ? message : JSON.stringify(message));
    },
  });

  const filtered = (events || []).filter((event: MaintenanceEvent) =>
    event.action_taken.toLowerCase().includes(search.toLowerCase()) ||
    event.work_order_code?.toLowerCase().includes(search.toLowerCase()) ||
    event.technician?.toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: 'work_order_code',
      header: 'Work Order',
      render: (event: MaintenanceEvent) => (
        <div>
          <span className="font-medium text-gray-900 dark:text-white">{event.work_order_code || `EV-${event.maintenance_event_id}`}</span>
          <p className="text-xs text-gray-400">Machine #{event.machine_id}</p>
        </div>
      ),
    },
    { key: 'event_type', header: 'Type', render: (event: MaintenanceEvent) => <StatusBadge status={event.event_type} /> },
    { key: 'trigger_source', header: 'Trigger' },
    {
      key: 'performed_at',
      header: 'Performed',
      render: (event: MaintenanceEvent) => new Date(event.performed_at).toLocaleString(),
    },
    {
      key: 'action_taken',
      header: 'Action',
      render: (event: MaintenanceEvent) => <span className="text-sm max-w-md truncate block">{event.action_taken}</span>,
    },
    { key: 'technician', header: 'Technician' },
    {
      key: 'duration_hours',
      header: 'Duration',
      render: (event: MaintenanceEvent) => event.duration_hours ? `${event.duration_hours}h` : '--',
    },
    {
      key: 'actions',
      header: '',
      render: (event: MaintenanceEvent) => (
        <button
          onClick={(clickEvent) => { clickEvent.stopPropagation(); setEditing(event); setFormError(null); }}
          className="text-xs text-blue-500 hover:text-blue-700"
        >
          Edit
        </button>
      ),
    },
  ];

  if (isLoading) return <LoadingSpinner />;

  return (
    <div>
      <PageHeader
        title="Maintenance History"
        subtitle={`${filtered.length} completed work records`}
        actions={
          <button
            onClick={() => { setShowCreate(true); setFormError(null); }}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <Plus size={16} />
            Add Event
          </button>
        }
      />

      <div className="relative mb-4">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Search maintenance work orders..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="w-full pl-9 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
        />
      </div>

      <DataTable columns={columns} data={filtered} emptyMessage="No maintenance history found." />

      <Modal isOpen={showCreate} onClose={() => { setShowCreate(false); setFormError(null); }} title="Add Maintenance Event">
        <MaintenanceEventForm
          onSubmit={(data) => createMutation.mutate(data)}
          onCancel={() => { setShowCreate(false); setFormError(null); }}
          isLoading={createMutation.isPending}
          error={formError}
        />
      </Modal>

      <Modal isOpen={!!editing} onClose={() => { setEditing(null); setFormError(null); }} title="Edit Maintenance Event">
        {editing && (
          <MaintenanceEventForm
            event={editing}
            onSubmit={(data) => updateMutation.mutate({ id: editing.maintenance_event_id, data })}
            onCancel={() => { setEditing(null); setFormError(null); }}
            isLoading={updateMutation.isPending}
            error={formError}
          />
        )}
      </Modal>
    </div>
  );
}
