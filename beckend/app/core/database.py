"""
Database connection and session management
Supports PostgreSQL (production) and SQLite (development fallback)
"""
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Determine database URL - fallback to SQLite if PostgreSQL not available
def _get_engine_url():
    """Get database URL, fallback to SQLite for easy development"""
    db_url = settings.sqlalchemy_database_url

    # If using PostgreSQL, test if it's available
    if db_url.startswith("postgresql"):
        try:
            import psycopg2
            # Try to connect
            test_engine = create_engine(db_url)
            with test_engine.connect() as conn:
                conn.execute(__import__('sqlalchemy').text("SELECT 1"))
            test_engine.dispose()
            logger.info("Using PostgreSQL database")
            return db_url
        except Exception as e:
            logger.warning(f"PostgreSQL not available ({e}), falling back to SQLite")

    # Fallback to SQLite
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "maintainiq.db")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    logger.info(f"Using SQLite database: {sqlite_path}")
    return f"sqlite:///{sqlite_path}"

# Create database engine
engine_url = _get_engine_url()

if engine_url.startswith("sqlite"):
    # SQLite doesn't support connection pooling
    engine = create_engine(
        engine_url,
        echo=settings.DB_ECHO,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL with connection pooling
    engine = create_engine(
        engine_url,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        poolclass=pool.QueuePool,
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """
    Dependency for getting database session in routes
    Usage:
        def my_route(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_database_connection():
    """Test database connectivity"""
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
