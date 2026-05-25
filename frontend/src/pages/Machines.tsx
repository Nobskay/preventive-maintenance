import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import DataTable from '../components/DataTable';
import StatusBadge from '../components/StatusBadge';
import Modal from '../components/Modal';
import MachineForm from '../components/MachineForm';
import LoadingSpinner from '../components/LoadingSpinner';
import { machinesApi } from '../services/machines';
import { Machine, MachineCreate } from '../types';

export default function Machines() {
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<Machine | null>(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data: machines, isLoading } = useQuery({
    queryKey: ['machines', statusFilter],
    queryFn: () => machinesApi.list({ status: statusFilter || undefined }).then(r => r.data.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: MachineCreate) => machinesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
      setShowCreate(false);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Failed to create machine';
      setFormError(typeof message === 'string' ? message : JSON.stringify(message));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => machinesApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['machines'] }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: MachineCreate }) => machinesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
      setEditing(null);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Failed to update machine';
      setFormError(typeof message === 'string' ? message : JSON.stringify(message));
    },
  });

  const filtered = (machines || []).filter((m: Machine) =>
    m.machine_name.toLowerCase().includes(search.toLowerCase()) ||
    m.machine_type.toLowerCase().includes(search.toLowerCase()) ||
    m.manufacturer?.toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: 'machine_name',
      header: 'Machine',
      render: (m: Machine) => (
        <div>
          <span className="font-medium text-gray-900 dark:text-white">{m.machine_name}</span>
          <p className="text-xs text-gray-400">{m.manufacturer}</p>
        </div>
      ),
    },
    { key: 'machine_type', header: 'Type' },
    {
      key: 'status',
      header: 'Status',
      render: (m: Machine) => <StatusBadge status={m.status} />,
    },
    { key: 'operating_schedule', header: 'Schedule' },
    {
      key: 'installation_date',
      header: 'Installed',
      render: (m: Machine) => new Date(m.installation_date).toLocaleDateString(),
    },
    {
      key: 'actions',
      header: '',
      render: (m: Machine) => (
        <div className="flex gap-3">
          <button
            onClick={(e) => { e.stopPropagation(); setEditing(m); setFormError(null); }}
            className="text-xs text-blue-500 hover:text-blue-700"
          >
            Edit
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(m.machine_id); }}
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
        title="Machines"
        subtitle={`${filtered.length} machines registered`}
        actions={
          <button
            onClick={() => { setShowCreate(true); setFormError(null); }}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <Plus size={16} />
            Add Machine
          </button>
        }
      />

      <div className="flex gap-3 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search machines..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="idle">Idle</option>
          <option value="maintenance">Maintenance</option>
        </select>
      </div>

      <DataTable
        columns={columns}
        data={filtered}
        onRowClick={(m) => navigate(`/machines/${m.machine_id}`)}
        emptyMessage="No machines found. Add your first machine to get started."
      />

      <Modal isOpen={showCreate} onClose={() => { setShowCreate(false); setFormError(null); }} title="Add Machine">
        <MachineForm
          onSubmit={(data) => createMutation.mutate(data)}
          onCancel={() => { setShowCreate(false); setFormError(null); }}
          isLoading={createMutation.isPending}
          error={formError}
        />
      </Modal>

      <Modal isOpen={!!editing} onClose={() => { setEditing(null); setFormError(null); }} title="Edit Machine">
        {editing && (
          <MachineForm
            machine={editing}
            onSubmit={(data) => updateMutation.mutate({ id: editing.machine_id, data })}
            onCancel={() => { setEditing(null); setFormError(null); }}
            isLoading={updateMutation.isPending}
            error={formError}
          />
        )}
      </Modal>
    </div>
  );
}
