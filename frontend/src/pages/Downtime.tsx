import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import DataTable from '../components/DataTable';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import DowntimeForm from '../components/DowntimeForm';
import { downtimeApi } from '../services/downtime';
import { Downtime as DowntimeType } from '../types';

export default function Downtime() {
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<DowntimeType | null>(null);
  const [severityFilter, setSeverityFilter] = useState('');
  const [unplannedOnly, setUnplannedOnly] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: records, isLoading } = useQuery({
    queryKey: ['downtime', severityFilter, unplannedOnly],
    queryFn: () => downtimeApi.list({
      severity: severityFilter || undefined,
      unplanned_only: unplannedOnly,
    }).then(r => r.data.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => downtimeApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['downtime'] });
      setShowCreate(false);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Failed to create downtime record';
      setFormError(typeof message === 'string' ? message : JSON.stringify(message));
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => downtimeApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['downtime'] });
      setEditing(null);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Failed to update downtime record';
      setFormError(typeof message === 'string' ? message : JSON.stringify(message));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => downtimeApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['downtime'] }),
  });

  const columns = [
    {
      key: 'machine',
      header: 'Machine',
      render: (d: DowntimeType) => <span className="font-medium">Machine #{d.machine_id}</span>,
    },
    {
      key: 'issue_description',
      header: 'Issue',
      render: (d: DowntimeType) => (
        <div className="max-w-xs truncate">
          <span className="text-sm">{d.issue_description}</span>
          {d.root_cause && <p className="text-xs text-gray-400 mt-0.5">Root: {d.root_cause}</p>}
        </div>
      ),
    },
    {
      key: 'severity_level',
      header: 'Severity',
      render: (d: DowntimeType) => <StatusBadge status={d.severity_level} />,
    },
    {
      key: 'is_unplanned',
      header: 'Type',
      render: (d: DowntimeType) => (
        <span className={`text-xs px-2 py-0.5 rounded-full ${d.is_unplanned ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
          {d.is_unplanned ? 'Unplanned' : 'Scheduled'}
        </span>
      ),
    },
    {
      key: 'timestamp_start',
      header: 'Start',
      render: (d: DowntimeType) => new Date(d.timestamp_start).toLocaleString(),
    },
    {
      key: 'downtime_duration',
      header: 'Duration',
      render: (d: DowntimeType) => d.downtime_duration || '--',
    },
    {
      key: 'corrective_action',
      header: 'Action',
      render: (d: DowntimeType) => (
        <span className="text-xs text-gray-500 max-w-xs truncate block">{d.corrective_action || '--'}</span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (d: DowntimeType) => (
        <div className="flex gap-3">
          <button
            onClick={(e) => { e.stopPropagation(); setEditing(d); setFormError(null); }}
            className="text-xs text-blue-500 hover:text-blue-700"
          >
            Edit
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(d.downtime_id); }}
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
        title="Downtime Log"
        subtitle={`${(records || []).length} records`}
        actions={
          <button
            onClick={() => { setShowCreate(true); setFormError(null); }}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <Plus size={16} />
            Log Downtime
          </button>
        }
      />

      <div className="flex gap-3 mb-4">
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
        >
          <option value="">All Severity</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <input
            type="checkbox"
            checked={unplannedOnly}
            onChange={(e) => setUnplannedOnly(e.target.checked)}
            className="rounded border-gray-300"
          />
          Unplanned only
        </label>
      </div>

      <DataTable columns={columns} data={records || []} emptyMessage="No downtime records found." />

      <Modal isOpen={showCreate} onClose={() => { setShowCreate(false); setFormError(null); }} title="Log Downtime Event">
        <DowntimeForm
          onSubmit={(data) => createMutation.mutate(data)}
          onCancel={() => { setShowCreate(false); setFormError(null); }}
          isLoading={createMutation.isPending}
          error={formError}
        />
      </Modal>

      <Modal isOpen={!!editing} onClose={() => { setEditing(null); setFormError(null); }} title="Edit Downtime Event">
        {editing && (
          <DowntimeForm
            downtime={editing}
            onSubmit={(data) => updateMutation.mutate({ id: editing.downtime_id, data })}
            onCancel={() => { setEditing(null); setFormError(null); }}
            isLoading={updateMutation.isPending}
            error={formError}
          />
        )}
      </Modal>
    </div>
  );
}
