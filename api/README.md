# SadakAI API

FastAPI backend for the SadakAI road hazard detection platform.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (with PostGIS extension)
- Or SQLite for development

### Installation

```bash
# Navigate to API directory
cd api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start the server
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Setup

```bash
# Using SQLite (no external dependencies)
docker build -t sadakai-api .
docker run -p 8000:8000 sadakai-api

# Using Docker Compose (with PostgreSQL)
docker-compose up -d api
```

## ⚙️ Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./sadakai.db` |
| `R2_ENDPOINT` | Cloudflare R2 endpoint | None |
| `R2_ACCESS_KEY` | R2 access key | None |
| `R2_SECRET_KEY` | R2 secret key | None |
| `R2_BUCKET` | R2 bucket name | `sadakai-images` |
| `API_KEY` | API authentication key | `dev_api_key` |
| `MODEL_PATH` | Path to YOLO model weights | `model/weights/best.pt` |

## 🏗️ Project Structure

```
api/
├── config.py              # Configuration management
├── main.py               # FastAPI application entry point
├── seed.py               # Demo data seeder
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image definition
│
├── models/               # Database layer
│   ├── database.py       # SQLAlchemy models (PostgreSQL)
│   ├── database_sqlite.py # SQLite models (development)
│   └── schemas.py        # Pydantic schemas
│
├── routers/              # API endpoints
│   ├── detect.py         # Image detection endpoints
│   ├── hazards.py        # Hazard CRUD endpoints
│   └── stats.py          # Statistics endpoints
│
└── services/             # Business logic
    ├── detection.py      # YOLO inference wrapper
    └── storage.py        # R2 storage service
```

## 📡 API Endpoints

### Health Check

```bash
GET /health

Response:
{
  "status": "ok",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### Detection

#### POST /api/detect

Upload an image for hazard detection.

```bash
curl -X POST http://localhost:8000/api/detect \
  -F "file=@image.jpg" \
  -F "lat=26.7" \
  -F "lng=88.4"
```

**Parameters:**
- `file` (required): Image file (JPEG, PNG, WebP)
- `lat` (optional): Latitude of hazard location
- `lng` (optional): Longitude of hazard location

**Response:**
```json
{
  "id": "uuid",
  "detections": [
    {
      "class_name": "pothole",
      "confidence": 0.87,
      "bbox": {"x1": 100, "y1": 50, "x2": 300, "y2": 200},
      "severity": "moderate"
    }
  ],
  "annotated_image_url": null,
  "severity_score": 5.5,
  "location": {"lat": 26.7, "lng": 88.4}
}
```

### Hazards

#### GET /api/hazards

List all hazards with optional filtering.

```bash
curl "http://localhost:8000/api/hazards?severity=critical&type=pothole&page=1&page_size=50"
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50, max: 100)
- `severity`: Filter by severity (minor, moderate, critical)
- `type`: Filter by type (pothole, crack, speed_breaker, waterlogging)
- `status`: Filter by status (active, reported, fixed)
- `from_date`: Filter from date (ISO format)
- `to_date`: Filter to date (ISO format)

#### GET /api/hazards/{id}

Get single hazard details.

#### PATCH /api/hazards/{id}

Update hazard status.

```bash
curl -X PATCH http://localhost:8000/api/hazards/{id} \
  -H "Content-Type: application/json" \
  -d '{"status": "fixed"}'
```

#### DELETE /api/hazards/{id}

Soft delete a hazard.

#### GET /api/hazards/nearby

Get hazards near a location.

```bash
curl "http://localhost:8000/api/hazards/nearby?lat=26.7&lng=88.4&radius_km=5"
```

### Statistics

#### GET /api/stats/overview

Get overview statistics.

```bash
curl "http://localhost:8000/api/stats/overview"
```

**Response:**
```json
{
  "total_hazards": 150,
  "by_type": {"pothole": 50, "crack": 30, "speed_breaker": 40, "waterlogging": 30},
  "by_severity": {"minor": 40, "moderate": 60, "critical": 50},
  "by_status": {"active": 80, "reported": 40, "fixed": 30},
  "critical_count": 50,
  "fixed_count": 30,
  "detection_rate": 20.0
}
```

#### GET /api/stats/trends

Get hazard trends over time.

```bash
curl "http://localhost:8000/api/stats/trends?period=day"
```

## 🗄️ Database Schema

### Hazards Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `type` | VARCHAR(50) | Hazard type |
| `severity` | VARCHAR(50) | Severity level |
| `status` | VARCHAR(50) | Hazard status |
| `confidence` | FLOAT | Model confidence |
| `bbox` | JSONB | Bounding box coordinates |
| `lat` | FLOAT | Latitude (SQLite) |
| `lng` | FLOAT | Longitude (SQLite) |
| `location` | GEOMETRY(Point) | PostGIS location |
| `address` | TEXT | Reverse geocoded address |
| `original_image` | TEXT | Original image URL |
| `annotated_image` | TEXT | Annotated image URL |
| `danger_score` | FLOAT | Aggregate danger score |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |
| `deleted_at` | TIMESTAMP | Soft delete timestamp |

### Detection Sessions Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `image_count` | INT | Number of images processed |
| `total_hazards` | INT | Total hazards detected |
| `api_key_id` | UUID | FK to API keys |
| `metadata` | JSONB | Additional metadata |
| `created_at` | TIMESTAMP | Creation timestamp |

## 🔒 Authentication

The API uses a simple API key authentication for write operations:

```bash
# Include API key in requests
curl -H "X-API-Key: your_api_key" \
  -X POST http://localhost:8000/api/detect \
  -F "file=@image.jpg"
```

## 🧪 Testing

```bash
# Run the API
uvicorn api.main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Test detection
curl -X POST http://localhost:8000/api/detect \
  -F "file=@/path/to/image.jpg"

# Test hazards list
curl http://localhost:8000/api/hazards

# Test stats
curl http://localhost:8000/api/stats/overview
```

## 🔧 Development

### Adding New Endpoints

1. Create a new router file in `api/routers/`
2. Define endpoints using FastAPI
3. Import and include the router in `api/main.py`

Example:
```python
# api/routers/example.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def example_endpoint():
    return {"message": "Hello, World!"}

# api/main.py
from api.routers import example
app.include_router(example.router, prefix="/api")
```

### Database Migrations

For PostgreSQL with Alembic:

```bash
cd api
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 📦 Dependencies

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Ultralytics** - YOLO model
- **Boto3** - AWS/S3 storage
- **GeoAlchemy2** - PostGIS support

See `requirements.txt` for full list.

## 📄 License

MIT License - see parent project README.
