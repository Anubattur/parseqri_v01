from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import re

# Ensure the database URL is for PostgreSQL
database_url = settings.DATABASE_URL
if not database_url.startswith('postgresql'):
    # If it's a different database type, default to a local PostgreSQL instance
    print("Warning: Non-PostgreSQL database URL detected. Using default PostgreSQL settings.")
    database_url = "postgresql://postgres:password@localhost:5432/parseqri"

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()