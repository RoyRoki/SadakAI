import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Enum, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, GEOMETRY
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class HazardType(str, enum.Enum):
    POTHOL = "pothole"
    CRACK = "crack"
    SPEED_BREAKER = "speed_breaker"
    WATERLOGGING = "waterlogging"


class Severity(str, enum.Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    CRITICAL = "critical"


class HazardStatus(str, enum.Enum):
    ACTIVE = "active"
    REPORTED = "reported"
    FIXED = "fixed"


class Hazard(Base):
    __tablename__ = "hazards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(HazardType), nullable=False, index=True)
    severity = Column(Enum(Severity), nullable=False, index=True)
    status = Column(Enum(HazardStatus), default=HazardStatus.ACTIVE, nullable=False, index=True)
    
    confidence = Column(Float, nullable=False)
    bbox = Column(JSONB, nullable=False)
    
    location = Column(GEOMETRY("Point", srid=4326), nullable=True, index=True)
    address = Column(Text, nullable=True)
    
    original_image = Column(Text, nullable=True)
    annotated_image = Column(Text, nullable=True)
    danger_score = Column(Float, nullable=True)
    
    session_id = Column(UUID(as_uuid=True), ForeignKey("detection_sessions.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    session = relationship("DetectionSession", back_populates="hazards")
    
    __table_args__ = (
        Index("idx_hazard_geo", "location", postgresql_using="gist"),
        Index("idx_hazard_type_severity", "type", "severity"),
        Index("idx_hazard_status_created", "status", "created_at"),
    )


class DetectionSession(Base):
    __tablename__ = "detection_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_count = Column(Integer, default=0)
    total_hazards = Column(Integer, default=0)
    
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=True)
    
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    hazards = relationship("Hazard", back_populates="session")
    api_key = relationship("APIKey", back_populates="sessions")


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(255), nullable=False, unique=True)
    name = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=30)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    sessions = relationship("DetectionSession", back_populates="api_key")
