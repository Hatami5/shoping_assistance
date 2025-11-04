# AI-Shopping-Assistant/app/database/db.py

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from ..utils.logger import setup_logging

logger = setup_logging(__name__)

# --- Configuration ---
# Determine the path for the SQLite database file
# It places the DB file outside the 'app' directory, at the project root level
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'ai_shopping_assistant.db')}"

# --- SQLAlchemy Setup ---
# connect_args is needed only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Base class for declarative class definitions (our ORM models)
Base = declarative_base()

# SessionLocal class for creating new sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Database Models (Schemas) ---

class Product(Base):
    """SQLAlchemy model for storing product data."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    url = Column(String, unique=True, index=True, nullable=False)
    current_price = Column(Float, nullable=False)
    store = Column(String, index=True)
    last_scraped = Column(DateTime, default=datetime.utcnow)
    
    # Optional field for AI/embeddings context
    embedding_vector = Column(String) # Stored as a serialized string/JSON

class PriceHistory(Base):
    """SQLAlchemy model for tracking price changes over time."""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class PriceAlert(Base):
    """SQLAlchemy model for user price drop alerts."""
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    user_email = Column(String, index=True)
    target_price = Column(Float, nullable=False)
    active = Column(Boolean, default=True)

# --- Database Initialization ---

def create_db_and_tables():
    """Initializes the database and creates all tables defined by Base."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")

# --- Dependency for FastAPI Routes ---

def get_db():
    """
    Dependency function to provide a database session to FastAPI route handlers.
    Ensures the session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# --- Initial Setup ---
create_db_and_tables()