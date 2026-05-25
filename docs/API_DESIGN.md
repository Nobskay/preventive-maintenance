# API Endpoint Design - Predictive Maintenance System

## Base URL
```
http://localhost:8000/api/v1
```

## Current MVP Endpoint Map

The implemented API uses a consistent `ApiResponse` envelope and exposes these production MVP routes:

### Machines
- `GET /machines/`
- `POST /machines/`
- `GET /machines/{machine_id}`
- `PUT /machines/{machine_id}`
- `DELETE /machines/{machine_id}`
- `GET /machines/{machine_id}/health`

### Components
- `GET /components/?machine_id={machine_id}`
- `POST /components/`
- `GET /components/{component_id}`
- `PUT /components/{component_id}`
- `DELETE /components/{component_id}`
- `GET /components/{component_id}/health`

Component lifecycle fields:

```json
{
  "machine_id": 1,
  "component_name": "Motor Bearing",
  "component_type": "bearing",
  "lifetime_hours": 5000,
  "lifetime_months": 24,
  "installed_runtime_hours": 0,
  "warning_threshold_percent": 90,
  "critical_threshold_percent": 100,
  "installation_date": "2024-06-10",
  "last_replacement_date": "2024-06-10",
  "maintenance_sop": "Inspect vibration trend, lubricate bearing housing, replace if axial play is detected."
}
```

Component health response includes both condition and lifecycle consumption:

```json
{
  "health_percent": 6.0,
  "life_consumed_percent": 94.0,
  "health_status": "WARNING",
  "maintenance_due_status": "DUE_SOON",
  "remaining_useful_life_hours": 300,
  "used_runtime_hours": 4700
}
```

### Runtime
- `GET /runtime/{machine_id}`
- `GET /runtime/{machine_id}/latest`
- `POST /runtime/`
- `POST /runtime/batch`
- `POST /runtime/{machine_id}/import-csv`

### Downtime
- `GET /downtime/`
- `GET /downtime/trends/`
- `POST /downtime/`
- `GET /downtime/{downtime_id}`
- `PUT /downtime/{downtime_id}`
- `DELETE /downtime/{downtime_id}`

### Alerts
- `GET /alerts/`
- `POST /alerts/`
- `POST /alerts/generate`
- `GET /alerts/{alert_id}`
- `POST /alerts/{alert_id}/resolve`

### Maintenance Events
- `GET /maintenance-events/`
- `POST /maintenance-events/`
- `GET /maintenance-events/{maintenance_event_id}`
- `PUT /maintenance-events/{maintenance_event_id}`
- `DELETE /maintenance-events/{maintenance_event_id}`

Maintenance events represent completed work order history and are used as the predictive-maintenance training foundation:

```json
{
  "machine_id": 1,
  "component_id": 1,
  "event_type": "lubrication",
  "trigger_source": "condition_based",
  "work_order_code": "WO-AGV-0101",
  "performed_at": "2026-03-01T08:00:00",
  "duration_hours": 1.5,
  "technician": "Senior Maintenance Technician",
  "action_taken": "Lubricated motor bearing housing and captured vibration baseline.",
  "parts_replaced": "High-temp bearing grease"
}
```

### Dashboard and KPI
- `GET /dashboard/summary`
- `GET /dashboard/kpis`
- `GET /dashboard/kpis/{machine_id}`
- `GET /dashboard/machine-health`
- `GET /dashboard/downtime-trends`
- `GET /dashboard/recommendations`
- `POST /dashboard/generate-recommendations`

The examples below are retained as design reference, but the endpoint map above is the current implementation contract.

## Authentication
JWT scaffolding exists, but MVP endpoints are currently open for demo and portfolio usage. Production hardening should enforce JWT/RBAC on all endpoints except `/auth/*`:
```
Authorization: Bearer {token}
```

---

## 1. Authentication Endpoints

### 1.1 Register User
```
POST /auth/register
Content-Type: application/json

{
  "username": "tech1",
  "email": "tech1@company.com",
  "password": "secure_password",
  "full_name": "John Technician",
  "role": "technician"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "user_id": 1,
    "username": "tech1",
    "email": "tech1@company.com",
    "role": "technician"
  },
  "message": "User created successfully"
}
```

### 1.2 Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "tech1",
  "password": "secure_password"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 3600
  },
  "message": "Login successful"
}
```

### 1.3 Refresh Token
```
POST /auth/refresh
Authorization: Bearer {refresh_token}

Response: 200 OK
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "token_type": "bearer"
  }
}
```

---

## 2. Machine Endpoints

### 2.1 Create Machine
```
POST /machines
Content-Type: application/json
Authorization: Bearer {token}

{
  "machine_name": "AGV-001",
  "machine_type": "AGV",
  "manufacturer": "Mobile Industrial Robots",
  "installation_date": "2023-01-15",
  "operating_schedule": "continuous",
  "status": "active",
  "notes": "Main warehouse AGV"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "machine_id": 1,
    "machine_name": "AGV-001",
    "machine_type": "AGV",
    "manufacturer": "Mobile Industrial Robots",
    "installation_date": "2023-01-15",
    "operating_schedule": "continuous",
    "status": "active",
    "created_at": "2024-05-21T10:30:00Z",
    "updated_at": "2024-05-21T10:30:00Z"
  },
  "message": "Machine created successfully"
}
```

### 2.2 Get All Machines
```
GET /machines?page=1&limit=20&status=active
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "machines": [
      {
        "machine_id": 1,
        "machine_name": "AGV-001",
        "machine_type": "AGV",
        "status": "active",
        "installation_date": "2023-01-15",
        "created_at": "2024-05-21T10:30:00Z"
      },
      ...
    ],
    "pagination": {
      "current_page": 1,
      "limit": 20,
      "total_count": 45,
      "total_pages": 3
    }
  },
  "message": "Machines retrieved"
}
```

### 2.3 Get Machine Details
```
GET /machines/{machine_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "machine_id": 1,
    "machine_name": "AGV-001",
    "machine_type": "AGV",
    "manufacturer": "Mobile Industrial Robots",
    "installation_date": "2023-01-15",
    "operating_schedule": "continuous",
    "status": "active",
    "created_at": "2024-05-21T10:30:00Z",
    "updated_at": "2024-05-21T10:30:00Z",
    "components": [
      {
        "component_id": 1,
        "component_name": "Main Battery",
        "component_type": "battery",
        "health_percent": 65.5,
        "health_status": "HEALTHY"
      }
    ],
    "current_runtime_hours": 2450.5
  }
}
```

### 2.4 Update Machine
```
PUT /machines/{machine_id}
Authorization: Bearer {token}

{
  "machine_name": "AGV-001",
  "status": "maintenance"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "machine_id": 1,
    "machine_name": "AGV-001",
    "status": "maintenance",
    "updated_at": "2024-05-21T11:00:00Z"
  }
}
```

### 2.5 Delete Machine
```
DELETE /machines/{machine_id}
Authorization: Bearer {token}

Response: 204 No Content
```

### 2.6 Get Machine Health Summary
```
GET /machines/{machine_id}/health
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "machine_id": 1,
    "machine_name": "AGV-001",
    "overall_health_percent": 75.3,
    "overall_health_status": "HEALTHY",
    "components_health": [
      {
        "component_id": 1,
        "component_name": "Main Battery",
        "health_percent": 65.5,
        "health_status": "HEALTHY",
        "remaining_useful_life_hours": 1234,
        "remaining_useful_life_days": 51
      },
      {
        "component_id": 2,
        "component_name": "Motor Bearing",
        "health_percent": 85.2,
        "health_status": "WARNING",
        "remaining_useful_life_hours": 320,
        "remaining_useful_life_days": 13
      }
    ],
    "active_alerts": 2
  }
}
```

### 2.7 Get Machine KPIs
```
GET /machines/{machine_id}/kpi
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "machine_id": 1,
    "machine_name": "AGV-001",
    "mtbf_hours": 1250.5,
    "mttr_hours": 2.75,
    "availability_percent": 99.78,
    "failure_frequency": 0.32,
    "total_failures": 4,
    "total_uptime_hours": 8760,
    "total_downtime_hours": 11,
    "period": "last_30_days"
  }
}
```

---

## 3. Component Endpoints

### 3.1 Create Component
```
POST /components
Content-Type: application/json
Authorization: Bearer {token}

{
  "machine_id": 1,
  "component_name": "Main Battery Pack",
  "component_type": "battery",
  "lifetime_hours": 4000,
  "lifetime_months": 36,
  "warning_threshold_percent": 80,
  "critical_threshold_percent": 90,
  "replacement_cost": 5000.00,
  "maintenance_sop": "Follow manufacturer guidelines for replacement",
  "installation_date": "2023-01-15"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "component_id": 1,
    "machine_id": 1,
    "component_name": "Main Battery Pack",
    "component_type": "battery",
    "lifetime_hours": 4000,
    "health_percent": 61.25,
    "health_status": "HEALTHY",
    "created_at": "2024-05-21T10:30:00Z"
  }
}
```

### 3.2 Get Components for Machine
```
GET /machines/{machine_id}/components
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "components": [
      {
        "component_id": 1,
        "component_name": "Main Battery Pack",
        "component_type": "battery",
        "health_percent": 61.25,
        "health_status": "HEALTHY",
        "remaining_hours": 1525,
        "remaining_months": 13
      }
    ]
  }
}
```

### 3.3 Update Component
```
PUT /components/{component_id}
Authorization: Bearer {token}

{
  "last_replacement_date": "2024-05-21",
  "installation_date": "2024-05-21"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "component_id": 1,
    "health_percent": 0,
    "health_status": "HEALTHY",
    "last_replacement_date": "2024-05-21"
  }
}
```

### 3.4 Delete Component
```
DELETE /components/{component_id}
Authorization: Bearer {token}

Response: 204 No Content
```

---

## 4. Runtime Endpoints

### 4.1 Record Runtime Manually
```
POST /runtime
Content-Type: application/json
Authorization: Bearer {token}

{
  "machine_id": 1,
  "runtime_hours": 2450.5,
  "delta_hours": 10.5,
  "data_source": "manual",
  "notes": "Recorded from machine display panel"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "runtime_id": 1001,
    "machine_id": 1,
    "runtime_hours": 2450.5,
    "delta_hours": 10.5,
    "timestamp": "2024-05-21T10:30:00Z",
    "data_source": "manual"
  }
}
```

### 4.2 Import Runtime Data (CSV)
```
POST /runtime/import
Content-Type: multipart/form-data
Authorization: Bearer {token}

Files:
- file: [CSV file]
- machine_id: 1
- data_source: csv_import

CSV Format:
timestamp,runtime_hours,delta_hours
2024-05-20T10:00:00,2440,0
2024-05-20T14:00:00,2445,5
2024-05-20T18:00:00,2450,5
2024-05-21T10:30:00,2450.5,0.5

Response: 200 OK
{
  "success": true,
  "data": {
    "imported_count": 4,
    "skipped_count": 0,
    "errors": []
  },
  "message": "Runtime data imported successfully"
}
```

### 4.3 Get Runtime History
```
GET /machines/{machine_id}/runtime?days=30&limit=100
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "runtime_history": [
      {
        "runtime_id": 1001,
        "machine_id": 1,
        "runtime_hours": 2450.5,
        "delta_hours": 10.5,
        "timestamp": "2024-05-21T10:30:00Z",
        "data_source": "manual"
      },
      ...
    ],
    "summary": {
      "current_runtime": 2450.5,
      "total_delta": 150.5,
      "average_daily_hours": 5.02,
      "sample_count": 25
    }
  }
}
```

---

## 5. Downtime Endpoints

### 5.1 Log Downtime Event
```
POST /downtime
Content-Type: application/json
Authorization: Bearer {token}

{
  "machine_id": 1,
  "timestamp_start": "2024-05-21T09:00:00Z",
  "timestamp_end": "2024-05-21T09:45:00Z",
  "issue_description": "Motor bearing overheating",
  "root_cause": "Insufficient lubrication",
  "corrective_action": "Applied bearing lubricant and monitored temperature",
  "severity_level": "high",
  "component_affected": 2,
  "is_unplanned": true
}

Response: 201 Created
{
  "success": true,
  "data": {
    "downtime_id": 5001,
    "machine_id": 1,
    "timestamp_start": "2024-05-21T09:00:00Z",
    "timestamp_end": "2024-05-21T09:45:00Z",
    "downtime_duration": "00:45:00",
    "severity_level": "high",
    "root_cause": "Insufficient lubrication"
  }
}
```

### 5.2 Get Downtime History
```
GET /machines/{machine_id}/downtime?days=90&sort=recent
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "downtime_events": [
      {
        "downtime_id": 5001,
        "machine_id": 1,
        "timestamp_start": "2024-05-21T09:00:00Z",
        "timestamp_end": "2024-05-21T09:45:00Z",
        "downtime_duration": "00:45:00",
        "issue_description": "Motor bearing overheating",
        "severity_level": "high",
        "is_unplanned": true
      }
    ],
    "summary": {
      "total_downtime_hours": 11.25,
      "total_events": 8,
      "average_duration_minutes": 84.375,
      "critical_events": 1,
      "high_events": 3
    }
  }
}
```

### 5.3 Update Downtime Event
```
PUT /downtime/{downtime_id}
Authorization: Bearer {token}

{
  "root_cause": "Worn bearing requiring replacement",
  "corrective_action": "Replaced bearing assembly, tested, and returned to service"
}

Response: 200 OK
```

### 5.4 Resolve Downtime Event
```
POST /downtime/{downtime_id}/resolve
Authorization: Bearer {token}

{
  "resolution_notes": "Bearing replaced successfully, machine operational"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "downtime_id": 5001,
    "status": "resolved",
    "resolved_at": "2024-05-21T14:30:00Z"
  }
}
```

---

## 6. Alerts Endpoints

### 6.1 Get Active Alerts
```
GET /alerts?machine_id=1&is_active=true&severity=critical
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "alerts": [
      {
        "alert_id": 9001,
        "machine_id": 1,
        "component_id": 2,
        "alert_type": "CRITICAL",
        "alert_severity": "critical",
        "message": "Motor bearing health exceeds critical threshold (92%)",
        "additional_data": {
          "component_name": "Motor Bearing",
          "health_percent": 92,
          "remaining_hours": 160
        },
        "created_at": "2024-05-21T10:00:00Z",
        "is_active": true
      }
    ],
    "summary": {
      "total_active": 3,
      "critical": 1,
      "warning": 2
    }
  }
}
```

### 6.2 Resolve Alert
```
POST /alerts/{alert_id}/resolve
Authorization: Bearer {token}

{
  "resolution_notes": "Motor bearing replaced successfully"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "alert_id": 9001,
    "is_active": false,
    "resolved_at": "2024-05-21T14:30:00Z"
  }
}
```

---

## 7. Maintenance Recommendations Endpoints

### 7.1 Get Recommendations
```
GET /recommendations?machine_id=1&status=open&urgency=urgent
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "recommendation_id": 10001,
        "machine_id": 1,
        "component_id": 2,
        "recommendation_type": "replacement",
        "description": "Replace motor bearing within 160 operational hours (2-3 days)",
        "urgency": "urgent",
        "estimated_cost": 250.00,
        "estimated_duration_hours": 4,
        "status": "open",
        "created_at": "2024-05-21T10:00:00Z"
      }
    ]
  }
}
```

### 7.2 Create Recommendation
```
POST /recommendations
Authorization: Bearer {token}

{
  "machine_id": 1,
  "component_id": 2,
  "recommendation_type": "inspection",
  "description": "Vibration analysis inspection recommended",
  "urgency": "high",
  "estimated_cost": 500.00,
  "estimated_duration_hours": 2,
  "recommended_by_system": "user"
}

Response: 201 Created
```

### 7.3 Schedule Recommendation
```
PUT /recommendations/{recommendation_id}
Authorization: Bearer {token}

{
  "status": "scheduled",
  "scheduled_date": "2024-05-25"
}

Response: 200 OK
```

---

## 8. Dashboard Endpoints

### 8.1 Get Dashboard Summary
```
GET /dashboard/summary
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "total_machines": 45,
    "active_machines": 42,
    "machines_in_maintenance": 3,
    "total_components": 320,
    "active_alerts": 12,
    "critical_alerts": 2,
    "warning_alerts": 10,
    "avg_availability": 99.2,
    "avg_mtbf": 1150.5,
    "avg_mttr": 2.3,
    "scheduled_maintenance_today": 1,
    "overdue_recommendations": 4
  }
}
```

### 8.2 Get Machines Health Overview
```
GET /dashboard/machines-health
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "healthy_machines": 40,
    "warning_machines": 4,
    "critical_machines": 1,
    "machines_by_health": [
      {
        "machine_id": 1,
        "machine_name": "AGV-001",
        "health_status": "HEALTHY",
        "health_percent": 75,
        "critical_components": 0,
        "warning_components": 1
      }
    ]
  }
}
```

### 8.3 Get Downtime Trends
```
GET /dashboard/downtime-trends?period=30days
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "trend_data": [
      {
        "date": "2024-05-20",
        "total_downtime_hours": 2.5,
        "downtime_events": 2,
        "avg_duration_minutes": 75
      },
      {
        "date": "2024-05-21",
        "total_downtime_hours": 0.75,
        "downtime_events": 1,
        "avg_duration_minutes": 45
      }
    ],
    "summary": {
      "total_period_downtime": 45.25,
      "total_period_events": 28
    }
  }
}
```

### 8.4 Get Failure Frequency
```
GET /dashboard/failure-frequency?period=month
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "frequency_by_machine": [
      {
        "machine_id": 1,
        "machine_name": "AGV-001",
        "failures_per_week": 0.25,
        "total_failures": 4,
        "trend": "stable"
      }
    ]
  }
}
```

---

## 9. Analytics Endpoints

### 9.1 Get KPI History
```
GET /analytics/kpi-history/{machine_id}?period=3months&metric=availability
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "kpi_snapshots": [
      {
        "snapshot_date": "2024-04-21",
        "mtbf_hours": 1100,
        "mttr_hours": 2.5,
        "availability_percent": 99.75,
        "failure_frequency": 0.33
      }
    ]
  }
}
```

---

## Error Response Format

```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Field 'machine_name' is required",
  "details": {
    "field": "machine_name",
    "constraint": "required"
  },
  "timestamp": "2024-05-21T10:30:00Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR` (400)
- `UNAUTHORIZED` (401)
- `FORBIDDEN` (403)
- `NOT_FOUND` (404)
- `DUPLICATE_RESOURCE` (409)
- `INTERNAL_SERVER_ERROR` (500)

---

**Version**: 1.0.0
**Last Updated**: May 2024
