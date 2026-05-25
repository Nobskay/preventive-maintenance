# Predictive Maintenance & Reliability Monitoring System

![Platform](https://img.shields.io/badge/platform-Industrial%20IoT-blue)
![Status](https://img.shields.io/badge/status-Active%20Development-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.104%2B-blue)
![React](https://img.shields.io/badge/react-18%2B-blue)

A modern, enterprise-grade web-based predictive maintenance and reliability monitoring platform designed for manufacturing environments including AGV systems, robotics, conveyors, CNC machines, compressors, and industrial automation equipment.

## 🎯 Features

### Core Capabilities
- **Machine Management**: Track any industrial equipment with comprehensive lifecycle management
- **Component Management**: Monitor replaceable/serviceable components with dual-lifetime tracking (hours + calendar age)
- **Runtime Tracking**: Record and import machine operational hours with CSV support
- **Downtime Logging**: Comprehensive failure analysis with root cause tracking
- **Preventive Maintenance Engine**: Rule-based maintenance logic with health calculations
- **Real-time Alerts**: Automatic alerting for component health thresholds
- **Industrial KPIs**: Calculate and track MTBF, MTTR, Availability, and more
- **Maintenance Recommendations**: AI-ready recommendation system (future ML integration)
- **Dashboard & Analytics**: Modern industrial-style dashboard with KPI visualizations

### Technical Highlights
- **Clean Architecture**: Modular, scalable, and maintainable codebase
- **RESTful API**: Production-ready FastAPI with OpenAPI documentation
- **PostgreSQL Database**: Enterprise-grade data storage with proper indexing
- **React Frontend**: Modern, responsive UI with TailwindCSS
- **Docker Ready**: Full containerization for easy deployment
- **RBAC**: Role-based access control (Admin, Manager, Technician, Viewer)
- **Future-Ready**: Designed for AI/ML integration and IoT connectivity

## 📋 Tech Stack

### Backend
- **Python 3.11+** - Programming language
- **FastAPI 0.104+** - Web framework
- **SQLAlchemy 2.0+** - ORM
- **PostgreSQL 13+** - Database
- **Pydantic 2.0+** - Data validation
- **JWT** - Authentication

### Frontend
- **React 18+** - UI framework
- **TypeScript 5.0+** - Type safety
- **TailwindCSS 3.3+** - Styling
- **Recharts 2.10+** - Charts and visualizations
- **React Query 5.0+** - Server state management
- **Vite 5.0+** - Build tool

### DevOps
- **Docker & Docker Compose** - Containerization
- **PostgreSQL 15** - Database container
- **Nginx** - Reverse proxy
- **Render/Railway** - Platform as a Service

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- PostgreSQL 13+ (for local development)
- Git

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repository_url>
cd predictive-maintenance

# Create .env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit .env files if needed (local defaults should work)

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Services will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# pgAdmin (dev): http://localhost:5050
```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Initialize database
psql -U postgres -d postgres -a -f ../database/SCHEMA.sql

# Run FastAPI server
uvicorn app.main:app --reload
# API available at: http://localhost:8000
```

#### Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
# Frontend available at: http://localhost:5173
```

## 📊 Database Schema

The system includes comprehensive database schema with:

- **Machines Table**: Core equipment data
- **Components Table**: Replaceable/serviceable parts
- **Runtime Table**: Time-series operational hours
- **Downtime Table**: Failure and maintenance events
- **Alerts Table**: Real-time alert tracking
- **Recommendations Table**: Maintenance recommendations
- **KPI Snapshots**: Historical KPI data for trends
- **Users Table**: RBAC and authentication
- **Audit Logs**: Compliance and audit trail

See [SCHEMA.sql](database/SCHEMA.sql) for detailed schema design.

## 🔌 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Key Endpoints

#### Authentication
```
POST   /auth/register          - Register new user
POST   /auth/login             - User login
POST   /auth/refresh           - Refresh JWT token
```

#### Machines
```
POST   /machines               - Create machine
GET    /machines               - List machines (paginated)
GET    /machines/{id}          - Get machine details
PUT    /machines/{id}          - Update machine
DELETE /machines/{id}          - Delete machine
GET    /machines/{id}/health   - Get machine health
GET    /machines/{id}/kpi      - Get machine KPIs
```

#### Components
```
POST   /components             - Create component
GET    /machines/{id}/components - List machine components
PUT    /components/{id}        - Update component
DELETE /components/{id}        - Delete component
```

#### Runtime
```
POST   /runtime                - Record runtime manually
POST   /runtime/import         - Import runtime data (CSV)
GET    /machines/{id}/runtime  - Get runtime history
```

#### Downtime
```
POST   /downtime               - Log downtime event
GET    /machines/{id}/downtime - Get downtime history
PUT    /downtime/{id}          - Update downtime event
```

#### Dashboard
```
GET    /dashboard/summary      - Dashboard KPI summary
GET    /dashboard/machines-health - Machines health overview
GET    /dashboard/downtime-trends - Downtime trends
```

Full API documentation available at `http://localhost:8000/docs` (Swagger UI)

## 📈 KPI Calculations

### MTBF (Mean Time Between Failures)
```
MTBF = Total Operational Time / Number of Failures
```

### MTTR (Mean Time To Repair)
```
MTTR = Total Downtime / Number of Failures
```

### Availability
```
Availability = MTBF / (MTBF + MTTR) × 100%
```

### Component Health
```
Health % = MAX(
  (Current Hours / Lifetime Hours) × 100,
  (Months Elapsed / Lifetime Months) × 100
)
```

### Remaining Useful Life
```
RUL (hours) = MAX(0, Lifetime Hours - Current Hours)
RUL (days) = RUL Hours / Average Daily Runtime
```

## 🏗️ Project Structure

```
predictive-maintenance/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── api/                      # Route handlers
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── services/                 # Business logic
│   │   ├── core/                     # Configuration & database
│   │   ├── utils/                    # Utilities & helpers
│   │   └── main.py                   # FastAPI app entry
│   ├── tests/                        # Unit & integration tests
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Backend container
│   └── .env.example                  # Environment template
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/               # Reusable components
│   │   ├── pages/                    # Page components
│   │   ├── services/                 # API client services
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── types/                    # TypeScript types
│   │   └── App.tsx                   # Main app component
│   ├── public/                       # Static assets
│   ├── package.json                  # Node dependencies
│   ├── Dockerfile                    # Frontend container
│   ├── vite.config.ts                # Vite config
│   ├── tailwind.config.js            # TailwindCSS config
│   └── .env.example                  # Environment template
│
├── database/
│   ├── SCHEMA.sql                    # PostgreSQL schema
│   └── migrations/                   # Database migrations
│
├── docker/
│   ├── docker-compose.yml            # Full stack composition
│   ├── Dockerfile.backend            # Backend image
│   └── Dockerfile.frontend           # Frontend image
│
├── docs/
│   ├── ARCHITECTURE.md               # System architecture
│   ├── API_DESIGN.md                 # API endpoint design
│   ├── IMPLEMENTATION_PLAN.md        # Implementation guide
│   └── DEPLOYMENT.md                 # Deployment instructions
│
├── data/
│   ├── sample_runtime_data.csv       # Sample data for testing
│   └── sample_machines.json          # Sample machine config
│
└── README.md                         # This file
```

## 🔐 Authentication & Authorization

### Supported Roles
- **Admin**: Full system access
- **Manager**: Create/edit machines, view all reports
- **Technician**: Create/edit maintenance records
- **Viewer**: Read-only access

### JWT Authentication
All API endpoints (except `/auth/*`) require JWT token in header:
```
Authorization: Bearer {token}
```

## 📊 Sample Data

Sample industrial data is provided for testing:

```bash
# Import sample runtime data
curl -X POST http://localhost:8000/api/v1/runtime/import \
  -F "file=@data/sample_runtime_data.csv" \
  -F "machine_id=1" \
  -H "Authorization: Bearer {token}"
```

See `data/` directory for sample datasets.

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_machines.py -v
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm run test

# Watch mode
npm run test:ui
```

## 📦 Building & Deployment

### Local Build
```bash
# Build backend image
docker build -t predictive-maintenance-api:latest ./backend

# Build frontend image
docker build -t predictive-maintenance-ui:latest ./frontend

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up
```

### Deploy to Render

```bash
# 1. Create PostgreSQL database on Render
# 2. Create two Web Services:
#    - Backend: repo/backend, Dockerfile, PORT=8000
#    - Frontend: repo/frontend, Dockerfile, PORT=3000

# 3. Set environment variables for each service
# 4. Deploy from GitHub

# 5. Update frontend .env with production backend URL
VITE_API_URL=https://your-api.onrender.com/api/v1
```

### Deploy to Railway

```bash
# 1. Install Railway CLI
npm i -g railway

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Create services for backend, frontend, and PostgreSQL
# 5. Deploy
railway up
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 🚀 Future Enhancements

### Phase 2: AI/ML Integration
- [ ] Anomaly detection (vibration, temperature)
- [ ] Failure prediction using ML models
- [ ] Optimized RUL prediction
- [ ] Maintenance cost optimization

### Phase 3: IoT Integration
- [ ] MQTT support for real-time sensor data
- [ ] ESP32 integration examples
- [ ] PLC connectivity
- [ ] SCADA system integration

### Phase 4: Advanced Features
- [ ] Work order management system
- [ ] Spare parts inventory tracking
- [ ] Email/WhatsApp notifications
- [ ] Mobile app (React Native)
- [ ] Real-time dashboards (WebSocket)
- [ ] Multi-tenant support

### Phase 5: Enterprise
- [ ] Advanced RBAC and permissions
- [ ] Audit logging and compliance
- [ ] Data encryption at rest
- [ ] Multi-region deployment
- [ ] Advanced analytics and BI integration

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design patterns
- [API_DESIGN.md](docs/API_DESIGN.md) - Complete API specification
- [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) - Development roadmap
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Production deployment guide

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

For issues, questions, or suggestions:
1. Check [Existing Issues](https://github.com/yourname/predictive-maintenance/issues)
2. [Create New Issue](https://github.com/yourname/predictive-maintenance/issues/new)
3. Review [Documentation](docs/)

## 👨‍💼 Author

Built as a portfolio project demonstrating modern full-stack industrial software development.

- **Full-Stack Development**: React + FastAPI + PostgreSQL
- **Software Architecture**: Clean Architecture principles
- **Industrial Expertise**: Real manufacturing workflows
- **DevOps**: Docker, containerization, cloud deployment

## 🙏 Acknowledgments

This project implements best practices from:
- Clean Architecture (Robert C. Martin)
- FastAPI best practices
- React patterns and hooks
- PostgreSQL design principles
- Industrial maintenance standards (ISO 13373)

---

**Status**: Active Development  
**Latest Release**: v1.0.0  
**Last Updated**: May 2024

**Remember**: The system is designed for quality over quantity. Apply to roles where there is genuine fit. Every application should represent your best work.
