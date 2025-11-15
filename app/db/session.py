from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Create the SQLAlchemy engine
engine = create_engine(
    settings.get_database_url(), # Use the dynamic URL getter
    pool_pre_ping=True
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Session:
    """
    FastAPI dependency to get a database session.
    Yields a session and ensures it's closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()