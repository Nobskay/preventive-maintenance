# Predictive Maintenance System - Architecture

## 1. System Overview

This is a modern industrial predictive maintenance and reliability monitoring platform designed for manufacturing environments including AGV systems, robotics, conveyors, CNC machines, compressors, and industrial automation equipment.

The system follows **Clean Architecture** principles with separation of concerns, making it scalable, testable, and maintainable.

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TailwindCSS)           │
│  - Dashboard (KPIs, Alerts, Health)                         │
│  - Machine Management (CRUD)                                │
│  - Component Management                                     │
│  - Runtime Tracking & Analytics                             │
│  - Downtime Reporting                                       │
│  - Maintenance Recommendations                              │
└────────────────────┬────────────────────────────────────────┘
                     │ (REST API / JSON)
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  API LAYER (FastAPI)                        │
│  - Authentication & Authorization                           │
│  - Request Validation                                       │
│  - Response Serialization                                   │
│  - Error Handling                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              SERVICE/BUSINESS LOGIC LAYER                    │
│  ┌──────────────────┬──────────────────┬──────────────────┐  │
│  │ MachineService   │ ComponentService │ RuntimeService   │  │
│  │ - CRUD Ops       │ - Health Calc    │ - Data Import    │  │
│  │ - Monitoring     │ - Lifecycle Mgmt │ - Tracking       │  │
│  └──────────────────┴──────────────────┴──────────────────┘  │
│  ┌──────────────────┬──────────────────┬──────────────────┐  │
│  │DowntimeService   │MaintenanceEngine │AnalyticsService │  │
│  │ - Logging        │ - Alerts         │ - KPIs (MTBF)    │  │
│  │ - RCA            │ - Predictions    │ - Trends         │  │
│  └──────────────────┴──────────────────┴──────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              DATA ACCESS LAYER (SQLAlchemy ORM)              │
│  - Database Queries                                         │
│  - Transaction Management                                   │
│  - Data Relationships                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              DATABASE (PostgreSQL)                           │
│  - Machines Table                                           │
│  - Components Table                                         │
│  - Runtime History Table                                    │
│  - Downtime Logs Table                                      │
│  - Alerts & Recommendations Table                           │
│  - KPI Snapshots Table                                      │
└─────────────────────────────────────────────────────────────┘
```

## 3. Design Patterns & Principles

### 3.1 Clean Architecture
- **Entities Layer**: Core business models (Machine, Component, Runtime, Downtime)
- **Use Cases Layer**: Service layer (business logic)
- **Interface Adapters**: API routes and schemas
- **Frameworks & Drivers**: FastAPI, SQLAlchemy, PostgreSQL

### 3.2 Design Patterns
- **Repository Pattern**: Abstract database access
- **Service Pattern**: Centralize business logic
- **Factory Pattern**: Create complex objects
- **Strategy Pattern**: Multiple calculation algorithms (MTBF, MTTR, RUL)
- **Observer Pattern**: Alert and notification system (future)

### 3.3 SOLID Principles
- **S**ingle Responsibility: Each service handles one concern
- **O**pen/Closed: Services extensible without modification
- **L**iskov Substitution: Service interfaces are substitutable
- **I**nterface Segregation: Specific schemas for each endpoint
- **D**ependency Inversion: Depend on abstractions, not concretions

## 4. Core Entities & Relationships

```
┌──────────────┐
│   MACHINE    │
├──────────────┤
│ machine_id   │
│ name         │
│ type         │
│ manufacturer │
│ install_date │
│ status       │
│ schedule     │
└──────────────┘
       │1
       │
      *│
       │
    ┌──────────────┐         ┌──────────────┐
    │  COMPONENT   │────────→│   RUNTIME    │
    ├──────────────┤    1    ├──────────────┤
    │ component_id │────*    │ runtime_id   │
    │ machine_id   │         │ machine_id   │
    │ name         │         │ hours        │
    │ type         │         │ timestamp    │
    │ lifetime_hrs │         │ imported     │
    │ lifetime_mth │         └──────────────┘
    │ warn_thresh  │
    └──────────────┘
       │1
       │
      *│
       │
    ┌──────────────┐
    │   DOWNTIME   │
    ├──────────────┤
    │ downtime_id  │
    │ machine_id   │
    │ start_time   │
    │ end_time     │
    │ duration     │
    │ description  │
    │ root_cause   │
    │ severity     │
    └──────────────┘

    ┌──────────────┐
    │   ALERTS     │
    ├──────────────┤
    │ alert_id     │
    │ machine_id   │
    │ component_id │
    │ type         │ (WARNING, CRITICAL, INFO)
    │ message      │
    │ created_at   │
    │ resolved_at  │
    └──────────────┘
```

## 5. Core Services

### 5.1 MachineService
- Create, read, update, delete machines
- Retrieve machine status and health
- Get associated components and runtime history
- Archive machines

### 5.2 ComponentService
- Manage components per machine
- Calculate component health (%)
- Determine remaining useful life (hours/days/months)
- Track installation and replacement history
- Generate replacement recommendations

### 5.3 RuntimeService
- Record machine runtime hours
- Import bulk runtime data from CSV
- Validate data integrity
- Track timestamp and source

### 5.4 DowntimeService
- Log downtime events with root cause analysis
- Calculate total downtime per machine
- Track failure patterns
- Severity classification

### 5.5 MaintenanceEngine
- Core logic for preventive maintenance
- Component health calculation: `(current_hours / lifetime_hours) * 100`
- Alert generation based on thresholds
- Maintenance recommendation generation
- Calendar-based lifecycle tracking

### 5.6 AnalyticsService
**MTBF (Mean Time Between Failures)**
```
MTBF = Total Operational Time / Number of Failures
```

**MTTR (Mean Time To Repair)**
```
MTTR = Total Downtime / Number of Failures
```

**Availability**
```
Availability = MTBF / (MTBF + MTTR) * 100%
```

**RUL (Remaining Useful Life)**
```
RUL_hours = Max(0, lifetime_hours - current_hours)
RUL_days = RUL_hours / average_daily_runtime
RUL_months = RUL_days / 30
```

**Failure Frequency**
```
Failure_Frequency = Number of Failures / Time Period
```

## 6. API Layer Design

### RESTful Principles
- Resource-oriented endpoints
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Proper status codes
- Consistent response format

### Response Format
```json
{
  "success": true,
  "data": { /* resource data */ },
  "message": "Success message",
  "timestamp": "2024-05-21T10:30:00Z"
}

{
  "success": false,
  "error": "Error code",
  "message": "Detailed error message",
  "timestamp": "2024-05-21T10:30:00Z"
}
```

### Pagination
- Implement for list endpoints
- Default page size: 20
- Include total count and current page

## 7. Data Flow Examples

### 7.1 Machine Creation Flow
```
Frontend (React) 
  → POST /api/machines (MachineCreate schema)
  → FastAPI Route Handler
  → MachineService.create_machine()
  → Machine ORM Model
  → PostgreSQL
  → Return MachineRead schema
  → React state update
```

### 7.2 Health Calculation Flow
```
Frontend requests machine health
  → GET /api/machines/{id}/health
  → API retrieves machine + components
  → MaintenanceEngine.calculate_component_health()
    - Get current runtime hours
    - Apply lifetime_hours and lifetime_months
    - Check warning thresholds
    - Generate alerts
  → Return health data (% per component, status, alerts)
  → Frontend visualizes in dashboard
```

### 7.3 Maintenance Alert Generation Flow
```
Background task (every 5 minutes)
  → Query all active machines
  → For each machine:
    - Get all components
    - Calculate health %
    - Check thresholds:
      * health > 90% → generate WARNING alert
      * health > 100% → generate CRITICAL alert
      * calendar_age > threshold → generate MAINTENANCE_DUE
    - Save alerts to database
    - Return to frontend via WebSocket (future)
```

## 8. Database Schema Strategy

### Indexing Strategy
```sql
-- High-frequency queries
CREATE INDEX idx_machines_status ON machines(status);
CREATE INDEX idx_components_machine_id ON components(machine_id);
CREATE INDEX idx_runtime_machine_timestamp ON runtime(machine_id, timestamp);
CREATE INDEX idx_downtime_machine_timestamp ON downtime(machine_id, timestamp_start);
CREATE INDEX idx_alerts_machine_resolved ON alerts(machine_id, resolved_at);
```

### Partitioning (Future Enhancement)
- Partition `runtime` by machine_id for large-scale deployments
- Partition `downtime` by month for historical data

### Archival Strategy
- Archive completed downtime records after 1 year
- Archive resolved alerts after 90 days
- Maintain KPI snapshots for trend analysis

## 9. Error Handling Strategy

### HTTP Status Codes
- **200**: Successful GET
- **201**: Successful POST (resource created)
- **204**: Successful DELETE
- **400**: Invalid request (validation error)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Resource not found
- **409**: Conflict (e.g., duplicate machine_id)
- **500**: Internal server error

### Custom Error Types
```python
class ValidationError(Exception): pass
class NotFoundError(Exception): pass
class DuplicateResourceError(Exception): pass
class InsufficientDataError(Exception): pass
class CalculationError(Exception): pass
```

## 10. Scalability Considerations

### Current (MVP)
- Single PostgreSQL instance
- Synchronous API calls
- In-memory calculations

### Phase 2 (Scale)
- Read replicas for analytics queries
- Redis caching for frequently accessed data
- Celery/APScheduler for background tasks
- Message queue for alerts

### Phase 3 (Enterprise)
- Database sharding by machine_id
- MQTT for real-time IoT data
- Elasticsearch for time-series data
- Kafka for event streaming
- ML pipeline integration

## 11. Security Considerations

### Authentication
- JWT tokens for API access
- User registration and login
- Role-based access control (RBAC)

### Data Protection
- HTTPS/TLS encryption
- Password hashing (bcrypt)
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)

### Audit Trail (Future)
- Track who made changes
- Timestamp all modifications
- Log critical operations

## 12. Deployment Architecture

```
┌─────────────────────────────────────────────┐
│          Load Balancer (nginx)              │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│FastAPI │  │FastAPI │  │FastAPI │
│Container│  │Container│  │Container│
└───┬────┘  └───┬────┘  └───┬────┘
    │           │           │
    └───────────┼───────────┘
                │
        ┌───────▼────────┐
        │   PostgreSQL   │
        │   Container    │
        └────────────────┘

        ┌────────────────┐
        │  React Build   │
        │  (Static S3)   │
        └────────────────┘
```

## 13. Future AI/ML Integration Points

The system is designed to accept AI prediction modules:

### 1. Anomaly Detection
- Real-time vibration/temperature analysis
- Deviation from baseline patterns

### 2. Failure Prediction
- Train models on historical downtime + runtime data
- Predict probability of failure in next N days
- Confidence scores

### 3. RUL Prediction
- More accurate than rule-based calculation
- Consider operating conditions
- Machine-specific patterns

### 4. Maintenance Optimization
- Optimize replacement timing
- Minimize total maintenance cost
- Reduce unplanned downtime

### Integration Points
```python
# In MaintenanceEngine
if ai_model_enabled:
    failure_probability = ml_models.predict_failure(machine, days_ahead=7)
    rul_predicted = ml_models.predict_rul(component)
    optimize_schedule = ml_models.recommend_maintenance(machine, budget)
```

## 14. Testing Strategy

### Unit Tests
- Service layer logic
- KPI calculations
- Alert generation
- Data validation

### Integration Tests
- API endpoints
- Database operations
- Service interactions

### E2E Tests
- Complete workflows
- UI interactions
- Data consistency

---

**Version**: 1.0.0
**Last Updated**: May 2024
**Architecture Pattern**: Clean Architecture
**Database**: PostgreSQL 13+
**API Framework**: FastAPI
**Frontend Framework**: React 18+
