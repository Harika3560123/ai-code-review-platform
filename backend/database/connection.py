import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger("code_review.database")

Base = declarative_base()

engine = None
SessionLocal = None

def get_or_create_engine():
    global engine, SessionLocal
    if engine is not None and SessionLocal is not None:
        return engine, SessionLocal
        
    try:
        db_url = settings.DATABASE_URL
        connect_args = {"connect_timeout": 10}
        
        # Enable SSL for cloud MySQL providers when not local
        if "localhost" not in db_url and "127.0.0.1" not in db_url and "db:3306" not in db_url:
            # Most managed providers (Aiven, Railway, Supabase) require SSL
            if "ssl" not in db_url.lower():
                connect_args["ssl"] = {"ssl_mode": "REQUIRED"}

        new_engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=10,
            max_overflow=20,
            connect_args=connect_args
        )
        new_session = sessionmaker(autocommit=False, autoflush=False, bind=new_engine)
        engine = new_engine
        SessionLocal = new_session
        return engine, SessionLocal
    except Exception as e:
        logger.error(f"Failed to create SQLAlchemy engine: {e}")
        return None, None

# Initial engine setup
get_or_create_engine()

def get_db() -> Generator:
    """FastAPI dependency to yield database sessions with connection verification."""
    _, session_maker = get_or_create_engine()
    if session_maker is None:
        raise ConnectionError("MySQL database engine is not initialized. Check your DATABASE_URL configuration.")
    
    db = session_maker()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> tuple[bool, str]:
    """Verify if the MySQL database is reachable without throwing unhandled exceptions."""
    eng, _ = get_or_create_engine()
    if eng is None:
        return False, "Database engine failed to initialize. Check DATABASE_URL."
    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "MySQL database connected successfully."
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")
        return False, f"MySQL database unavailable: {str(e)}"


def init_db():
    """Create all database tables on application startup if MySQL is available."""
    eng, _ = get_or_create_engine()
    if eng is not None:
        try:
            Base.metadata.create_all(bind=eng)
            logger.info("Database tables initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
