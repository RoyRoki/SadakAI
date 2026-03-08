from fastapi import APIRouter, Query, Depends
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from api.models.schemas import StatsOverview, StatsTrends
from api.models.database_sqlite import Hazard, SessionLocal

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


@router.get("/stats/overview", response_model=StatsOverview)
async def get_stats_overview(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get a high-level overview of hazard statistics.
    
    Provides counts by type, severity, and status, along with 
    aggregate metrics like critical count and fix rate.
    
    Args:
        from_date: Optional start date for stats (ISO format)
        to_date: Optional end date for stats (ISO format)
        db: Database session dependency
        
    Returns:
        StatsOverview containing counts and calculated rates.
    """
    query = db.query(Hazard).filter(Hazard.deleted_at.is_(None))
    
    # Apply date filters
    if from_date:
        query = query.filter(Hazard.created_at >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.filter(Hazard.created_at <= datetime.fromisoformat(to_date))
    
    total = query.count()
    
    from collections import Counter
    # Count occurrences by type
    types = query.with_entities(Hazard.type).all()
    by_type = dict(Counter([t[0] for t in types]))
    
    # Count occurrences by severity
    severities = query.with_entities(Hazard.severity).all()
    by_severity = dict(Counter([s[0] for s in severities]))
    
    # Count occurrences by status
    statuses = query.with_entities(Hazard.status).all()
    by_status = dict(Counter([s[0] for s in statuses]))
    
    critical_count = by_severity.get("critical", 0)
    fixed_count = by_status.get("fixed", 0)
    detection_rate = (fixed_count / total * 100) if total > 0 else 0
    
    return StatsOverview(
        total_hazards=total,
        by_type=by_type,
        by_severity=by_severity,
        by_status=by_status,
        critical_count=critical_count,
        fixed_count=fixed_count,
        detection_rate=round(detection_rate, 1)
    )


@router.get("/stats/trends", response_model=StatsTrends)
async def get_stats_trends(
    period: str = Query("day", regex="^(day|week|month)$"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get hazard trends over time.
    
    Groups hazards by date to show reporting activity trends.
    
    Args:
        period: Time period for grouping (day, week, month)
        from_date: Optional start date (defaults to last 90 days)
        to_date: Optional end date
        db: Database session dependency
        
    Returns:
        StatsTrends containing a list of date-count pairs.
    """
    query = db.query(Hazard).filter(Hazard.deleted_at.is_(None))
    
    # Apply date filters with a 90-day default window if from_date is missing
    if from_date:
        query = query.filter(Hazard.created_at >= datetime.fromisoformat(from_date))
    else:
        query = query.filter(Hazard.created_at >= datetime.utcnow() - timedelta(days=90))
    
    if to_date:
        query = query.filter(Hazard.created_at <= datetime.fromisoformat(to_date))
    
    hazards = query.all()
    
    from collections import defaultdict
    by_date = defaultdict(int)
    for h in hazards:
        # Currently only supports daily grouping regardless of 'period' parameter
        # TODO: Implement weekly/monthly grouping logic based on 'period'
        date_str = h.created_at.strftime("%Y-%m-%d")
        by_date[date_str] += 1
    
    data = [{"date": d, "count": c} for d, c in sorted(by_date.items())]
    
    return StatsTrends(period=period, data=data)


@router.get("/stats/worst-roads")
async def get_worst_areas(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Identify areas with the highest concentration of hazards.
    
    Args:
        limit: Number of top areas to return (max 50)
        db: Database session dependency
        
    Returns:
        List of areas and their corresponding hazard counts.
    """
    hazards = db.query(Hazard).filter(
        Hazard.deleted_at.is_(None),
        Hazard.address.isnot(None)
    ).all()
    
    from collections import Counter
    # Group hazards by their reverse-geocoded address
    area_counts = Counter(h.address for h in hazards if h.address)
    
    worst = [{"area": area, "count": count} for area, count in area_counts.most_common(limit)]
    
    return {"worst_areas": worst}
