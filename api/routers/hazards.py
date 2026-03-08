from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from uuid import uuid4
from sqlalchemy.orm import Session
from datetime import datetime
import json

from api.models.database_sqlite import SessionLocal, Hazard, DetectionSession
from api.models.schemas import (
    HazardResponse, HazardListResponse, HazardCreate, HazardUpdate,
    HazardType, Severity, HazardStatus, NearbyHazard
)

router = APIRouter()


def get_db():
    """
    Database session dependency.
    Yields a database session and ensures it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/hazards", response_model=HazardListResponse)
async def list_hazards(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    hazard_type: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all hazards with optional filtering and pagination.
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        severity: Filter by severity (minor, moderate, critical)
        hazard_type: Filter by hazard type (pothole, crack, speed_breaker, waterlogging)
        status: Filter by status (active, reported, fixed)
        from_date: Filter hazards created after this date (ISO format)
        to_date: Filter hazards created before this date (ISO format)
        db: Database session dependency
        
    Returns:
        HazardListResponse containing items, total count, page, and page_size.
    """
    query = db.query(Hazard).filter(Hazard.deleted_at.is_(None))
    
    # Apply filters if provided
    if severity:
        query = query.filter(Hazard.severity == severity)
    if hazard_type:
        query = query.filter(Hazard.type == hazard_type)
    if status:
        query = query.filter(Hazard.status == status)
    if from_date:
        query = query.filter(Hazard.created_at >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.filter(Hazard.created_at <= datetime.fromisoformat(to_date))
    
    # Count total matching records
    total = query.count()
    
    # Apply pagination and fetch results
    hazards = query.offset((page - 1) * page_size).limit(page_size).all()
    
    items = []
    for h in hazards:
        location_dict = None
        if h.lat and h.lng:
            location_dict = {"lat": h.lat, "lng": h.lng}
        
        items.append(HazardResponse(
            id=h.id,
            type=h.type,
            severity=h.severity,
            status=h.status,
            confidence=h.confidence,
            bbox=json.loads(h.bbox) if h.bbox else {},
            location=location_dict,
            address=h.address,
            original_image=h.original_image,
            annotated_image=h.annotated_image,
            danger_score=h.danger_score,
            created_at=h.created_at,
            updated_at=h.updated_at
        ))
    
    return HazardListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/hazards/{hazard_id}", response_model=HazardResponse)
async def get_hazard(hazard_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information for a single hazard.
    
    Args:
        hazard_id: The unique identifier of the hazard
        db: Database session dependency
        
    Returns:
        HazardResponse with all hazard details.
        
    Raises:
        HTTPException: 404 if hazard is not found.
    """
    hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
    if not hazard:
        raise HTTPException(status_code=404, detail="Hazard not found")
    
    location_dict = None
    if hazard.lat and hazard.lng:
        location_dict = {"lat": hazard.lat, "lng": hazard.lng}
    
    return HazardResponse(
        id=hazard.id,
        type=hazard.type,
        severity=hazard.severity,
        status=hazard.status,
        confidence=hazard.confidence,
        bbox=json.loads(hazard.bbox) if hazard.bbox else {},
        location=location_dict,
        address=hazard.address,
        original_image=hazard.original_image,
        annotated_image=hazard.annotated_image,
        danger_score=hazard.danger_score,
        created_at=hazard.created_at,
        updated_at=hazard.updated_at
    )


@router.patch("/hazards/{hazard_id}")
async def update_hazard(hazard_id: str, update: HazardUpdate, db: Session = Depends(get_db)):
    """
    Update hazard status or address.
    
    Args:
        hazard_id: The unique identifier of the hazard
        update: HazardUpdate object containing fields to update
        db: Database session dependency
        
    Returns:
        Dictionary with success flag and hazard ID.
        
    Raises:
        HTTPException: 404 if hazard is not found.
    """
    hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
    if not hazard:
        raise HTTPException(status_code=404, detail="Hazard not found")
    
    # Update provided fields
    if update.status:
        hazard.status = update.status
    if update.address:
        hazard.address = update.address
    
    hazard.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "id": hazard_id}


@router.delete("/hazards/{hazard_id}")
async def delete_hazard(hazard_id: str, db: Session = Depends(get_db)):
    """
    Soft delete a hazard by setting its deleted_at timestamp.
    
    Args:
        hazard_id: The unique identifier of the hazard
        db: Database session dependency
        
    Returns:
        Dictionary with success flag and hazard ID.
        
    Raises:
        HTTPException: 404 if hazard is not found.
    """
    hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
    if not hazard:
        raise HTTPException(status_code=404, detail="Hazard not found")
    
    hazard.deleted_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "id": hazard_id}


@router.get("/hazards/nearby")
async def get_nearby_hazards(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5, ge=0.1, le=50),
    db: Session = Depends(get_db)
):
    """
    Search for hazards within a specified radius of a location.
    
    Uses a bounding box approximation for performance followed by 
    Euclidean distance calculation.
    
    Args:
        lat: Latitude of the center point
        lng: Longitude of the center point
        radius_km: Radius in kilometers (default 5km, max 50km)
        db: Database session dependency
        
    Returns:
        List of NearbyHazard objects including type, severity, and distance.
    """
    import math
    
    # Simple bounding box approximation
    lat_min = lat - (radius_km / 111.0)
    lat_max = lat + (radius_km / 111.0)
    lng_min = lng - (radius_km / (111.0 * math.cos(math.radians(lat))))
    lng_max = lng + (radius_km / (111.0 * math.cos(math.radians(lat))))
    
    # Fetch candidates within bounding box
    hazards = db.query(Hazard).filter(
        Hazard.deleted_at.is_(None),
        Hazard.lat.between(lat_min, lat_max),
        Hazard.lng.between(lng_min, lng_max)
    ).limit(20).all()
    
    results = []
    for h in hazards:
        # Calculate approximate distance
        distance = math.sqrt((h.lat - lat)**2 + (h.lng - lng)**2) * 111.0
        results.append(NearbyHazard(
            id=h.id,
            type=h.type,
            severity=h.severity,
            distance_km=round(distance, 2)
        ))
    
    return results
