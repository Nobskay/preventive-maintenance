import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { machinesApi } from '../services/machines';
import { Downtime } from '../types';

interface DowntimeFormProps {
  downtime?: Downtime;
  onSubmit: (data: any) => void;
  onCancel: () => void;
  isLoading?: boolean;
  error?: string | null;
}

const severityLevels = ['critical', 'high', 'medium', 'low'];

const toDateTimeLocal = (value?: string) => value ? value.slice(0, 16) : '';

export default function DowntimeForm({ downtime, onSubmit, onCancel, isLoading, error }: DowntimeFormProps) {
  const [formData, setFormData] = useState({
    machine_id: downtime?.machine_id?.toString() || '',
    timestamp_start: toDateTimeLocal(downtime?.timestamp_start),
    timestamp_end: toDateTimeLocal(downtime?.timestamp_end),
    issue_description: downtime?.issue_description || '',
    root_cause: downtime?.root_cause || '',
    corrective_action: downtime?.corrective_action || '',
    severity_level: downtime?.severity_level || 'medium',
    is_unplanned: downtime?.is_unplanned ?? true,
  });

  const { data: machines } = useQuery({
    queryKey: ['machines'],
    queryFn: () => machinesApi.list().then(r => r.data.data),
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      machine_id: Number(formData.machine_id),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Machine</label>
        <select
          name="machine_id"
          value={formData.machine_id}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">Select Machine</option>
          {(machines || []).map((m: any) => (
            <option key={m.machine_id} value={m.machine_id}>{m.machine_name}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Time</label>
          <input
            type="datetime-local"
            name="timestamp_start"
            value={formData.timestamp_start}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Time</label>
          <input
            type="datetime-local"
            name="timestamp_end"
            value={formData.timestamp_end}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Issue Description</label>
        <textarea
          name="issue_description"
          value={formData.issue_description}
          onChange={handleChange}
          required
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="Describe the issue..."
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Root Cause</label>
          <input
            type="text"
            name="root_cause"
            value={formData.root_cause}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            placeholder="Root cause..."
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Severity</label>
          <select
            name="severity_level"
            value={formData.severity_level}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            {severityLevels.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Corrective Action</label>
        <textarea
          name="corrective_action"
          value={formData.corrective_action}
          onChange={handleChange}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="Corrective action taken..."
        />
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          name="is_unplanned"
          checked={formData.is_unplanned}
          onChange={handleChange}
          className="rounded border-gray-300"
        />
        <label className="text-sm text-gray-700 dark:text-gray-300">Unplanned Downtime</label>
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 text-sm bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          {isLoading ? 'Saving...' : downtime ? 'Update Downtime' : 'Log Downtime'}
        </button>
      </div>
    </form>
  );
}
