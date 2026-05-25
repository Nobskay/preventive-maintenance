-- ================================================================
-- Predictive Maintenance System - Database Schema
-- PostgreSQL 15+
-- Reference schema only. Runtime deployments should apply backend Alembic
-- migrations so schema changes are versioned and repeatable.
-- ================================================================

-- ================================================================
-- 1. USERS TABLE (for RBAC)
-- ================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'technician',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    CONSTRAINT chk_role CHECK (role IN ('admin', 'manager', 'technician', 'viewer'))
);

-- ================================================================
-- 2. MACHINES TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS machines (
    machine_id SERIAL PRIMARY KEY,
    machine_name VARCHAR(255) NOT NULL,
    machine_type VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(255),
    installation_date DATE NOT NULL,
    operating_schedule VARCHAR(50) DEFAULT 'continuous',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    CONSTRAINT chk_machine_type CHECK (machine_type IN (
        'AGV', 'Robotic Arm', 'Conveyor', 'CNC', 'Compressor',
        'Motor', 'Pump', 'Fan', 'Lathe', 'Drill', 'Other'
    )),
    CONSTRAINT chk_schedule CHECK (operating_schedule IN ('continuous', 'shift', 'part-time')),
    CONSTRAINT chk_status CHECK (status IN ('active', 'idle', 'maintenance', 'decommissioned'))
);

-- ================================================================
-- 3. COMPONENTS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS components (
    component_id SERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    component_name VARCHAR(255) NOT NULL,
    component_type VARCHAR(100) NOT NULL,
    lifetime_hours INTEGER,
    lifetime_months INTEGER,
    installed_runtime_hours DECIMAL(10,2) DEFAULT 0,
    warning_threshold_percent DECIMAL(5,2) DEFAULT 90,
    critical_threshold_percent DECIMAL(5,2) DEFAULT 100,
    replacement_cost DECIMAL(10,2),
    maintenance_sop TEXT,
    installation_date DATE NOT NULL,
    last_replacement_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_component_type CHECK (component_type IN (
        'bearing', 'seal', 'belt', 'chain', 'motor', 'pump',
        'sensor', 'valve', 'filter', 'hydraulic', 'pneumatic', 'other'
    )),
    CONSTRAINT chk_thresholds CHECK (
        warning_threshold_percent < critical_threshold_percent
        AND warning_threshold_percent > 0
        AND critical_threshold_percent <= 100
    ),
    CONSTRAINT chk_lifetime CHECK (
        (lifetime_hours IS NOT NULL OR lifetime_months IS NOT NULL)
    )
);

-- ================================================================
-- 4. RUNTIME TABLE (Time-Series Data)
-- ================================================================
CREATE TABLE IF NOT EXISTS runtime (
    runtime_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    runtime_hours DECIMAL(10,2) NOT NULL,
    delta_hours DECIMAL(10,2),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(50) DEFAULT 'manual',
    recorded_by INTEGER REFERENCES users(user_id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_runtime_hours CHECK (runtime_hours >= 0),
    CONSTRAINT chk_delta_hours CHECK (delta_hours IS NULL OR delta_hours >= 0),
    CONSTRAINT chk_data_source CHECK (data_source IN ('manual', 'csv_import', 'iot', 'plc', 'api', 'scada'))
);

CREATE INDEX IF NOT EXISTS idx_runtime_machine_timestamp ON runtime(machine_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_runtime_timestamp ON runtime(timestamp DESC);

-- ================================================================
-- 5. DOWNTIME TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS downtime (
    downtime_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    timestamp_start TIMESTAMP NOT NULL,
    timestamp_end TIMESTAMP NOT NULL,
    downtime_duration INTERVAL,
    issue_description TEXT NOT NULL,
    root_cause TEXT,
    corrective_action TEXT,
    severity_level VARCHAR(50) NOT NULL DEFAULT 'medium',
    component_affected INTEGER REFERENCES components(component_id),
    reported_by INTEGER REFERENCES users(user_id),
    resolved_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_unplanned BOOLEAN DEFAULT true,
    CONSTRAINT chk_timestamps CHECK (timestamp_start < timestamp_end),
    CONSTRAINT chk_severity CHECK (severity_level IN ('critical', 'high', 'medium', 'low'))
);

CREATE INDEX IF NOT EXISTS idx_downtime_machine_timestamp ON downtime(machine_id, timestamp_start DESC);
CREATE INDEX IF NOT EXISTS idx_downtime_severity ON downtime(severity_level);

-- ================================================================
-- 6. ALERTS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS alerts (
    alert_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    component_id INTEGER REFERENCES components(component_id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL,
    alert_severity VARCHAR(50) DEFAULT 'warning',
    message TEXT NOT NULL,
    additional_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(user_id),
    resolution_notes TEXT,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT chk_alert_type CHECK (alert_type IN ('MAINTENANCE_DUE', 'WARNING', 'CRITICAL', 'INFO', 'FAILURE_PREDICTED')),
    CONSTRAINT chk_alert_severity CHECK (alert_severity IN ('critical', 'warning', 'info'))
);

CREATE INDEX IF NOT EXISTS idx_alerts_machine_active ON alerts(machine_id, is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);

-- ================================================================
-- 7. MAINTENANCE RECOMMENDATIONS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS maintenance_recommendations (
    recommendation_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    component_id INTEGER REFERENCES components(component_id) ON DELETE SET NULL,
    recommendation_type VARCHAR(100) NOT NULL,
    recommended_by_system VARCHAR(50) DEFAULT 'rule_engine',
    description TEXT NOT NULL,
    urgency VARCHAR(50) DEFAULT 'medium',
    estimated_cost DECIMAL(10,2),
    estimated_duration_hours DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'open',
    scheduled_date DATE,
    completed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_rec_type CHECK (recommendation_type IN ('replacement', 'inspection', 'lubrication', 'repair', 'adjustment', 'cleaning')),
    CONSTRAINT chk_urgency CHECK (urgency IN ('immediate', 'urgent', 'high', 'medium', 'low')),
    CONSTRAINT chk_rec_status CHECK (status IN ('open', 'scheduled', 'in_progress', 'completed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_recommendations_machine_status ON maintenance_recommendations(machine_id, status);

-- ================================================================
-- 8. MAINTENANCE EVENTS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS maintenance_events (
    maintenance_event_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    component_id INTEGER REFERENCES components(component_id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    trigger_source VARCHAR(50) DEFAULT 'preventive',
    work_order_code VARCHAR(100) UNIQUE,
    performed_at TIMESTAMP NOT NULL,
    duration_hours DECIMAL(10,2),
    technician VARCHAR(255),
    action_taken TEXT NOT NULL,
    parts_replaced TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_maintenance_event_type CHECK (event_type IN ('inspection', 'lubrication', 'replacement', 'repair', 'calibration', 'cleaning')),
    CONSTRAINT chk_maintenance_trigger_source CHECK (trigger_source IN ('preventive', 'corrective', 'condition_based', 'operator_request', 'system_alert'))
);

CREATE INDEX IF NOT EXISTS idx_maintenance_events_machine_performed ON maintenance_events(machine_id, performed_at);

-- ================================================================
-- 9. KPI SNAPSHOTS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS kpi_snapshots (
    snapshot_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    mtbf_hours DECIMAL(10,2),
    mttr_hours DECIMAL(10,2),
    availability_percent DECIMAL(5,2),
    failure_frequency DECIMAL(10,4),
    total_uptime_hours DECIMAL(10,2),
    total_downtime_hours DECIMAL(10,2),
    total_failures INTEGER,
    snapshot_date DATE NOT NULL,
    time_period VARCHAR(50) DEFAULT 'month',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kpi_machine_date ON kpi_snapshots(machine_id, snapshot_date DESC);
