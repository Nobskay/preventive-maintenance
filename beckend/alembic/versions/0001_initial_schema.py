"""Initial industrial maintenance schema.

Revision ID: 0001
Revises:
Create Date: 2026-05-21 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def timestamp_columns():
    return [
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), server_default="technician", nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("role IN ('admin', 'manager', 'technician', 'viewer')", name="chk_role"),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "machines",
        sa.Column("machine_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("machine_name", sa.String(length=255), nullable=False),
        sa.Column("machine_type", sa.String(length=100), nullable=False),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("installation_date", sa.Date(), nullable=False),
        sa.Column("operating_schedule", sa.String(length=50), server_default="continuous", nullable=True),
        sa.Column("status", sa.String(length=50), server_default="active", nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint(
            "machine_type IN ('AGV', 'Robotic Arm', 'Conveyor', 'CNC', 'Compressor', "
            "'Motor', 'Pump', 'Fan', 'Lathe', 'Drill', 'Other')",
            name="chk_machine_type",
        ),
        sa.CheckConstraint("operating_schedule IN ('continuous', 'shift', 'part-time')", name="chk_schedule"),
        sa.CheckConstraint("status IN ('active', 'idle', 'maintenance', 'decommissioned')", name="chk_status"),
        sa.PrimaryKeyConstraint("machine_id"),
    )

    op.create_table(
        "components",
        sa.Column("component_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("component_name", sa.String(length=255), nullable=False),
        sa.Column("component_type", sa.String(length=100), nullable=False),
        sa.Column("lifetime_hours", sa.Integer(), nullable=True),
        sa.Column("lifetime_months", sa.Integer(), nullable=True),
        sa.Column("installed_runtime_hours", sa.Numeric(10, 2), server_default="0", nullable=True),
        sa.Column("warning_threshold_percent", sa.Numeric(5, 2), server_default="90", nullable=True),
        sa.Column("critical_threshold_percent", sa.Numeric(5, 2), server_default="100", nullable=True),
        sa.Column("replacement_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("maintenance_sop", sa.Text(), nullable=True),
        sa.Column("installation_date", sa.Date(), nullable=False),
        sa.Column("last_replacement_date", sa.Date(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint(
            "component_type IN ('bearing', 'seal', 'belt', 'chain', 'motor', 'pump', "
            "'sensor', 'valve', 'filter', 'hydraulic', 'pneumatic', 'other')",
            name="chk_component_type",
        ),
        sa.CheckConstraint(
            "warning_threshold_percent < critical_threshold_percent "
            "AND warning_threshold_percent > 0 AND critical_threshold_percent <= 100",
            name="chk_thresholds",
        ),
        sa.CheckConstraint("(lifetime_hours IS NOT NULL OR lifetime_months IS NOT NULL)", name="chk_lifetime"),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.machine_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("component_id"),
    )
    op.create_index("ix_components_machine_id", "components", ["machine_id"])

    op.create_table(
        "runtime",
        sa.Column("runtime_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("runtime_hours", sa.Numeric(10, 2), nullable=False),
        sa.Column("delta_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("data_source", sa.String(length=50), server_default="manual", nullable=True),
        sa.Column("recorded_by", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("runtime_hours >= 0", name="chk_runtime_hours"),
        sa.CheckConstraint("delta_hours IS NULL OR delta_hours >= 0", name="chk_delta_hours"),
        sa.CheckConstraint("data_source IN ('manual', 'csv_import', 'iot', 'plc', 'api', 'scada')", name="chk_data_source"),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.machine_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("runtime_id"),
    )
    op.create_index("ix_runtime_machine_id", "runtime", ["machine_id"])
    op.create_index("ix_runtime_timestamp", "runtime", ["timestamp"])
    op.create_index("idx_runtime_machine_timestamp", "runtime", ["machine_id", "timestamp"])

    op.create_table(
        "downtime",
        sa.Column("downtime_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("timestamp_start", sa.DateTime(), nullable=False),
        sa.Column("timestamp_end", sa.DateTime(), nullable=False),
        sa.Column("downtime_duration", sa.Interval(), nullable=True),
        sa.Column("issue_description", sa.Text(), nullable=False),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("corrective_action", sa.Text(), nullable=True),
        sa.Column("severity_level", sa.String(length=50), server_default="medium", nullable=False),
        sa.Column("component_affected", sa.Integer(), nullable=True),
        sa.Column("reported_by", sa.Integer(), nullable=True),
        sa.Column("resolved_by", sa.Integer(), nullable=True),
        sa.Column("is_unplanned", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("timestamp_start < timestamp_end", name="chk_timestamps"),
        sa.CheckConstraint("severity_level IN ('critical', 'high', 'medium', 'low')", name="chk_severity"),
        sa.ForeignKeyConstraint(["component_affected"], ["components.component_id"]),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.machine_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reported_by"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("downtime_id"),
    )
    op.create_index("ix_downtime_machine_id", "downtime", ["machine_id"])
    op.create_index("idx_downtime_machine_timestamp", "downtime", ["machine_id", "timestamp_start"])
    op.create_index("idx_downtime_severity", "downtime", ["severity_level"])

    op.create_table(
        "alerts",
        sa.Column("alert_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("component_id", sa.Integer(), nullable=True),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("alert_severity", sa.String(length=50), server_default="warning", nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("additional_data", sa.JSON(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_by", sa.Integer(), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint(
            "alert_type IN ('MAINTENANCE_DUE', 'WARNING', 'CRITICAL', 'INFO', 'FAILURE_PREDICTED')",
            name="chk_alert_type",
        ),
        sa.CheckConstraint("alert_severity IN ('critical', 'warning', 'info')", name="chk_alert_severity"),
        sa.ForeignKeyConstraint(["component_id"], ["components.component_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.machine_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("alert_id"),
    )
    op.create_index("ix_alerts_machine_id", "alerts", ["machine_id"])
    op.create_index("idx_alerts_machine_active", "alerts", ["machine_id", "is_active"])
    op.create_index("idx_alerts_created_at", "alerts", ["created_at"])

    op.create_table(
        "maintenance_recommendations",
        sa.Column("recommendation_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("component_id", sa.Integer(), nullable=True),
        sa.Column("recommendation_type", sa.String(length=100), nullable=False),
        sa.Column("recommended_by_system", sa.String(length=50), server_default="rule_engine", nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("urgency", sa.String(length=50), server_default="medium", nullable=True),
        sa.Column("estimated_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("estimated_duration_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="open", nullable=True),
        sa.Column("scheduled_date", sa.Date(), nullable=True),
        sa.Column("completed_date", sa.Date(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint(
            "recommendation_type IN ('replacement', 'inspection', 'lubrication', 'repair', 'adjustment', 'cleaning')",
            name="chk_rec_type",
        ),
        sa.CheckConstraint("urgency IN ('immediate', 'urgent', 'high', 'medium', 'low')", name="chk_urgency"),
        sa.CheckConstraint("status IN ('open', 'scheduled', 'in_progress', 'completed', 'cancelled')", name="chk_rec_status"),
        sa.ForeignKeyConstraint(["component_id"], ["components.component_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.machine_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("recommendation_id"),
    )
    op.create_index("ix_maintenance_recommendations_machine_id", "maintenance_recommendations", ["machine_id"])
    op.create_index("idx_recommendations_machine_status", "maintenance_recommendations", ["machine_id", "status"])

    op.create_table(
        "maintenance_events",
        sa.Column("maintenance_event_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("component_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("trigger_source", sa.String(length=50), server_default="preventive", nullable=True),
        sa.Column("work_order_code", sa.String(length=100), nullable=True),
        sa.Column("performed_at", sa.DateTime(), nullable=False),
        sa.Column("duration_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("technician", sa.String(length=255), nullable=True),
        sa.Column("action_taken", sa.Text(), nullable=False),
        sa.Column("parts_replaced", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint(
            "event_type IN ('inspection', 'lubrication', 'replacement', 'repair', 'calibration', 'cleaning')",
            name="chk_maintenance_event_type",
        ),
        sa.CheckConstraint(
            "trigger_source IN ('preventive', 'corrective', 'condition_based', 'operator_request', 'system_alert')",
            name="chk_maintenance_trigger_source",
        ),
        sa.ForeignKeyConstraint(["component_id"], ["components.component_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.machine_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("maintenance_event_id"),
        sa.UniqueConstraint("work_order_code"),
    )
    op.create_index("ix_maintenance_events_machine_id", "maintenance_events", ["machine_id"])
    op.create_index("ix_maintenance_events_component_id", "maintenance_events", ["component_id"])
    op.create_index("idx_maintenance_events_machine_performed", "maintenance_events", ["machine_id", "performed_at"])

    op.create_table(
        "kpi_snapshots",
        sa.Column("snapshot_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("mtbf_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("mttr_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("availability_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("failure_frequency", sa.Numeric(10, 4), nullable=True),
        sa.Column("total_uptime_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("total_downtime_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("total_failures", sa.Integer(), nullable=True),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("time_period", sa.String(length=50), server_default="month", nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.machine_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("snapshot_id"),
    )
    op.create_index("ix_kpi_snapshots_machine_id", "kpi_snapshots", ["machine_id"])
    op.create_index("idx_kpi_machine_date", "kpi_snapshots", ["machine_id", "snapshot_date"])


def downgrade() -> None:
    op.drop_table("kpi_snapshots")
    op.drop_table("maintenance_events")
    op.drop_table("maintenance_recommendations")
    op.drop_table("alerts")
    op.drop_table("downtime")
    op.drop_table("runtime")
    op.drop_table("components")
    op.drop_table("machines")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
