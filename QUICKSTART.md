# Quick Start Guide

## 🚀 Get Running in 5 Minutes (Docker)

### Prerequisites
- Docker & Docker Compose installed
- Git installed

### Steps

```bash
# 1. Clone and navigate
git clone <repository-url>
cd predictive-maintenance

# 2. Start all services
docker-compose -f docker/docker-compose.yml up -d

# 3. Access the application:

# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
# pgAdmin:   http://localhost:5050 (dev only)
```

### First Login
- **Username**: admin
- **Email**: admin@maintainiq.local
- **Password**: admin123

### Sample Data
Docker demo startup automatically seeds deterministic plant data when `AUTO_SEED_DATA=true`:
- `AGV-01`, `CNC-02`, and `Conveyor-03`
- Motor bearing, battery, wheel assembly, spindle bearing, cooling pump, belt drive, gearbox, and roller motor components
- 90 days of runtime history
- Downtime events, maintenance history, warning/critical alerts, recommendations, and system users

---

## 🔧 Local Development (Without Docker)

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL details

# Apply migrations
alembic upgrade head

# Optional: load realistic sample data
python -m app.seed_data

# Run server
uvicorn app.main:app --reload
```

Access API: `http://localhost:8000`

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start dev server
npm run dev
```

Access Frontend: `http://localhost:5173`

---

## 📝 Key Commands

### Docker Commands
```bash
# Start services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose -f docker/docker-compose.yml down

# Rebuild images
docker-compose -f docker/docker-compose.yml build
```

### Backend Commands
```bash
# Run tests
pytest

# Apply database migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "Describe schema change"

# Format code
black app/

# Check types
mypy app/

# Run linting
flake8 app/
```

### Frontend Commands
```bash
# Run tests
npm test

# Build for production
npm run build

# Lint code
npm run lint
```

---

## 📊 Exploring the System

### 1. Create a Machine
```bash
curl -X POST http://localhost:8000/api/v1/machines \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_name": "CNC-002",
    "machine_type": "CNC",
    "manufacturer": "Haas",
    "installation_date": "2024-01-01",
    "operating_schedule": "continuous",
    "status": "active"
  }'
```

### 2. Add a Component
```bash
curl -X POST http://localhost:8000/api/v1/components \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": 1,
    "component_name": "Spindle Motor",
    "component_type": "motor",
    "lifetime_hours": 8000,
    "lifetime_months": 60,
    "warning_threshold_percent": 80,
    "critical_threshold_percent": 90,
    "replacement_cost": 15000,
    "installation_date": "2024-01-01"
  }'
```

### 3. Record Runtime
```bash
curl -X POST http://localhost:8000/api/v1/runtime \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": 1,
    "runtime_hours": 500,
    "delta_hours": 50,
    "timestamp": "2026-05-21T08:00:00Z",
    "data_source": "manual"
  }'
```

### 4. Log Downtime
```bash
curl -X POST http://localhost:8000/api/v1/downtime \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": 1,
    "timestamp_start": "2024-05-21T10:00:00Z",
    "timestamp_end": "2024-05-21T10:45:00Z",
    "issue_description": "Motor overheating",
    "root_cause": "Coolant system malfunction",
    "corrective_action": "Flushed and refilled coolant",
    "severity_level": "high",
    "is_unplanned": true
  }'
```

### 5. View Dashboard
Open http://localhost:3000/dashboard in browser

---

## 🐛 Troubleshooting

### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs pred_maintenance_db

# Verify connection string
psql postgresql://app_user:app_password@localhost:5432/predictive_maintenance
```

### Port Already in Use
```bash
# Change ports in docker-compose.yml
# Or kill processes using ports:
# Linux/Mac:
lsof -i :3000  # find process on port 3000
kill -9 <PID>  # kill the process

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Build Errors
```bash
# Clean and rebuild
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

### API Documentation Not Loading
- Ensure `ENABLE_DOCS=true` in .env
- Restart backend service
- Check browser cache

---

## 📚 Next Steps

1. **Explore the API**
   - Open http://localhost:8000/docs
   - Try endpoints with Swagger UI

2. **Create Test Data**
   - Add machines and components
   - Import sample CSV data
   - Log downtime events

3. **Review Architecture**
   - Read [ARCHITECTURE.md](docs/ARCHITECTURE.md)
   - Check [API_DESIGN.md](docs/API_DESIGN.md)

4. **Study the Code**
   - Backend: `backend/app/`
   - Frontend: `frontend/src/`

5. **Extend Features**
   - Add new API endpoints
   - Create new dashboard pages
   - Implement ML predictions

---

## 📞 Support

- **Issues**: Check [GitHub Issues](https://github.com/yourname/predictive-maintenance/issues)
- **Docs**: Read `/docs/` folder
- **API**: Open `/docs` endpoint for Swagger
- **Examples**: Check `data/` folder for sample files

---

**Enjoy! 🚀**

Questions? Check the documentation or create an issue.
