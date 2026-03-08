from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Depends
from typing import Optional
from uuid import uuid4
import logging
import json

from api.services.detection import run_inference, annotate_image
from api.services.storage import storage_service
from api.models.schemas import DetectionResult, Detection, Bbox, Severity
from api.models.database_sqlite import SessionLocal, Session, DetectionSession, Hazard

router = APIRouter()
logger = logging.getLogger(__name__)


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


@router.post("/detect", response_model=DetectionResult)
async def detect_hazards(
    file: UploadFile = File(...),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Upload an image for road hazard detection.
    
    Processes the uploaded image through the YOLO model, saves the detection 
    results to the database, and returns the detected hazards.
    
    Args:
        file: The image file to process (JPEG, PNG, WebP, etc.)
        lat: Optional latitude of the hazard location
        lng: Optional longitude of the hazard location
        db: Database session dependency
        
    Returns:
        DetectionResult containing session ID, detected hazards, and severity score.
        
    Raises:
        HTTPException: 400 for invalid format/size, 500 for inference failures.
    """
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"]
    content_type = file.content_type or ""
    
    # Validate file type
    if not any(content_type.startswith(t.replace("*", "")) for t in allowed_types):
        if not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid image format")
    
    # Read file content
    image_bytes = await file.read()
    
    # Enforce size limit (10MB)
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
    
    # Run YOLO inference
    result = run_inference(image_bytes)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Detection failed"))
    
    # Create a detection session record
    session_id = str(uuid4())
    session = DetectionSession(
        id=session_id,
        image_count=1,
        total_hazards=len(result["detections"])
    )
    db.add(session)
    
    # Note: annotated_image_url is currently null as storage upload is optional
    # annotated_bytes = annotate_image(image_bytes, result["detections"])
    
    # Create hazard records for each detection
    hazard_ids = []
    for det in result["detections"]:
        hazard = Hazard(
            id=str(uuid4()),
            type=det["class_name"],
            severity=det["severity"],
            confidence=det["confidence"],
            bbox=json.dumps(det["bbox"]),
            session_id=session_id,
            danger_score=result["danger_score"],
            lat=lat,
            lng=lng
        )
        db.add(hazard)
        hazard_ids.append(hazard.id)
    
    db.commit()
    
    return DetectionResult(
        id=session_id,
        detections=[
            Detection(
                class_name=d["class_name"],
                confidence=d["confidence"],
                bbox=Bbox(**d["bbox"]),
                severity=Severity(d["severity"])
            )
            for d in result["detections"]
        ],
        annotated_image_url=None,
        severity_score=result["danger_score"],
        location={"lat": lat, "lng": lng} if lat and lng else None
    )


@router.post("/detect/batch")
async def detect_batch(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Process multiple images for hazard detection in a single session.
    
    Args:
        files: List of image files to process
        db: Database session dependency
        
    Returns:
        Dictionary with session_id and list of results per filename.
    """
    results = []
    session_id = str(uuid4())
    
    session = DetectionSession(
        id=session_id,
        image_count=len(files),
        total_hazards=0
    )
    db.add(session)
    
    for file in files:
        image_bytes = await file.read()
        result = run_inference(image_bytes)
        
        if result["success"]:
            session.total_hazards += len(result["detections"])
            results.append({
                "filename": file.filename,
                "success": True,
                "detections": result["detections"],
                "danger_score": result["danger_score"]
            })
        else:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": result.get("error")
            })
    
    db.commit()
    
    return {
        "session_id": session_id,
        "results": results
    }
