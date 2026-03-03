# app/core/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default to zoning.db, but look for a custom URL set in environment variable
#DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./zoning.db")
#engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})



# Get the directory of this file (app/core/db.py)
basedir = os.path.abspath(os.path.dirname(__file__))
# Construct the absolute path to the database file in your root directory
# (going up two levels from app/core/)
db_path = os.path.join(basedir, '../../zoning.db')
DATABASE_URL = f"sqlite:///{db_path}" # <--- Hardcode this for now
engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get a DB session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
