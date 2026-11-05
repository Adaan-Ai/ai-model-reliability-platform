"""
Database Connection & Session Management
Provides SQLAlchemy Engine, SessionLocal factory, Base declarative class,
and the get_db() FastAPI dependency with transactional scope.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Create SQLAlchemy engine configured for MySQL
# pool_pre_ping ensures connections in the pool are tested before being handed to requests
# pool_recycle handles connection timeouts gracefully
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True if detailed SQL statement logs are desired during development
)

# Thread-safe session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all ORM models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session per request
    and guarantees proper closing/rollback upon completion or error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
