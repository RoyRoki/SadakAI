from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum

# --- Enumerations ---

class HazardType(str, Enum):
    """Types of road hazards detectable by the system."""
    POTHOL = "pothole"
    CRACK = "crack"
    SPEED_BREAKER = "speed_breaker"
    WATERLOGGING = "waterlogging"


class Severity(str, Enum):
    """Hazard severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    CRITICAL = "critical"


class HazardStatus(str, Enum):
    """Hazard lifecycle status."""
    ACTIVE = "active"
    REPORTED = "reported"
    FIXED = "fixed"

# --- Common Schemas ---

class Bbox(BaseModel):
    """Bounding box coordinates (normalized or pixel values)."""
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    """Individual hazard detection result from the YOLO model."""
    class_name: str
    confidence: float
    bbox: Bbox
    severity: Severity

# --- Response & Request Schemas ---

class DetectionResult(BaseModel):
    """Comprehensive result of a single image detection process."""
    id: UUID
    detections: List[Detection]
    annotated_image_url: Optional[str] = None
    severity_score: float
    location: Optional[Dict[str, float]] = None


class HazardCreate(BaseModel):
    """Schema for creating a new hazard record."""
    type: HazardType
    severity: Severity
    confidence: float
    bbox: Bbox
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    original_image: Optional[str] = None
    annotated_image: Optional[str] = None
    danger_score: Optional[float] = None


class HazardUpdate(BaseModel):
    """Schema for updating an existing hazard record."""
    status: Optional[HazardStatus] = None
    address: Optional[str] = None


class HazardResponse(BaseModel):
    """Schema for returning hazard details to the client."""
    id: UUID
    type: HazardType
    severity: Severity
    status: HazardStatus
    confidence: float
    bbox: Bbox
    location: Optional[Dict[str, float]] = None
    address: Optional[str] = None
    original_image: Optional[str] = None
    annotated_image: Optional[str] = None
    danger_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        # Allow Pydantic to work with SQLAlchemy models directly
        from_attributes = True


class HazardListResponse(BaseModel):
    """Paginated list of hazards."""
    items: List[HazardResponse]
    total: int
    page: int
    page_size: int

# --- Statistics Schemas ---

class StatsOverview(BaseModel):
    """High-level system statistics."""
    total_hazards: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    critical_count: int
    fixed_count: int
    detection_rate: float


class StatsTrends(BaseModel):
    """Reporting activity trends over a period."""
    period: str
    data: List[Dict[str, Any]]


class NearbyHazard(BaseModel):
    """Simplified hazard data for map markers or nearby lists."""
    id: UUID
    type: HazardType
    severity: Severity
    distance_km: float

# --- System Schemas ---

class HealthResponse(BaseModel):
    """API health status response."""
    status: str
    model_loaded: bool
    version: str = "1.0.0"
