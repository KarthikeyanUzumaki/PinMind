import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("pinmind.database")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("DATABASE_URL not found in env. Defaulting to local SQLite.")
    DATABASE_URL = "sqlite:///./pinmind.db"

engine = None
SessionLocal = None

try:
    # Try connecting to the specified database (Supabase PostgreSQL)
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        logger.info("Connected to local SQLite database.")
    else:
        # Configure connection engine with a 5-second fast-fail connection timeout
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=5,
            pool_recycle=1800
        )
        # Attempt a quick connection test to verify port/address routing
        with engine.connect() as conn:
            pass
        logger.info("Successfully connected to Supabase PostgreSQL cloud database.")
except Exception as e:
    logger.warning(
        f"Supabase PostgreSQL connection timed out/failed ({str(e)}).\n"
        "This usually indicates that port 5432 is blocked by your local network/ISP firewall.\n"
        "Self-healing database fallback: Redirecting application storage to local SQLite (pinmind.db)."
    )
    DATABASE_URL = "sqlite:///./pinmind.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    FastAPI Dependency yielding active database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
