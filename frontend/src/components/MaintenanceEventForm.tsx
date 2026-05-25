import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { machinesApi } from '../services/machines';
import { componentsApi } from '../services/components';
import { MaintenanceEvent } from '../types';

interface MaintenanceEventFormProps {
  event?: MaintenanceEvent;
  onSubmit: (data: any) => void;
  onCancel: () => void;
  isLoading?: boolean;
  error?: string | null;
}

const eventTypes = ['inspection', 'lubrication', 'replacement', 'repair', 'calibration', 'cleaning'];
const triggerSources = ['preventive', 'corrective', 'condition_based', 'operator_request', 'system_alert'];
const toDateTimeLocal = (value?: string) => value ? value.slice(0, 16) : '';

export default function MaintenanceEventForm({ event, onSubmit, onCancel, isLoading, error }: MaintenanceEventFormProps) {
  const [formData, setFormData] = useState({
    machine_id: event?.machine_id?.toString() || '',
    component_id: event?.component_id?.toString() || '',
    event_type: event?.event_type || 'inspection',
    trigger_source: event?.trigger_source || 'preventive',
    work_order_code: event?.work_order_code || '',
    performed_at: toDateTimeLocal(event?.performed_at),
    duration_hours: event?.duration_hours?.toString() || '',
    technician: event?.technician || '',
    action_taken: event?.action_taken || '',
    parts_replaced: event?.parts_replaced || '',
    notes: event?.notes || '',
  });

  const { data: machines } = useQuery({
    queryKey: ['machines'],
    queryFn: () => machinesApi.list().then(r => r.data.data),
  });

  const { data: components } = useQuery({
    queryKey: ['components'],
    queryFn: () => componentsApi.list().then(r => r.data.data),
  });

  const handleChange = (changeEvent: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = changeEvent.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (submitEvent: React.FormEvent) => {
    submitEvent.preventDefault();
    onSubmit({
      machine_id: Number(formData.machine_id),
      component_id: formData.component_id ? Number(formData.component_id) : null,
      event_type: formData.event_type,
      trigger_source: formData.trigger_source,
      work_order_code: formData.work_order_code || null,
      performed_at: formData.performed_at,
      duration_hours: formData.duration_hours ? Number(formData.duration_hours) : null,
      technician: formData.technician || null,
      action_taken: formData.action_taken,
      parts_replaced: formData.parts_replaced || null,
      notes: formData.notes || null,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Machine</label>
          <select name="machine_id" value={formData.machine_id} onChange={handleChange} required className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <option value="">Select Machine</option>
            {(machines || []).map((machine: any) => (
              <option key={machine.machine_id} value={machine.machine_id}>{machine.machine_name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Component</label>
          <select name="component_id" value={formData.component_id} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <option value="">None</option>
            {(components || []).map((component: any) => (
              <option key={component.component_id} value={component.component_id}>{component.component_name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Type</label>
          <select name="event_type" value={formData.event_type} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            {eventTypes.map(type => <option key={type} value={type}>{type}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Trigger</label>
          <select name="trigger_source" value={formData.trigger_source} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            {triggerSources.map(source => <option key={source} value={source}>{source}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Performed At</label>
          <input type="datetime-local" name="performed_at" value={formData.performed_at} onChange={handleChange} required className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Duration</label>
          <input type="number" step="0.1" name="duration_hours" value={formData.duration_hours} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Work Order</label>
          <input name="work_order_code" value={formData.work_order_code} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Technician</label>
          <input name="technician" value={formData.technician} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Action Taken</label>
        <textarea name="action_taken" value={formData.action_taken} onChange={handleChange} required rows={2} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Parts Replaced</label>
        <input name="parts_replaced" value={formData.parts_replaced} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">Cancel</button>
        <button type="submit" disabled={isLoading} className="px-4 py-2 text-sm bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors">
          {isLoading ? 'Saving...' : event ? 'Update Event' : 'Create Event'}
        </button>
      </div>
    </form>
  );
}
