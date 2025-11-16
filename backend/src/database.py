"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite by default (no installation needed)
# For PostgreSQL, set DATABASE_URL in .env file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bossboard.db")

# SQLite needs check_same_thread=False
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
else:
    # PostgreSQL: Use connection pooling for better performance
    # pool_size: number of connections to keep in pool
    # max_overflow: max connections beyond pool_size
    # pool_pre_ping: verify connections before using (important for ngrok)
    # echo=False: disable SQL logging for better performance
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,           # Keep 10 connections in pool
        max_overflow=20,        # Allow up to 20 extra connections
        pool_pre_ping=True,     # Verify connections before using (important for ngrok)
        echo=False,             # Disable SQL logging for performance
        pool_recycle=3600       # Recycle connections after 1 hour
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

