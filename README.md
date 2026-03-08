# SadakAI 🚧

> **Real-time Indian Road Hazard Detection & Crowdsourced Mapping Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)](https://fastapi.tiangolo.com/)

SadakAI is a comprehensive road hazard detection and mapping platform designed specifically for Indian roads. It uses computer vision (YOLOv8) to detect potholes, cracks, speed breakers, and waterlogging from images uploaded by users.

![SadakAI Dashboard](https://via.placeholder.com/800x400?text=SadakAI+Dashboard)

## ✨ Features

### Core Features
- **🗺️ Interactive Map** - View all reported hazards on an interactive Leaflet map
- **📸 Image Detection** - Upload images for AI-powered hazard detection
- **📊 Statistics Dashboard** - Comprehensive stats and trends visualization
- **📄 Report Generation** - Export hazard data as CSV reports
- **📱 Mobile-First** - Fully responsive PWA design
- **🔍 Advanced Filtering** - Filter by severity, type, and status

### Technical Features
- **🤖 YOLOv8 Model** - State-of-the-art object detection
- **🗄️ PostgreSQL + PostGIS** - Geospatial database for location data
- **☁️ Cloudflare R2** - S3-compatible object storage
- **🐳 Docker** - Containerized deployment
- **⚡ FastAPI** - High-performance async backend
- **🌐 Next.js 14** - Modern React frontend

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14)                    │
│  Dashboard │ Map View │ Upload │ Reports │ Stats            │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  /detect │ /hazards │ /reports │ /stats │ /upload           │
└───────────┬──────────┬──────────────────┬─────────────────────┘
            │          │                  │
       ┌────▼────┐ ┌───▼────────┐  ┌─────▼──────┐
       │ YOLOv8  │ │ PostgreSQL │  │ Cloudflare │
       │ Model   │ │ + PostGIS  │  │ R2 Storage │
       └─────────┘ └────────────┘  └────────────┘
```

## 📁 Project Structure

```
SadakAI/
├── model/                    # Machine Learning
│   ├── data/               # Dataset configuration
│   ├── notebooks/          # Training notebooks (Colab)
│   ├── scripts/           # Dataset preparation scripts
│   └── weights/           # Trained model weights
│
├── api/                    # Backend API (FastAPI)
│   ├── config.py          # Configuration settings
│   ├── main.py            # Application entry point
│   ├── models/            # Database models & schemas
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── seed.py            # Demo data seeder
│   └── requirements.txt   # Python dependencies
│
├── dashboard/              # Frontend (Next.js 14)
│   ├── src/
│   │   ├── app/          # App router pages
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom React hooks
│   │   └── lib/          # Utilities & API client
│   └── package.json
│
├── docker-compose.yml      # Docker orchestration
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+** (with PostGIS extension)
- **Docker & Docker Compose** (optional)

### Option 1: Local Development

#### 1. Clone the repository
```bash
git clone https://github.com/your-username/SadakAI.git
cd SadakAI
```

#### 2. Set up the backend

```bash
cd api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run the API server
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

#### 3. Set up the frontend

```bash
cd dashboard

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Option 2: Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📖 API Endpoints

### Detection
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/detect` | Upload image for hazard detection |
| POST | `/api/detect/batch` | Batch detection for multiple images |

### Hazards
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hazards` | List all hazards (paginated) |
| GET | `/api/hazards/{id}` | Get hazard details |
| PATCH | `/api/hazards/{id}` | Update hazard status |
| DELETE | `/api/hazards/{id}` | Delete hazard (soft delete) |
| GET | `/api/hazards/nearby` | Get hazards near a location |
| GET | `/api/hazards/bbox` | Get hazards in bounding box |

### Statistics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats/overview` | Get overview statistics |
| GET | `/api/stats/trends` | Get hazard trends over time |
| GET | `/api/stats/worst-roads` | Get worst areas by hazard count |

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `api/` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sadakai

# Cloudflare R2 Storage (optional)
R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET=sadakai-images

# API
API_KEY=your_api_key_here
MODEL_PATH=model/weights/best.pt

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤖 Training the Model

### Dataset Preparation

The model is trained on publicly available road damage datasets:

| Dataset | Source | Description |
|---------|--------|-------------|
| RDD2022 | IEEE Big Data Cup | 47,000+ images |
| Indian Pothole Dataset | Roboflow Universe | 1,500+ Indian potholes |
| Speed Breaker Dataset | Roboflow Universe | 500+ speed breakers |

### Training Steps

1. Download datasets from the sources above
2. Place images in `model/data/images/{train,val,test}/`
3. Run dataset preparation:
   ```bash
   python model/scripts/prepare_dataset.py
   ```
4. Open `model/notebooks/train.ipynb` in Google Colab
5. Run the training notebook with T4 GPU
6. Download trained weights to `model/weights/best.pt`

### Supported Hazard Classes

- `pothole` - Road potholes
- `crack` - Road cracks
- `speed_breaker` - Speed breakers
- `waterlogging` - Water accumulation

## 📱 Mobile Features

- **📍 GPS Location** - Auto-detect current location
- **📸 Camera Capture** - Take photos directly
- **📋 Clipboard Paste** - Paste images from clipboard
- **🖼️ Photo Library** - Select from gallery

## 🧪 Testing

### Backend Tests
```bash
cd api
pytest
```

### Frontend Tests
```bash
cd dashboard
npm test
```

## 🚢 Deployment

### Production Build

```bash
# Frontend
cd dashboard
npm run build

# Backend
cd api
pip install -r requirements.txt
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Recommended Hosting

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| Vercel | Frontend | ✅ |
| Railway/Render | Backend | ✅ |
| Neon/Supabase | PostgreSQL | ✅ |
| Cloudflare R2 | Storage | ✅ |

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) for details.

## 🙏 Acknowledgments

- [Ultralytics](https://ultralytics.com/) for YOLOv8
- [Road Damage Dataset](https://github.com/sekilab/RoadDamageDataset) creators
- [OpenStreetMap](https://www.openstreetmap.org/) for map tiles
- All contributors and testers

## 📧 Contact

- **Author:** Roki Roy
- **Email:** rokiroydev@gmail.com
- **GitHub:** https://github.com/RoyRoki/SadakAI
- **Website:** https://rokiroy.in

---

<div align="center">

**Made with ❤️ for safer Indian roads**

</div>
