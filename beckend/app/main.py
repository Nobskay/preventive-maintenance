"""
Predictive Maintenance System - FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.database import engine, SessionLocal
from app.models.base import Base
from app import models  # noqa: F401 - register ORM metadata
from app.api import machines, components, runtime, downtime, alerts, auth, dashboard, maintenance

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="Industrial Predictive Maintenance & Reliability Monitoring System",
    version=settings.API_VERSION,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(machines.router, prefix="/api/v1/machines", tags=["Machines"])
app.include_router(components.router, prefix="/api/v1/components", tags=["Components"])
app.include_router(runtime.router, prefix="/api/v1/runtime", tags=["Runtime"])
app.include_router(downtime.router, prefix="/api/v1/downtime", tags=["Downtime"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(maintenance.router, prefix="/api/v1/maintenance-events", tags=["Maintenance Events"])


@app.on_event("startup")
def startup_event():
    """Initialize database tables and seed data on startup"""
    if settings.AUTO_CREATE_TABLES:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created.")

    if settings.AUTO_SEED_DATA:
        _auto_seed()


def _auto_seed():
    """Seed database with sample data if empty"""
    from app.models.machine import Machine
    from app.seed_data import run as seed_run

    db = SessionLocal()
    try:
        if db.query(Machine).first():
            logger.info("Database already has data; skipping seed.")
            return
        logger.info("Seeding database with sample data...")
        seed_run()
        logger.info("Database seeded successfully.")
    except Exception as e:
        logger.error(f"Seed failed: {e}")
    finally:
        db.close()


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.API_VERSION}


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": "/api/v1",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal Server Error", "message": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
    )
