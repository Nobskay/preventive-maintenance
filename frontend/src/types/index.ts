// Frontend TypeScript Types

export interface Machine {
  machine_id: number;
  machine_name: string;
  machine_type: string;
  manufacturer: string;
  installation_date: string;
  operating_schedule: string;
  status: 'active' | 'idle' | 'maintenance' | 'decommissioned';
  created_at: string;
  updated_at: string;
  notes?: string;
}

export interface MachineCreate {
  machine_name: string;
  machine_type: string;
  manufacturer?: string;
  installation_date: string;
  operating_schedule?: string;
  status?: string;
  notes?: string;
}

export interface Component {
  component_id: number;
  machine_id: number;
  component_name: string;
  component_type: string;
  lifetime_hours?: number;
  lifetime_months?: number;
  installed_runtime_hours: number;
  warning_threshold_percent: number;
  critical_threshold_percent: number;
  replacement_cost?: number;
  maintenance_sop?: string;
  installation_date: string;
  last_replacement_date?: string;
  created_at: string;
  updated_at: string;
  health_percent?: number;
  health_status?: 'HEALTHY' | 'WARNING' | 'CRITICAL';
  remaining_useful_life_hours?: number;
  remaining_useful_life_days?: number;
}

export interface MaintenanceEvent {
  maintenance_event_id: number;
  machine_id: number;
  component_id?: number;
  event_type: 'inspection' | 'lubrication' | 'replacement' | 'repair' | 'calibration' | 'cleaning';
  trigger_source: 'preventive' | 'corrective' | 'condition_based' | 'operator_request' | 'system_alert';
  work_order_code?: string;
  performed_at: string;
  duration_hours?: number;
  technician?: string;
  action_taken: string;
  parts_replaced?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Runtime {
  runtime_id: number;
  machine_id: number;
  runtime_hours: number;
  delta_hours?: number;
  timestamp: string;
  data_source: 'manual' | 'csv_import' | 'iot' | 'plc' | 'api' | 'scada';
  recorded_by?: number;
  notes?: string;
}

export interface Downtime {
  downtime_id: number;
  machine_id: number;
  timestamp_start: string;
  timestamp_end: string;
  downtime_duration: string;
  issue_description: string;
  root_cause?: string;
  corrective_action?: string;
  severity_level: 'critical' | 'high' | 'medium' | 'low';
  component_affected?: number;
  is_unplanned: boolean;
  reported_by?: number;
  resolved_by?: number;
  created_at: string;
}

export interface Alert {
  alert_id: number;
  machine_id: number;
  component_id?: number;
  alert_type: 'MAINTENANCE_DUE' | 'WARNING' | 'CRITICAL' | 'INFO' | 'FAILURE_PREDICTED';
  alert_severity: 'critical' | 'warning' | 'info';
  message: string;
  additional_data?: Record<string, any>;
  created_at: string;
  resolved_at?: string;
  resolved_by?: number;
  resolution_notes?: string;
  is_active: boolean;
}

export interface Recommendation {
  recommendation_id: number;
  machine_id: number;
  component_id?: number;
  recommendation_type: 'replacement' | 'inspection' | 'lubrication' | 'repair' | 'adjustment' | 'cleaning';
  recommended_by_system: 'rule_engine' | 'ml_model' | 'user' | 'technician';
  description: string;
  urgency: 'immediate' | 'urgent' | 'high' | 'medium' | 'low';
  estimated_cost?: number;
  estimated_duration_hours?: number;
  status: 'open' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  scheduled_date?: string;
  completed_date?: string;
  created_at: string;
  updated_at: string;
}

export interface KPI {
  machine_id: number;
  machine_name: string;
  mtbf_hours: number;
  mttr_hours: number;
  availability_percent: number;
  failure_frequency: number;
  total_failures: number;
  total_uptime_hours: number;
  total_downtime_hours: number;
  period?: string;
}

export interface DashboardSummary {
  total_machines: number;
  active_machines: number;
  machines_in_maintenance: number;
  total_components: number;
  active_alerts: number;
  critical_alerts: number;
  warning_alerts: number;
  avg_availability: number;
  avg_mtbf: number;
  avg_mttr: number;
  scheduled_maintenance_today: number;
  overdue_recommendations: number;
}

export interface MachineHealth {
  machine_id: number;
  machine_name: string;
  overall_health_percent: number;
  overall_health_status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
  components: ComponentHealth[];
  active_alerts: number;
}

export interface ComponentHealth {
  component_id: number;
  component_name: string;
  health_percent: number;
  life_consumed_percent: number;
  health_status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
  maintenance_due_status: string;
  remaining_useful_life_hours: number;
  remaining_useful_life_days: number;
  current_runtime_hours: number;
  installed_runtime_hours: number;
  used_runtime_hours: number;
}

export interface User {
  user_id: number;
  username: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'manager' | 'technician' | 'viewer';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}
