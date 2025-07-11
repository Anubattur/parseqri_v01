from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import re

# Ensure the database URL is for MySQL
database_url = settings.DATABASE_URL
if not database_url.startswith('mysql'):
    # If it's a different database type, default to a local MySQL instance
    print("Warning: Non-MySQL database URL detected. Using default MySQL settings.")
    database_url = "mysql+pymysql://root:root@localhost:3306/parseqri"

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()