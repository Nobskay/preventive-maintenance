# Development Notes - Implementation Guidance

## Key Implementation Patterns

### 1. Service Layer Pattern (Backend)

All business logic goes in `app/services/`. Example:

```python
# app/services/maintenance_engine.py
from app.models.machine import Machine
from app.models.component import Component
from app.schemas.component import ComponentRead
from datetime import datetime, timedelta

class MaintenanceEngine:
    @staticmethod
    def calculate_component_health(
        current_hours: float,
        lifetime_hours: int,
        months_elapsed: int,
        lifetime_months: int,
    ) -> dict:
        """Calculate component health with status"""
        health_by_hours = 0
        health_by_age = 0
        
        if lifetime_hours:
            health_by_hours = (current_hours / lifetime_hours) * 100
            
        if lifetime_months:
            health_by_age = (months_elapsed / lifetime_months) * 100
            
        health = max(health_by_hours, health_by_age)
        
        return {
            "health_percent": round(health, 2),
            "limited_by": "hours" if health_by_hours > health_by_age else "age",
            "status": "CRITICAL" if health > 90 else "WARNING" if health > 80 else "HEALTHY"
        }
    
    @staticmethod
    def calculate_rul(
        current_hours: float,
        lifetime_hours: int,
        avg_daily_hours: float,
    ) -> dict:
        """Calculate remaining useful life"""
        if not lifetime_hours or current_hours >= lifetime_hours:
            return {"hours": 0, "days": 0}
            
        remaining_hours = lifetime_hours - current_hours
        remaining_days = remaining_hours / avg_daily_hours if avg_daily_hours > 0 else 0
        
        return {
            "hours": round(remaining_hours, 2),
            "days": round(remaining_days, 0),
            "months": round(remaining_days / 30, 1)
        }

# app/services/analytics_service.py
class AnalyticsService:
    @staticmethod
    def calculate_mtbf(downtime_events: list, total_runtime: float) -> float:
        """Calculate Mean Time Between Failures"""
        failures = [d for d in downtime_events if d.is_unplanned]
        if not failures or total_runtime == 0:
            return 0
        return total_runtime / len(failures)
    
    @staticmethod
    def calculate_mttr(downtime_events: list) -> float:
        """Calculate Mean Time To Repair"""
        failures = [d for d in downtime_events if d.is_unplanned]
        if not failures:
            return 0
            
        total_downtime = sum(
            (d.timestamp_end - d.timestamp_start).total_seconds() / 3600
            for d in failures
        )
        return total_downtime / len(failures)
    
    @staticmethod
    def calculate_availability(mtbf: float, mttr: float) -> float:
        """Calculate availability percentage"""
        if mtbf + mttr == 0:
            return 0
        return (mtbf / (mtbf + mttr)) * 100
```

### 2. API Route Pattern (Backend)

```python
# app/api/machines.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.machine import MachineCreate, MachineRead, MachineUpdate
from app.models.machine import Machine
from app.services.machine_service import MachineService

router = APIRouter()

@router.post("/", response_model=MachineRead, status_code=status.HTTP_201_CREATED)
def create_machine(
    machine: MachineCreate,
    db: Session = Depends(get_db)
):
    """Create a new machine"""
    try:
        new_machine = MachineService.create_machine(machine, db)
        return new_machine
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[MachineRead])
def list_machines(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    db: Session = Depends(get_db)
):
    """List machines with pagination"""
    machines = MachineService.list_machines(db, skip=skip, limit=limit, status=status)
    return machines

@router.get("/{machine_id}", response_model=MachineRead)
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    """Get machine details"""
    machine = db.query(Machine).filter(Machine.machine_id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.get("/{machine_id}/health")
def get_machine_health(machine_id: int, db: Session = Depends(get_db)):
    """Get machine health summary"""
    machine = db.query(Machine).filter(Machine.machine_id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    health_data = MachineService.calculate_health(machine, db)
    return {
        "success": True,
        "data": health_data,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 3. Pydantic Schema Pattern (Backend)

```python
# app/schemas/machine.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class MachineBase(BaseModel):
    machine_name: str = Field(..., min_length=1, max_length=255)
    machine_type: str = Field(..., regex="^(AGV|Robotic Arm|Conveyor|CNC|Compressor|Motor|Pump|Fan|Lathe|Drill|Other)$")
    manufacturer: Optional[str] = None
    installation_date: datetime
    operating_schedule: str = "continuous"
    status: str = "active"
    notes: Optional[str] = None

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    machine_name: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class MachineRead(MachineBase):
    machine_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility
```

### 4. React Hook Pattern (Frontend)

```typescript
// frontend/src/hooks/useMachines.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { machineService } from '../services/machines';
import { Machine } from '../types/machine';

export const useMachines = () => {
  return useQuery({
    queryKey: ['machines'],
    queryFn: machineService.listMachines,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useMachine = (machineId: number) => {
  return useQuery({
    queryKey: ['machines', machineId],
    queryFn: () => machineService.getMachine(machineId),
    enabled: !!machineId,
  });
};

export const useCreateMachine = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: machineService.createMachine,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
    },
  });
};

export const useMachineHealth = (machineId: number) => {
  return useQuery({
    queryKey: ['machines', machineId, 'health'],
    queryFn: () => machineService.getMachineHealth(machineId),
    refetchInterval: 30 * 1000, // Refresh every 30 seconds
    enabled: !!machineId,
  });
};
```

### 5. React Component Pattern (Frontend)

```typescript
// frontend/src/components/machines/MachineForm.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Machine } from '../../types/machine';
import { useCreateMachine } from '../../hooks/useMachines';

interface MachineFormProps {
  onSuccess?: () => void;
}

export const MachineForm: React.FC<MachineFormProps> = ({ onSuccess }) => {
  const { register, handleSubmit, formState: { errors } } = useForm<Machine>();
  const createMachine = useCreateMachine();
  
  const onSubmit = async (data: Machine) => {
    try {
      await createMachine.mutateAsync(data);
      onSuccess?.();
    } catch (error) {
      console.error('Error creating machine:', error);
    }
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Machine Name</label>
        <input
          {...register('machine_name', { required: 'Name is required' })}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
          placeholder="AGV-001"
        />
        {errors.machine_name && (
          <p className="mt-1 text-sm text-red-600">{errors.machine_name.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium">Machine Type</label>
        <select
          {...register('machine_type', { required: 'Type is required' })}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">Select type...</option>
          <option value="AGV">AGV</option>
          <option value="Robotic Arm">Robotic Arm</option>
          <option value="CNC">CNC</option>
          <option value="Conveyor">Conveyor</option>
        </select>
      </div>
      
      <button
        type="submit"
        disabled={createMachine.isPending}
        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
      >
        {createMachine.isPending ? 'Creating...' : 'Create Machine'}
      </button>
    </form>
  );
};
```

---

## Common Implementation Challenges & Solutions

### 1. Handling Timezone Issues
```python
# Always use UTC in database
from datetime import datetime, timezone

# Store:
created_at = datetime.now(timezone.utc)

# Retrieve and convert:
local_time = utc_time.astimezone(user_timezone)
```

### 2. Calculating Health with Dual Lifetime
```python
# Component can fail by EITHER hours OR age
# Use MAX to get the most restrictive limit

health_by_hours = (current_hours / lifetime_hours) * 100 if lifetime_hours else 0
health_by_age = (months_elapsed / lifetime_months) * 100 if lifetime_months else 0

# This is the actual component health:
actual_health = max(health_by_hours, health_by_age)

# Alert generation:
if actual_health > 90:
    alert = "CRITICAL"
elif actual_health > 80:
    alert = "WARNING"
else:
    alert = "HEALTHY"
```

### 3. Efficient Time-Series Queries
```sql
-- Get latest runtime efficiently
SELECT runtime_hours FROM runtime
WHERE machine_id = $1
ORDER BY timestamp DESC
LIMIT 1;

-- Get downtime in date range
SELECT * FROM downtime
WHERE machine_id = $1
AND timestamp_start >= $2
AND timestamp_start < $3
ORDER BY timestamp_start DESC;

-- KPI calculation over time period
SELECT 
    COUNT(CASE WHEN is_unplanned THEN 1 END) as failures,
    SUM(EXTRACT(EPOCH FROM downtime_duration) / 3600) as total_downtime
FROM downtime
WHERE machine_id = $1
AND timestamp_start >= $2
AND timestamp_start < $3;
```

### 4. Error Response Standardization (FastAPI)
```python
# app/utils/responses.py
from fastapi import HTTPException
from typing import Any, Optional

class APIResponse:
    @staticmethod
    def success(data: Any, message: str = "Success"):
        return {
            "success": True,
            "data": data,
            "message": message,
        }
    
    @staticmethod
    def error(error: str, message: str, status_code: int = 400):
        raise HTTPException(
            status_code=status_code,
            detail={
                "success": False,
                "error": error,
                "message": message,
            }
        )
```

### 5. Frontend API Service Pattern
```typescript
// frontend/src/services/api.ts
import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Add token to requests
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors globally
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default API;
```

---

## Testing Strategy

### Backend Unit Test Example
```python
# backend/tests/test_services/test_maintenance_engine.py
import pytest
from app.services.maintenance_engine import MaintenanceEngine

class TestMaintenanceEngine:
    def test_component_health_calculation(self):
        """Test health calculation"""
        health = MaintenanceEngine.calculate_component_health(
            current_hours=2000,
            lifetime_hours=4000,
            months_elapsed=12,
            lifetime_months=36
        )
        assert health['health_percent'] == 50.0
        assert health['status'] == 'HEALTHY'
    
    def test_component_health_critical(self):
        """Test critical health threshold"""
        health = MaintenanceEngine.calculate_component_health(
            current_hours=3700,
            lifetime_hours=4000,
            months_elapsed=12,
            lifetime_months=36
        )
        assert health['health_percent'] > 90
        assert health['status'] == 'CRITICAL'

@pytest.fixture
def sample_machine(db):
    """Create a test machine"""
    machine = Machine(
        machine_name="TEST-AGV",
        machine_type="AGV",
        installation_date=datetime.now(),
    )
    db.add(machine)
    db.commit()
    return machine
```

---

## Database Migration Pattern

```bash
# Use Alembic for migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add components table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Performance Optimization Checklist

- [ ] Database indexes on frequently queried columns
- [ ] Connection pooling configured
- [ ] Query optimization (N+1 problem)
- [ ] API response caching (Redis)
- [ ] Frontend bundle optimization
- [ ] Image optimization
- [ ] Lazy loading for large lists
- [ ] Database query profiling

---

## Security Checklist

- [ ] JWT secret key is strong (32+ characters)
- [ ] CORS origin whitelist configured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (ORM usage)
- [ ] XSS prevention (React escaping)
- [ ] CSRF protection if needed
- [ ] Password hashing (bcrypt)
- [ ] HTTPS enforced
- [ ] Sensitive data not logged
- [ ] Dependencies regularly updated

---

## Production Deployment Checklist

- [ ] Environment variables configured
- [ ] Database backups enabled
- [ ] Error tracking (Sentry) configured
- [ ] Logging aggregation set up
- [ ] Monitoring and alerting configured
- [ ] Health checks implemented
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] SSL certificates installed
- [ ] Database indexes created
- [ ] API documentation updated
- [ ] Tests passing (100% critical paths)

---

**Version**: 1.0.0  
**Last Updated**: May 2024
