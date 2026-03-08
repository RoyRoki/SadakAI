import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker, Session
import enum

# Define SQLAlchemy Base
Base = declarative_base()


class HazardType(str, enum.Enum):
    """Enumeration of supported road hazard types."""
    POTHOL = "pothole"
    CRACK = "crack"
    SPEED_BREAKER = "speed_breaker"
    WATERLOGGING = "waterlogging"


class Severity(str, enum.Enum):
    """Enumeration of hazard severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    CRITICAL = "critical"


class HazardStatus(str, enum.Enum):
    """Enumeration of hazard reporting and fix statuses."""
    ACTIVE = "active"
    REPORTED = "reported"
    FIXED = "fixed"


class Hazard(Base):
    """
    SQLAlchemy model representing a single road hazard detection.
    
    Contains spatial location, visual classification, and lifecycle information.
    """
    __tablename__ = "hazards"
    
    # Unique identifier (UUID string)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Classification & Status
    type = Column(String(50), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default="active", nullable=False, index=True)
    
    # Model Metadata
    confidence = Column(Float, nullable=False)
    bbox = Column(Text, nullable=False) # JSON stringified bounding box
    
    # Geospatial Data
    lat = Column(Float, nullable=True, index=True)
    lng = Column(Float, nullable=True, index=True)
    address = Column(Text, nullable=True) # Reverse-geocoded human-readable location
    
    # Visual References
    original_image = Column(Text, nullable=True)
    annotated_image = Column(Text, nullable=True)
    
    # Aggregated metrics
    danger_score = Column(Float, nullable=True)
    
    # Relations
    session_id = Column(String(36), ForeignKey("detection_sessions.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True) # Soft delete timestamp
    
    session = relationship("DetectionSession", back_populates="hazards")


class DetectionSession(Base):
    """
    SQLAlchemy model representing an upload or detection event.
    
    A session can contain multiple hazard detections from one or more images.
    """
    __tablename__ = "detection_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_count = Column(Integer, default=0)
    total_hazards = Column(Integer, default=0)
    
    # Relation to the API key used for authentication
    api_key_id = Column(String(36), ForeignKey("api_keys.id"), nullable=True)
    
    # JSON metadata for the session
    meta = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    hazards = relationship("Hazard", back_populates="session")
    api_key = relationship("APIKey", back_populates="sessions")


class APIKey(Base):
    """
    SQLAlchemy model representing an authentication key.
    
    Used to track and limit usage of the API.
    """
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key_hash = Column(String(255), nullable=False, unique=True)
    name = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=30)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    sessions = relationship("DetectionSession", back_populates="api_key")


# Default SQLite database location
SQLALCHEMY_DATABASE_URL = "sqlite:///./sadakai.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} # Required for SQLite with multi-threaded FastAPI
)

# Database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all defined tables in the database if they do not exist."""
    Base.metadata.create_all(bind=engine)
