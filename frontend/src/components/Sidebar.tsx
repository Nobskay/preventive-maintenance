import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  Settings,
  Clock,
  AlertTriangle,
  Wrench,
  BarChart3,
  ClipboardList,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/machines', icon: Cpu, label: 'Machines' },
  { to: '/components', icon: Settings, label: 'Components' },
  { to: '/downtime', icon: Clock, label: 'Downtime' },
  { to: '/alerts', icon: AlertTriangle, label: 'Alerts' },
  { to: '/recommendations', icon: Wrench, label: 'Maintenance' },
  { to: '/maintenance-history', icon: ClipboardList, label: 'History' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 dark:bg-gray-950 text-white flex flex-col">
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-xl font-bold text-emerald-400">MaintainIQ</h1>
        <p className="text-xs text-gray-400 mt-1">Predictive Maintenance</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-emerald-600/20 text-emerald-400'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`
            }
          >
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-500">v1.0.0</div>
      </div>
    </aside>
  );
}
