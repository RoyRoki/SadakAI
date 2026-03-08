# SadakAI Dashboard

Next.js 14 frontend for the SadakAI road hazard detection platform.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## ⚙️ Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_MAP_CENTER_LAT` | Default map latitude | `26.7` |
| `NEXT_PUBLIC_MAP_CENTER_LNG` | Default map longitude | `88.4` |

## 📁 Project Structure

```
dashboard/
├── public/                  # Static assets
├── src/
│   ├── app/               # Next.js App Router
│   │   ├── layout.tsx     # Root layout
│   │   ├── page.tsx       # Map view (home)
│   │   ├── globals.css    # Global styles
│   │   ├── upload/        # Upload page
│   │   ├── stats/         # Statistics page
│   │   └── reports/       # Reports page
│   │
│   ├── components/        # React components
│   │   ├── layout/        # Layout components
│   │   │   └── Sidebar.tsx
│   │   ├── map/          # Map components
│   │   │   └── HazardMap.tsx
│   │   └── ui/           # UI components
│   │       └── Toast.tsx
│   │
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities
│   │   ├── api.ts        # API client
│   │   └── types.ts      # TypeScript types
│   │
│   └── styles/           # Additional styles
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 📱 Pages

### Map View (/)

The main page showing an interactive map with all reported hazards.

**Features:**
- Interactive Leaflet map centered on India
- Color-coded markers by severity (yellow/orange/red)
- Hazard type icons (🕳️裂凸💧)
- Click markers for details popup
- Filter by severity, type, and status
- My Location button (GPS)
- Refresh button
- Real-time hazard count

### Upload (/upload)

Page for uploading images and detecting road hazards.

**Features:**
- Drag and drop image upload
- File picker for image selection
- Camera capture for mobile devices
- Clipboard paste support
- GPS location detection
- Real-time detection results
- Hazard severity display
- Danger score calculation

### Statistics (/stats)

Dashboard showing comprehensive statistics and trends.

**Features:**
- Total hazards counter
- Critical hazards counter
- Fixed hazards counter
- Fix rate percentage
- Pie chart: hazards by type
- Bar chart: severity distribution
- Line chart: trends over time

### Reports (/reports)

Page for generating and downloading reports.

**Features:**
- Date range selection
- CSV export functionality

## 🧩 Components

### HazardMap

Interactive map component with markers and filtering.

```tsx
import HazardMap from "@/components/map/HazardMap";

// Usage
<HazardMap />
```

**Props:** None (fetches data from API)

### Sidebar

Navigation sidebar with mobile bottom navigation.

```tsx
import { Sidebar } from "@/components/layout/Sidebar";

// Usage
<Sidebar />
```

### Toast

Toast notification system for user feedback.

```tsx
import { useToast } from "@/components/ui/Toast";

// Usage
const { showToast } = useToast();
showToast("Operation successful!", "success");
```

## 🔌 API Client

The `lib/api.ts` file provides a typed API client:

```typescript
import { api } from "@/lib/api";

// Get hazards
const hazards = await api.getHazards({ page_size: 100 });

// Get single hazard
const hazard = await api.getHazard(id);

// Update hazard
await api.updateHazard(id, { status: "fixed" });

// Detect hazards
const result = await api.detectHazard(file, lat, lng);

// Get stats
const stats = await api.getStatsOverview();
```

## 🎨 Styling

The project uses Tailwind CSS for styling. See `tailwind.config.ts` for custom configuration.

### Custom Colors

```css
/* Available color classes */
.bg-primary      /* Highway yellow */
.bg-severity-minor    /* Yellow */
.bg-severity-moderate /* Orange */
.bg-severity-critical /* Red */
```

## 🧪 Testing

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Type check
npm run typecheck
```

## 🔧 Build & Deploy

### Build for Production

```bash
npm run build
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Or connect your GitHub repository to Vercel for automatic deployments.

## 📦 Dependencies

### Core
- **Next.js 14** - React framework
- **React 18** - UI library
- **TypeScript** - Type safety

### UI
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Recharts** - Charts
- **Leaflet/React-Leaflet** - Maps

### Utilities
- **Axios** - HTTP client
- **clsx** - ClassName utility
- **tailwind-merge** - Tailwind merge

See `package.json` for full list.

## 🌐 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome for Android)

## 📄 License

MIT License - see parent project README.
