"""
Deterministic industrial seed data for MaintainIQ.

Run manually:
    python -m app.seed_data

Docker demo environments can also enable AUTO_SEED_DATA=true.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal

from passlib.context import CryptContext

from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models import (
    Alert,
    Component,
    Downtime,
    Machine,
    MaintenanceEvent,
    MaintenanceRecommendation,
    Runtime,
    User,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_tables():
    Base.metadata.create_all(bind=engine)


def seed_users(db):
    users = [
        User(
            username="admin",
            email="admin@maintainiq.local",
            password_hash=pwd_context.hash("admin123"),
            full_name="Plant Reliability Administrator",
            role="admin",
        ),
        User(
            username="planner",
            email="planner@maintainiq.local",
            password_hash=pwd_context.hash("planner123"),
            full_name="Maintenance Planner",
            role="manager",
        ),
        User(
            username="tech1",
            email="tech1@maintainiq.local",
            password_hash=pwd_context.hash("tech123"),
            full_name="Senior Maintenance Technician",
            role="technician",
        ),
    ]
    db.add_all(users)
    db.flush()
    return users


def seed_machines(db):
    machines = [
        Machine(
            machine_name="AGV-01",
            machine_type="AGV",
            manufacturer="KUKA",
            installation_date=date(2024, 6, 10),
            operating_schedule="shift",
            status="active",
            notes="Automated guided vehicle serving inbound material flow.",
        ),
        Machine(
            machine_name="CNC-02",
            machine_type="CNC",
            manufacturer="Haas Automation",
            installation_date=date(2023, 8, 15),
            operating_schedule="shift",
            status="maintenance",
            notes="Critical machining asset for precision spindle operations.",
        ),
        Machine(
            machine_name="Conveyor-03",
            machine_type="Conveyor",
            manufacturer="Siemens",
            installation_date=date(2024, 11, 5),
            operating_schedule="continuous",
            status="active",
            notes="Packaging line conveyor with gearbox and roller drive section.",
        ),
    ]
    db.add_all(machines)
    db.flush()
    return machines


def seed_components(db, machines):
    machine_map = {machine.machine_name: machine for machine in machines}
    component_specs = [
        ("AGV-01", "Motor Bearing", "bearing", 5000, 24, 0, 420, "Inspect vibration trend, lubricate bearing housing, replace if axial play is detected."),
        ("AGV-01", "Battery", "other", None, 24, 0, 2400, "Check charge cycle count, thermal marks, and BMS fault history before replacement."),
        ("AGV-01", "Wheel Assembly", "bearing", 6500, 30, 0, 620, "Inspect tread wear, torque fasteners, verify wheel alignment."),
        ("CNC-02", "Spindle Bearing", "bearing", 6000, 24, 0, 3600, "Run spindle vibration test, lock-out machine, replace bearing set and balance spindle."),
        ("CNC-02", "Cooling Pump", "pump", 8000, 36, 0, 920, "Inspect coolant flow, seal leakage, impeller wear, and motor temperature."),
        ("CNC-02", "Belt Drive", "belt", 3000, 18, 3500, 480, "Check belt tension, pulley alignment, cracks, and oil contamination."),
        ("Conveyor-03", "Conveyor Belt", "belt", 3000, 18, 0, 700, "Inspect belt tracking, edge wear, splice condition, and tensioner setting."),
        ("Conveyor-03", "Gearbox", "motor", 12000, 48, 0, 2600, "Check oil condition, backlash, casing temperature, and abnormal noise."),
        ("Conveyor-03", "Roller Motor", "motor", 8000, 36, 0, 1200, "Trend motor current, inspect coupling, clean vents, and verify overload settings."),
    ]

    components = []
    for machine_name, name, ctype, hours, months, installed_runtime, cost, sop in component_specs:
        machine = machine_map[machine_name]
        component = Component(
            machine_id=machine.machine_id,
            component_name=name,
            component_type=ctype,
            lifetime_hours=hours,
            lifetime_months=months,
            installed_runtime_hours=Decimal(str(installed_runtime)),
            warning_threshold_percent=Decimal("90"),
            critical_threshold_percent=Decimal("100"),
            replacement_cost=Decimal(str(cost)),
            maintenance_sop=sop,
            installation_date=machine.installation_date,
            last_replacement_date=machine.installation_date,
        )
        components.append(component)
    db.add_all(components)
    db.flush()
    return components


def seed_runtime(db, machines):
    current_runtime = {
        "AGV-01": Decimal("4700"),
        "CNC-02": Decimal("6200"),
        "Conveyor-03": Decimal("1800"),
    }
    daily_runtime = {
        "AGV-01": Decimal("14.0"),
        "CNC-02": Decimal("11.5"),
        "Conveyor-03": Decimal("20.0"),
    }

    start = datetime.utcnow() - timedelta(days=89)
    records = []
    for machine in machines:
        total_days = Decimal("89")
        baseline = current_runtime[machine.machine_name] - daily_runtime[machine.machine_name] * total_days
        cumulative = baseline
        for day in range(90):
            timestamp = start + timedelta(days=day, hours=6)
            delta = daily_runtime[machine.machine_name]
            if day in (16, 42, 71):
                delta = delta * Decimal("0.55")
            cumulative += delta
            if day == 89:
                cumulative = current_runtime[machine.machine_name]
                delta = current_runtime[machine.machine_name] - records[-1].runtime_hours if records else delta
            records.append(
                Runtime(
                    machine_id=machine.machine_id,
                    runtime_hours=cumulative.quantize(Decimal("0.01")),
                    delta_hours=delta.quantize(Decimal("0.01")),
                    timestamp=timestamp,
                    data_source="plc",
                    notes="Daily cumulative runtime captured from production historian.",
                )
            )
    db.add_all(records)
    db.flush()
    return records


def seed_downtime(db, machines, components):
    machine_map = {machine.machine_name: machine for machine in machines}
    component_map = {component.component_name: component for component in components}
    now = datetime.utcnow()
    event_specs = [
        ("AGV-01", "Motor Bearing", 82, 2.5, "Abnormal vibration detected during transfer run", "Bearing lubrication starvation", "Lubricated bearing and reduced route speed pending replacement", "high", True),
        ("AGV-01", "Battery", 48, 1.2, "AGV low-voltage alarm under payload", "Battery internal resistance increasing", "Balanced battery cells and scheduled pack inspection", "medium", True),
        ("AGV-01", "Wheel Assembly", 19, 1.0, "Wheel slip on docking station", "Tread contamination from packaging dust", "Cleaned wheel assembly and recalibrated docking approach", "low", True),
        ("CNC-02", "Spindle Bearing", 76, 6.5, "Spindle high-vibration shutdown", "Bearing wear with rising vibration velocity", "Stopped machine and scheduled bearing replacement", "critical", True),
        ("CNC-02", "Cooling Pump", 51, 3.0, "Coolant temperature above process limit", "Cooling pump seal leakage reduced flow", "Replaced seal kit and flushed coolant circuit", "high", True),
        ("CNC-02", "Belt Drive", 23, 2.2, "Axis drive belt squeal during acceleration", "Belt tension drift and pulley misalignment", "Adjusted tension and aligned pulley", "medium", True),
        ("Conveyor-03", "Conveyor Belt", 68, 1.8, "Belt tracking alarm at transfer point", "Tensioner imbalance after product jam", "Realigned belt and reset tensioner", "medium", True),
        ("Conveyor-03", "Gearbox", 36, 2.0, "Gearbox oil inspection hold", "Scheduled oil sampling and filter change", "Changed oil and inspected magnetic plug", "low", False),
        ("Conveyor-03", "Roller Motor", 14, 1.1, "Roller motor thermal warning", "Ventilation blocked by dust accumulation", "Cleaned vents and verified current draw", "low", True),
    ]

    downtime_events = []
    for machine_name, component_name, days_ago, duration, issue, root, action, severity, unplanned in event_specs:
        machine = machine_map[machine_name]
        component = component_map[component_name]
        start = now - timedelta(days=days_ago, hours=3)
        end = start + timedelta(hours=duration)
        downtime_events.append(
            Downtime(
                machine_id=machine.machine_id,
                component_affected=component.component_id,
                timestamp_start=start,
                timestamp_end=end,
                downtime_duration=end - start,
                issue_description=issue,
                root_cause=root,
                corrective_action=action,
                severity_level=severity,
                is_unplanned=unplanned,
            )
        )
    db.add_all(downtime_events)
    db.flush()
    return downtime_events


def seed_maintenance_events(db, machines, components):
    machine_map = {machine.machine_name: machine for machine in machines}
    component_map = {component.component_name: component for component in components}
    now = datetime.utcnow()
    specs = [
        ("WO-AGV-0101", "AGV-01", "Motor Bearing", "lubrication", "condition_based", 81, 1.5, "Senior Maintenance Technician", "Lubricated motor bearing housing and captured vibration baseline.", "High-temp bearing grease"),
        ("WO-AGV-0102", "AGV-01", "Battery", "inspection", "system_alert", 47, 1.0, "Maintenance Planner", "Performed BMS diagnostic and charge-cycle review.", None),
        ("WO-CNC-0201", "CNC-02", "Cooling Pump", "repair", "corrective", 50, 2.5, "Senior Maintenance Technician", "Replaced cooling pump seal kit and verified flow recovery.", "Seal kit, coolant filter"),
        ("WO-CNC-0202", "CNC-02", "Belt Drive", "inspection", "condition_based", 22, 1.0, "Maintenance Planner", "Adjusted belt tension and inspected pulley runout.", None),
        ("WO-CONV-0301", "Conveyor-03", "Gearbox", "inspection", "preventive", 35, 2.0, "Senior Maintenance Technician", "Completed gearbox oil sampling and magnetic plug inspection.", "Gear oil, breather filter"),
        ("WO-CONV-0302", "Conveyor-03", "Conveyor Belt", "repair", "corrective", 67, 1.3, "Senior Maintenance Technician", "Corrected belt tracking and restored transfer alignment.", None),
    ]

    events = []
    for code, machine_name, component_name, event_type, trigger, days_ago, duration, tech, action, parts in specs:
        events.append(
            MaintenanceEvent(
                machine_id=machine_map[machine_name].machine_id,
                component_id=component_map[component_name].component_id,
                event_type=event_type,
                trigger_source=trigger,
                work_order_code=code,
                performed_at=now - timedelta(days=days_ago),
                duration_hours=Decimal(str(duration)),
                technician=tech,
                action_taken=action,
                parts_replaced=parts,
                notes="Seeded maintenance history for reliability analytics and audit trail.",
            )
        )
    db.add_all(events)
    db.flush()
    return events


def seed_alerts(db, machines, components):
    from app.services.alert_service import generate_maintenance_alerts

    generated = generate_maintenance_alerts(db)
    if not generated:
        return generated
    return generated


def seed_recommendations(db):
    from app.services.recommendation_service import generate_recommendations

    return generate_recommendations(db)


def run():
    print("Seeding deterministic industrial demo data...")
    create_tables()
    db = SessionLocal()
    try:
        if db.query(Machine).first():
            print("Seed data already exists; skipping.")
            return
        users = seed_users(db)
        machines = seed_machines(db)
        components = seed_components(db, machines)
        runtime_records = seed_runtime(db, machines)
        downtime_events = seed_downtime(db, machines, components)
        maintenance_events = seed_maintenance_events(db, machines, components)
        alerts = seed_alerts(db, machines, components)
        recommendations = seed_recommendations(db)
        db.commit()
        print(f"  Users: {len(users)}")
        print(f"  Machines: {len(machines)}")
        print(f"  Components: {len(components)}")
        print(f"  Runtime records: {len(runtime_records)}")
        print(f"  Downtime events: {len(downtime_events)}")
        print(f"  Maintenance events: {len(maintenance_events)}")
        print(f"  Alerts: {len(alerts)}")
        print(f"  Recommendations: {len(recommendations)}")
        print("Seed complete: healthy, warning, and critical states are available.")
    except Exception as exc:
        db.rollback()
        print(f"Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
