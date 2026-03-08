# SadakAI - Project Breakdown (L1 → L2 → L3)

**Real-time Indian Road Hazard Detection & Crowdsourced Mapping Platform**

---

## Data Strategy: Existing Open Datasets ONLY

No going outside. No dashcam recording. All training uses publicly available datasets:

| Dataset | Source | What It Has | Size |
|---------|--------|-------------|------|
| Indian Pothole Dataset | Roboflow Universe | Annotated Indian road potholes | 1,500+ images |
| Road Damage Dataset (RDD2022) | IEEE Big Data Cup | Potholes, cracks, rutting (Japan/India/Czech) | 47,000+ images |
| Pothole Detection Dataset | Kaggle (various) | Labeled potholes, different severities | 5,000+ images |
| Indian Driving Dataset (IDD) | IIIT Hyderabad | Indian road scenes, segmentation masks | 10,000+ frames |
| Speed Breaker Dataset | Roboflow Universe | Annotated speed breakers | 500+ images |

**Augmentation:** Roboflow auto-augmentation (flip, rotate, brightness, blur, crop) to 3-5x the dataset size for free.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                    │
│  Dashboard │ Map View │ Upload │ Reports │ Stats         │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                  BACKEND (FastAPI)                       │
│  /detect │ /hazards │ /reports │ /stats │ /upload        │
└───────┬──────────┬──────────────────┬───────────────────┘
        │          │                  │
   ┌────▼────┐ ┌───▼────────┐  ┌─────▼──────┐
   │ YOLOv8  │ │ PostgreSQL │  │ Cloudflare │
   │ Model   │ │ + PostGIS  │  │ R2 Storage │
   └─────────┘ └────────────┘  └────────────┘
```

---

# L1: SYSTEM MODULES

The project has **4 major L1 modules:**

| # | L1 Module | Purpose |
|---|-----------|---------|
| 1 | **Detection Engine** | YOLOv8 model training + inference pipeline |
| 2 | **Backend API** | FastAPI server handling requests, data, business logic |
| 3 | **Frontend Dashboard** | Next.js web app with maps, uploads, stats |
| 4 | **Data Layer** | PostgreSQL + PostGIS + R2 storage |

---

# L1.1: DETECTION ENGINE

> YOLOv8 model that detects road hazards from images

## L2 Breakdown

| # | L2 Component | Description |
|---|-------------|-------------|
| 1.1 | Dataset Preparation | Collect, clean, merge open datasets |
| 1.2 | Model Training | Train YOLOv8 on Google Colab |
| 1.3 | Inference Pipeline | Run detection on uploaded images |
| 1.4 | Severity Scoring | Score each detection (minor/moderate/critical) |

---

### L3: 1.1 Dataset Preparation

| # | Task | Details |
|---|------|---------|
| 1.1.1 | Download datasets | Pull RDD2022 + Kaggle pothole + Roboflow datasets |
| 1.1.2 | Normalize annotations | Convert all to YOLO format (class x_center y_center width height) |
| 1.1.3 | Unify class labels | Map all labels to: `pothole`, `crack`, `speed_breaker`, `waterlogging` |
| 1.1.4 | Train/val/test split | 70% train, 20% val, 10% test |
| 1.1.5 | Augmentation | Roboflow augmentation: flip, rotate ±15°, brightness ±25%, blur, mosaic |
| 1.1.6 | Dataset YAML | Create `data.yaml` with class names, paths, counts |
| 1.1.7 | Validation | Spot-check 50 random images to verify annotations are correct |

**Output:** Clean dataset folder with `train/`, `val/`, `test/` in YOLO format

---

### L3: 1.2 Model Training

| # | Task | Details |
|---|------|---------|
| 1.2.1 | Colab setup | Mount Drive, install `ultralytics`, upload dataset |
| 1.2.2 | Base model selection | Start with `yolov8m.pt` (medium - good accuracy/speed balance) |
| 1.2.3 | Training config | `epochs=100, imgsz=640, batch=16, patience=20` |
| 1.2.4 | Training run | `model.train(data='data.yaml', ...)` on Colab T4 GPU |
| 1.2.5 | Evaluate metrics | Check mAP@50, mAP@50-95, precision, recall per class |
| 1.2.6 | Confusion matrix | Analyze misclassifications, identify weak classes |
| 1.2.7 | Hyperparameter tuning | Adjust lr, augmentation, mosaic if mAP < 80% |
| 1.2.8 | Export model | Export best weights as `best.pt` + ONNX format |
| 1.2.9 | Model card | Document: classes, mAP scores, dataset size, training config |

**Target:** mAP@50 ≥ 80% on test set
**Output:** `best.pt` (YOLOv8 weights), `best.onnx` (for deployment)

---

### L3: 1.3 Inference Pipeline

| # | Task | Details |
|---|------|---------|
| 1.3.1 | Load model | `YOLO('best.pt')` with Ultralytics |
| 1.3.2 | Preprocess image | Resize to 640x640, normalize, handle EXIF rotation |
| 1.3.3 | Run inference | `model.predict(image, conf=0.25, iou=0.45)` |
| 1.3.4 | Parse results | Extract: class, confidence, bounding box (x1,y1,x2,y2) |
| 1.3.5 | Draw annotations | Overlay bounding boxes + labels on original image |
| 1.3.6 | Return structured output | JSON: `{detections: [{class, confidence, bbox, severity}]}` |
| 1.3.7 | Batch processing | Support multiple images in one request |
| 1.3.8 | Performance | Target: < 500ms per image on CPU, < 100ms on GPU |

**Output:** Function `detect(image) -> DetectionResult`

---

### L3: 1.4 Severity Scoring

| # | Task | Details |
|---|------|---------|
| 1.4.1 | Size calculation | Calculate bounding box area as % of image |
| 1.4.2 | Severity thresholds | `minor: <2%`, `moderate: 2-5%`, `critical: >5%` of image area |
| 1.4.3 | Confidence weighting | Factor in model confidence (low conf = reduce severity) |
| 1.4.4 | Class-specific rules | Speed breakers always `moderate+`, waterlogging always `critical` |
| 1.4.5 | Aggregate scoring | Multiple hazards in one image = higher road danger score |
| 1.4.6 | Output format | Each detection gets: `severity: "minor" | "moderate" | "critical"` |

**Output:** Severity score attached to each detection

---

# L1.2: BACKEND API

> FastAPI server exposing detection, data, and reporting endpoints

## L2 Breakdown

| # | L2 Component | Description |
|---|-------------|-------------|
| 2.1 | API Server Setup | FastAPI app, CORS, middleware, config |
| 2.2 | Detection Endpoints | Upload image → get detections |
| 2.3 | Hazard CRUD | Store, query, filter detected hazards |
| 2.4 | Geospatial Queries | Location-based hazard lookups (PostGIS) |
| 2.5 | Statistics & Reports | Aggregated stats, CSV/PDF report generation |
| 2.6 | Auth (Basic) | API key auth for uploads, public read for map |

---

### L3: 2.1 API Server Setup

| # | Task | Details |
|---|------|---------|
| 2.1.1 | Project structure | `api/main.py`, `api/routers/`, `api/models/`, `api/services/`, `api/config.py` |
| 2.1.2 | FastAPI app init | Create app with title, description, version |
| 2.1.3 | CORS middleware | Allow frontend origin (localhost + production domain) |
| 2.1.4 | Environment config | `.env` for DB_URL, R2 keys, API keys, model path |
| 2.1.5 | Lifespan handler | Load YOLO model once on startup, cleanup on shutdown |
| 2.1.6 | Error handling | Global exception handler, structured error responses |
| 2.1.7 | Logging | Structured JSON logging with request IDs |
| 2.1.8 | Health check | `GET /health` → `{status: "ok", model_loaded: true}` |

---

### L3: 2.2 Detection Endpoints

| # | Task | Details |
|---|------|---------|
| 2.2.1 | `POST /api/detect` | Accept image upload (multipart/form-data) |
| 2.2.2 | Image validation | Check file type (jpg/png/webp), max size 10MB |
| 2.2.3 | Run detection | Call inference pipeline from L1.3 |
| 2.2.4 | Optional geotag | Accept `lat`, `lng` query params or extract from EXIF |
| 2.2.5 | Save detection | Store result in DB with timestamp + location |
| 2.2.6 | Upload annotated image | Save annotated image to R2, return URL |
| 2.2.7 | Response format | `{id, detections: [...], annotated_image_url, severity_score, location}` |
| 2.2.8 | `POST /api/detect/batch` | Accept multiple images, return array of results |

---

### L3: 2.3 Hazard CRUD

| # | Task | Details |
|---|------|---------|
| 2.3.1 | `GET /api/hazards` | List all hazards, paginated (default 50) |
| 2.3.2 | Query filters | `?severity=critical&type=pothole&from=2026-01-01&to=2026-03-01` |
| 2.3.3 | `GET /api/hazards/:id` | Single hazard detail with all detections |
| 2.3.4 | `PATCH /api/hazards/:id` | Update status: `active` → `reported` → `fixed` |
| 2.3.5 | `DELETE /api/hazards/:id` | Soft delete (mark as removed, don't hard delete) |
| 2.3.6 | Pydantic schemas | Request/response models for all endpoints |

---

### L3: 2.4 Geospatial Queries

| # | Task | Details |
|---|------|---------|
| 2.4.1 | PostGIS extension | Enable PostGIS on PostgreSQL |
| 2.4.2 | Geometry column | `location GEOMETRY(Point, 4326)` on hazards table |
| 2.4.3 | `GET /api/hazards/nearby` | `?lat=26.7&lng=88.4&radius_km=5` → hazards within radius |
| 2.4.4 | `GET /api/hazards/bbox` | `?sw_lat&sw_lng&ne_lat&ne_lng` → hazards in bounding box (for map viewport) |
| 2.4.5 | `GET /api/hazards/heatmap` | Return clustered points for heatmap layer |
| 2.4.6 | Spatial index | `CREATE INDEX idx_hazard_geo ON hazards USING GIST(location)` |

---

### L3: 2.5 Statistics & Reports

| # | Task | Details |
|---|------|---------|
| 2.5.1 | `GET /api/stats/overview` | Total hazards, by type, by severity, by status |
| 2.5.2 | `GET /api/stats/trends` | Hazards per day/week/month (time series data) |
| 2.5.3 | `GET /api/stats/worst-roads` | Top 10 roads/areas by hazard density |
| 2.5.4 | `GET /api/reports/generate` | Generate PDF/CSV report for a date range |
| 2.5.5 | Report content | Summary stats + worst areas + hazard list + map screenshot |

---

### L3: 2.6 Auth (Basic)

| # | Task | Details |
|---|------|---------|
| 2.6.1 | API key middleware | `X-API-Key` header for write endpoints |
| 2.6.2 | Public read access | Map view, hazard list, stats = no auth needed |
| 2.6.3 | Rate limiting | 30 detections/hour per API key (prevent abuse) |
| 2.6.4 | Key generation | Simple admin endpoint to generate API keys |

---

# L1.3: FRONTEND DASHBOARD

> Next.js 14 web app with interactive map, upload, stats

## L2 Breakdown

| # | L2 Component | Description |
|---|-------------|-------------|
| 3.1 | Project Setup | Next.js 14 + Tailwind + shadcn/ui |
| 3.2 | Layout & Navigation | App shell, sidebar/header, routing |
| 3.3 | Map View (Main Page) | Interactive Leaflet map with hazard markers |
| 3.4 | Upload & Detect | Drag-drop image upload, show detection results |
| 3.5 | Stats Dashboard | Charts, numbers, trends |
| 3.6 | Hazard Detail View | Single hazard page with all info |
| 3.7 | Reports Page | Generate and download reports |

---

### L3: 3.1 Project Setup

| # | Task | Details |
|---|------|---------|
| 3.1.1 | `create-next-app` | Next.js 14, App Router, TypeScript, Tailwind |
| 3.1.2 | Install shadcn/ui | `npx shadcn-ui@latest init` + needed components |
| 3.1.3 | Install map lib | `react-leaflet` + `leaflet` + types |
| 3.1.4 | Install chart lib | `recharts` for stats charts |
| 3.1.5 | API client | Axios or fetch wrapper for backend calls |
| 3.1.6 | Types | Shared TypeScript types: `Hazard`, `Detection`, `Stats` |
| 3.1.7 | Env config | `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_MAPBOX_TOKEN` |

---

### L3: 3.2 Layout & Navigation

| # | Task | Details |
|---|------|---------|
| 3.2.1 | Root layout | Dark theme, sidebar navigation, responsive |
| 3.2.2 | Sidebar | Links: Map, Upload, Stats, Reports |
| 3.2.3 | Header | Logo "SadakAI", tagline, mobile menu toggle |
| 3.2.4 | Mobile responsive | Sidebar collapses to bottom nav on mobile |
| 3.2.5 | Loading states | Skeleton loaders for all data-fetching pages |
| 3.2.6 | Error boundaries | Graceful error display per page section |

**Routes:**
```
/              → Map view (default)
/upload        → Upload & detect
/stats         → Statistics dashboard
/reports       → Report generation
/hazard/[id]   → Hazard detail
```

---

### L3: 3.3 Map View (Main Page)

| # | Task | Details |
|---|------|---------|
| 3.3.1 | Map component | Leaflet map centered on India (default: Siliguri) |
| 3.3.2 | Tile layer | OpenStreetMap tiles (free, no API key needed) |
| 3.3.3 | Hazard markers | Color-coded by severity: green/yellow/red |
| 3.3.4 | Marker clustering | Cluster nearby markers at low zoom levels |
| 3.3.5 | Marker popup | Click marker → show: type, severity, date, thumbnail |
| 3.3.6 | Heatmap layer | Toggle heatmap overlay showing hazard density |
| 3.3.7 | Filter sidebar | Filter by: hazard type, severity, date range, status |
| 3.3.8 | Viewport loading | Fetch hazards only for current map viewport (bbox query) |
| 3.3.9 | Legend | Color legend for severity levels |
| 3.3.10 | Geolocation | "My Location" button to center map on user |

---

### L3: 3.4 Upload & Detect

| # | Task | Details |
|---|------|---------|
| 3.4.1 | Upload zone | Drag-and-drop area + file picker button |
| 3.4.2 | Image preview | Show uploaded image before detection |
| 3.4.3 | Location input | Optional: manual lat/lng or click-on-map picker |
| 3.4.4 | Detect button | Call `POST /api/detect`, show loading spinner |
| 3.4.5 | Results display | Show annotated image with bounding boxes |
| 3.4.6 | Detection list | Table: class, confidence %, severity, bbox size |
| 3.4.7 | Save to map | Button to save detection to the hazard database |
| 3.4.8 | Batch upload | Upload multiple images at once |
| 3.4.9 | History | Show recent uploads by this session |

---

### L3: 3.5 Stats Dashboard

| # | Task | Details |
|---|------|---------|
| 3.5.1 | Summary cards | Total hazards, critical count, fixed count, detection rate |
| 3.5.2 | Hazard by type chart | Pie/donut chart: potholes vs cracks vs speed breakers |
| 3.5.3 | Severity distribution | Bar chart: minor/moderate/critical counts |
| 3.5.4 | Trend line | Line chart: detections over time (daily/weekly) |
| 3.5.5 | Worst areas table | Top 10 areas ranked by hazard count |
| 3.5.6 | Status breakdown | Active vs Reported vs Fixed |
| 3.5.7 | Date range picker | Filter all stats by date range |

---

### L3: 3.6 Hazard Detail View

| # | Task | Details |
|---|------|---------|
| 3.6.1 | Hazard info card | Type, severity, status, date detected, coordinates |
| 3.6.2 | Original image | Full-size original uploaded image |
| 3.6.3 | Annotated image | Image with bounding boxes overlaid |
| 3.6.4 | Mini map | Small map showing exact location |
| 3.6.5 | Status update | Buttons: Mark as Reported / Mark as Fixed |
| 3.6.6 | Nearby hazards | List of other hazards within 500m |

---

### L3: 3.7 Reports Page

| # | Task | Details |
|---|------|---------|
| 3.7.1 | Report config form | Select: date range, area, hazard types, severity |
| 3.7.2 | Preview | Show report summary before download |
| 3.7.3 | Download CSV | Export filtered hazards as CSV |
| 3.7.4 | Download PDF | Generate PDF report with stats + map + hazard list |
| 3.7.5 | Share link | Generate shareable link for the report |

---

# L1.4: DATA LAYER

> PostgreSQL + PostGIS + Cloudflare R2

## L2 Breakdown

| # | L2 Component | Description |
|---|-------------|-------------|
| 4.1 | Database Schema | Tables, indexes, relationships |
| 4.2 | Migrations | Schema versioning with Alembic |
| 4.3 | Object Storage | R2 for images (original + annotated) |
| 4.4 | Seeding | Demo data for development/demo |

---

### L3: 4.1 Database Schema

| # | Task | Details |
|---|------|---------|

**Tables:**

```sql
-- Core hazard record
hazards
├── id              UUID PRIMARY KEY
├── type            ENUM('pothole', 'crack', 'speed_breaker', 'waterlogging')
├── severity        ENUM('minor', 'moderate', 'critical')
├── status          ENUM('active', 'reported', 'fixed') DEFAULT 'active'
├── confidence      FLOAT (model confidence 0-1)
├── bbox            JSONB {x1, y1, x2, y2}
├── location        GEOMETRY(Point, 4326) -- PostGIS
├── address         TEXT (reverse geocoded, nullable)
├── original_image  TEXT (R2 URL)
├── annotated_image TEXT (R2 URL)
├── danger_score    FLOAT (aggregate score for the image)
├── created_at      TIMESTAMP
├── updated_at      TIMESTAMP
└── deleted_at      TIMESTAMP (soft delete)

-- Detection session (one upload = one session, can have multiple hazards)
detection_sessions
├── id              UUID PRIMARY KEY
├── image_count     INT
├── total_hazards   INT
├── api_key_id      UUID FK (nullable)
├── created_at      TIMESTAMP
└── metadata        JSONB (device info, etc)

-- API keys
api_keys
├── id              UUID PRIMARY KEY
├── key_hash        TEXT (hashed key)
├── name            TEXT
├── is_active       BOOLEAN DEFAULT true
├── rate_limit      INT DEFAULT 30
├── created_at      TIMESTAMP
└── last_used_at    TIMESTAMP
```

| 4.1.1 | Create hazards table | As defined above with PostGIS geometry |
| 4.1.2 | Create detection_sessions table | Links multiple hazards to one upload |
| 4.1.3 | Create api_keys table | For basic auth |
| 4.1.4 | Spatial index | GIST index on hazards.location |
| 4.1.5 | Query indexes | Index on type, severity, status, created_at |
| 4.1.6 | Foreign keys | hazards.session_id → detection_sessions.id |

---

### L3: 4.2 Migrations

| # | Task | Details |
|---|------|---------|
| 4.2.1 | Alembic init | `alembic init migrations` |
| 4.2.2 | Initial migration | Create all tables from schema |
| 4.2.3 | Migration scripts | Auto-generate from SQLAlchemy models |
| 4.2.4 | Seed migration | Insert demo data for development |

---

### L3: 4.3 Object Storage

| # | Task | Details |
|---|------|---------|
| 4.3.1 | R2 bucket setup | Create `sadakai-images` bucket on Cloudflare R2 |
| 4.3.2 | Upload service | Python function: upload image → return public URL |
| 4.3.3 | Folder structure | `originals/{session_id}/{filename}`, `annotated/{session_id}/{filename}` |
| 4.3.4 | Image optimization | Compress to WebP before upload (reduce storage costs) |
| 4.3.5 | Cleanup job | Delete images for soft-deleted hazards after 30 days |

---

### L3: 4.4 Seeding (Demo Data)

| # | Task | Details |
|---|------|---------|
| 4.4.1 | Seed script | Generate 100+ fake hazards across Siliguri area |
| 4.4.2 | Realistic coordinates | Random points within Siliguri city bounds |
| 4.4.3 | Variety | Mix of types, severities, dates (last 3 months) |
| 4.4.4 | Sample images | Use 10-15 real pothole images from open datasets as demo thumbnails |

---

# DIRECTORY STRUCTURE

```
SadakAI/
├── README.md
├── PROJECT_BREAKDOWN.md          ← This file
│
├── model/                        ← Detection Engine (L1.1)
│   ├── notebooks/
│   │   └── train.ipynb           ← Colab training notebook
│   ├── data/
│   │   └── data.yaml             ← Dataset config
│   ├── weights/
│   │   ├── best.pt               ← Trained model
│   │   └── best.onnx             ← Exported model
│   └── scripts/
│       ├── prepare_dataset.py    ← Download + normalize datasets
│       └── evaluate.py           ← Test set evaluation
│
├── api/                          ← Backend (L1.2)
│   ├── main.py                   ← FastAPI app
│   ├── config.py                 ← Environment config
│   ├── routers/
│   │   ├── detect.py             ← Detection endpoints
│   │   ├── hazards.py            ← Hazard CRUD
│   │   ├── stats.py              ← Statistics
│   │   └── reports.py            ← Report generation
│   ├── services/
│   │   ├── detection.py          ← YOLO inference wrapper
│   │   ├── severity.py           ← Severity scoring logic
│   │   ├── storage.py            ← R2 upload/download
│   │   └── geocoding.py          ← Reverse geocoding
│   ├── models/
│   │   ├── database.py           ← SQLAlchemy models
│   │   └── schemas.py            ← Pydantic schemas
│   ├── migrations/               ← Alembic migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── dashboard/                    ← Frontend (L1.3)
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx          ← Map view
│   │   │   ├── upload/page.tsx
│   │   │   ├── stats/page.tsx
│   │   │   ├── reports/page.tsx
│   │   │   └── hazard/[id]/page.tsx
│   │   ├── components/
│   │   │   ├── map/
│   │   │   │   ├── HazardMap.tsx
│   │   │   │   ├── HazardMarker.tsx
│   │   │   │   ├── HeatmapLayer.tsx
│   │   │   │   └── MapFilters.tsx
│   │   │   ├── upload/
│   │   │   │   ├── DropZone.tsx
│   │   │   │   └── DetectionResults.tsx
│   │   │   ├── stats/
│   │   │   │   ├── SummaryCards.tsx
│   │   │   │   ├── HazardTypeChart.tsx
│   │   │   │   ├── SeverityChart.tsx
│   │   │   │   └── TrendLine.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   └── ui/               ← shadcn components
│   │   ├── lib/
│   │   │   ├── api.ts            ← API client
│   │   │   └── types.ts          ← Shared types
│   │   └── hooks/
│   │       ├── useHazards.ts
│   │       └── useStats.ts
│   ├── package.json
│   └── tailwind.config.ts
│
├── docker-compose.yml            ← PostgreSQL + PostGIS + API
├── .env.example
└── .gitignore
```

---

# IMPLEMENTATION ORDER

| Phase | What | L3 Tasks | Effort |
|-------|------|----------|--------|
| **1** | Dataset + Model | 1.1.1 → 1.2.9 | 3-4 days |
| **2** | API Foundation | 2.1.1 → 2.1.8, 4.1.1 → 4.2.4 | 2-3 days |
| **3** | Detection API | 1.3.1 → 1.4.6, 2.2.1 → 2.2.8 | 2-3 days |
| **4** | Hazard + Geo API | 2.3.1 → 2.4.6 | 2 days |
| **5** | Frontend Shell | 3.1.1 → 3.2.6 | 1-2 days |
| **6** | Map View | 3.3.1 → 3.3.10 | 2-3 days |
| **7** | Upload + Detect UI | 3.4.1 → 3.4.9 | 2 days |
| **8** | Stats + Reports | 3.5.1 → 3.7.5, 2.5.1 → 2.5.5 | 2-3 days |
| **9** | Seed + Polish | 4.4.1 → 4.4.4, auth, deploy | 2-3 days |

**Total estimated: ~20-25 days** (working alongside Fordel)

---

# TECH DECISIONS

| Decision | Choice | Why |
|----------|--------|-----|
| YOLO version | YOLOv8m | Best accuracy/speed balance, Ultralytics makes it dead simple |
| Backend | FastAPI | Python-native (same as YOLO), async, auto-docs |
| Frontend | Next.js 14 | Roki's strongest framework, SSR for SEO |
| Map library | Leaflet (react-leaflet) | Free, no API key, good enough for this use case |
| Database | PostgreSQL + PostGIS | Industry standard for geospatial, free on Railway |
| Storage | Cloudflare R2 | Free egress, S3-compatible, cheap |
| Charts | Recharts | React-native, simple API, good defaults |
| Deployment | Vercel + Railway | Free tiers, easy setup |
| Training | Google Colab | Free T4 GPU, no local GPU needed |

---

# VERIFICATION CHECKLIST

- [ ] Model mAP@50 ≥ 80% on test set
- [ ] API returns detections in < 2s per image
- [ ] Map renders 500+ markers without lag
- [ ] Upload → Detect → See on map works end-to-end
- [ ] Filters work (type, severity, date, location)
- [ ] Stats page shows accurate aggregated data
- [ ] Mobile responsive (all pages)
- [ ] Deployed and accessible via public URL
- [ ] README with architecture diagram + demo GIF
- [ ] Lighthouse ≥ 90 on dashboard

---

*Built for Roki Roy's portfolio - showing CV + full-stack + product thinking*
