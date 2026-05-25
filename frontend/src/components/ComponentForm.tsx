import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Component } from '../types';
import { machinesApi } from '../services/machines';

interface ComponentFormProps {
  component?: Component;
  onSubmit: (data: any) => void;
  onCancel: () => void;
  isLoading?: boolean;
  error?: string | null;
}

const componentTypes = ['bearing', 'seal', 'belt', 'chain', 'motor', 'pump', 'sensor', 'valve', 'filter', 'hydraulic', 'pneumatic', 'other'];

export default function ComponentForm({ component, onSubmit, onCancel, isLoading, error }: ComponentFormProps) {
  const [formData, setFormData] = useState({
    machine_id: component?.machine_id?.toString() || '',
    component_name: component?.component_name || '',
    component_type: component?.component_type || 'bearing',
    lifetime_hours: component?.lifetime_hours?.toString() || '',
    lifetime_months: component?.lifetime_months?.toString() || '',
    installed_runtime_hours: component?.installed_runtime_hours?.toString() || '0',
    warning_threshold_percent: component?.warning_threshold_percent?.toString() || '90',
    critical_threshold_percent: component?.critical_threshold_percent?.toString() || '100',
    replacement_cost: component?.replacement_cost?.toString() || '',
    maintenance_sop: component?.maintenance_sop || '',
    installation_date: component?.installation_date || '',
    last_replacement_date: component?.last_replacement_date || '',
  });

  const { data: machines } = useQuery({
    queryKey: ['machines'],
    queryFn: () => machinesApi.list().then(r => r.data.data),
  });

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const toNumberOrNull = (value: string) => value === '' ? null : Number(value);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSubmit({
      machine_id: Number(formData.machine_id),
      component_name: formData.component_name,
      component_type: formData.component_type,
      lifetime_hours: toNumberOrNull(formData.lifetime_hours),
      lifetime_months: toNumberOrNull(formData.lifetime_months),
      installed_runtime_hours: Number(formData.installed_runtime_hours || 0),
      warning_threshold_percent: Number(formData.warning_threshold_percent),
      critical_threshold_percent: Number(formData.critical_threshold_percent),
      replacement_cost: toNumberOrNull(formData.replacement_cost),
      maintenance_sop: formData.maintenance_sop || null,
      installation_date: formData.installation_date,
      last_replacement_date: formData.last_replacement_date || null,
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
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Component Type</label>
          <select name="component_type" value={formData.component_type} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            {componentTypes.map(type => <option key={type} value={type}>{type}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Component Name</label>
        <input name="component_name" value={formData.component_name} onChange={handleChange} required className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" placeholder="e.g. Spindle Bearing" />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Lifetime Hours</label>
          <input type="number" name="lifetime_hours" value={formData.lifetime_hours} onChange={handleChange} min="1" className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Lifetime Months</label>
          <input type="number" name="lifetime_months" value={formData.lifetime_months} onChange={handleChange} min="1" className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Installed Runtime</label>
          <input type="number" name="installed_runtime_hours" value={formData.installed_runtime_hours} onChange={handleChange} min="0" className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Warning %</label>
          <input type="number" name="warning_threshold_percent" value={formData.warning_threshold_percent} onChange={handleChange} min="1" max="99" required className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Critical %</label>
          <input type="number" name="critical_threshold_percent" value={formData.critical_threshold_percent} onChange={handleChange} min="2" max="100" required className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Install Date</label>
          <input type="date" name="installation_date" value={formData.installation_date} onChange={handleChange} required className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Replacement Cost</label>
          <input type="number" name="replacement_cost" value={formData.replacement_cost} onChange={handleChange} min="0" className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Maintenance SOP</label>
        <textarea name="maintenance_sop" value={formData.maintenance_sop} onChange={handleChange} rows={3} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" placeholder="Inspection or replacement procedure..." />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">Cancel</button>
        <button type="submit" disabled={isLoading} className="px-4 py-2 text-sm bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors">
          {isLoading ? 'Saving...' : component ? 'Update Component' : 'Create Component'}
        </button>
      </div>
    </form>
  );
}
