import json
import random
from datetime import datetime, timedelta
from uuid import uuid4
from api.models.database_sqlite import SessionLocal, Hazard, DetectionSession, create_tables
import uuid

HAZARD_TYPES = ["pothole", "crack", "speed_breaker", "waterlogging"]
SEVERITIES = ["minor", "moderate", "critical"]
STATUSES = ["active", "reported", "fixed"]

SILIGURI_AREA = {
    "lat_min": 26.65,
    "lat_max": 26.85,
    "lng_min": 88.35,
    "lng_max": 88.55
}

ADDRESSES = [
    "NH-31, Siliguri",
    "Sevoke Road, Siliguri",
    "Bidhan Road, Siliguri",
    "Hill Cart Road, Siliguri",
    "MG Road, Siliguri",
    "Darjeeling More, Siliguri",
    "Matigara, Siliguri",
    "Pradhannagar, Siliguri",
    "Kanchenjunga Road, Siliguri",
    "Burudih More, Siliguri"
]


def generate_seed_data(count: int = 100):
    db = SessionLocal()
    
    existing = db.query(Hazard).count()
    if existing > 0:
        print(f"Database already has {existing} hazards. Skipping seed.")
        return
    
    print(f"Generating {count} demo hazards...")
    
    for i in range(count):
        hazard_type = random.choice(HAZARD_TYPES)
        severity = random.choice(SEVERITIES)
        status = random.choice(STATUSES)
        
        lat = random.uniform(SILIGURI_AREA["lat_min"], SILIGURI_AREA["lat_max"])
        lng = random.uniform(SILIGURI_AREA["lng_min"], SILIGURI_AREA["lng_max"])
        
        days_ago = random.randint(0, 90)
        created_at = datetime.utcnow() - timedelta(days=days_ago)
        
        bbox = {
            "x1": random.randint(50, 200),
            "y1": random.randint(50, 200),
            "x2": random.randint(300, 500),
            "y2": random.randint(300, 500)
        }
        
        hazard = Hazard(
            id=str(uuid4()),
            type=hazard_type,
            severity=severity,
            status=status,
            confidence=round(random.uniform(0.6, 0.99), 2),
            bbox=json.dumps(bbox),
            lat=lat,
            lng=lng,
            address=random.choice(ADDRESSES),
            danger_score=round(random.uniform(1, 9), 1),
            created_at=created_at,
            updated_at=created_at
        )
        db.add(hazard)
    
    db.commit()
    print(f"✅ Created {count} demo hazards!")
    
    total = db.query(Hazard).count()
    print(f"Total hazards in database: {total}")


if __name__ == "__main__":
    create_tables()
    generate_seed_data(100)
