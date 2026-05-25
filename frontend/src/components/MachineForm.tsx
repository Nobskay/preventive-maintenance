import { useForm } from 'react-hook-form';
import { Machine, MachineCreate } from '../types';

interface MachineFormProps {
  machine?: Machine;
  onSubmit: (data: MachineCreate) => void;
  onCancel: () => void;
  isLoading?: boolean;
  error?: string | null;
}

const machineTypes = ['AGV', 'Robotic Arm', 'Conveyor', 'CNC', 'Compressor', 'Motor', 'Pump', 'Fan', 'Lathe', 'Drill', 'Other'];
const schedules = ['continuous', 'shift', 'part-time'];
const statuses = ['active', 'idle', 'maintenance', 'decommissioned'];

export default function MachineForm({ machine, onSubmit, onCancel, isLoading, error }: MachineFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<MachineCreate>({
    defaultValues: machine ? {
      machine_name: machine.machine_name,
      machine_type: machine.machine_type as any,
      manufacturer: machine.manufacturer,
      installation_date: machine.installation_date,
      operating_schedule: machine.operating_schedule as any,
      status: machine.status as any,
      notes: machine.notes || '',
    } : {
      operating_schedule: 'continuous',
      status: 'active',
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Machine Name</label>
        <input
          {...register('machine_name', { required: 'Required' })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          placeholder="e.g. CNC Lathe #1"
        />
        {errors.machine_name && <p className="text-red-500 text-xs mt-1">{errors.machine_name.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Type</label>
          <select
            {...register('machine_type', { required: 'Required' })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            {machineTypes.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Manufacturer</label>
          <input
            {...register('manufacturer')}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            placeholder="e.g. Haas Automation"
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Installation Date</label>
          <input
            type="date"
            {...register('installation_date', { required: 'Required' })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Schedule</label>
          <select
            {...register('operating_schedule')}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            {schedules.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
          <select
            {...register('status')}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            {statuses.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Notes</label>
        <textarea
          {...register('notes')}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="Optional notes about this machine..."
        />
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
          {isLoading ? 'Saving...' : machine ? 'Update Machine' : 'Create Machine'}
        </button>
      </div>
    </form>
  );
}
