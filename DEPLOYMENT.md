# SadakAI Deployment Guide

This guide covers deploying SadakAI to production environments.

## 🏭 Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CDN (Cloudflare)                      │
└────────────────────────┬────────────────────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
    ┌────▼────┐                  ┌────▼────┐
    │ Vercel  │                  │ Railway │
    │Frontend │                  │  API    │
    └─────────┘                  └────┬────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
               ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
               │ Neon DB  │     │  R2     │     │ Sentry  │
               │(Postgres)│     │(Storage)│     │(Logs)   │
               └─────────┘     └─────────┘     └─────────┘
```

## 🚀 Quick Deploy

### Option 1: Vercel + Railway (Recommended)

#### 1. Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to dashboard
cd dashboard

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

Or connect your GitHub repository to Vercel:
1. Go to https://vercel.com
2. Import your repository
3. Configure:
   - Framework: Next.js
   - Build Command: npm run build
   - Output Directory: .next
4. Add environment variables
5. Deploy

#### 2. Deploy Backend to Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Create project
railway init

# Add PostgreSQL plugin
railway add -p postgres

# Deploy
railway up
```

Or use Railway's GitHub integration.

### Option 2: Docker Compose (Self-Hosted)

```bash
# Clone and configure
git clone https://github.com/your-username/SadakAI.git
cd SadakAI

# Edit environment
cp .env.example .env
nano .env

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## ⚙️ Environment Configuration

### Production Environment Variables

#### Backend (.env)

```env
# Database - Use PostgreSQL in production
DATABASE_URL=postgresql://user:password@host:5432/sadakai

# Cloudflare R2 Storage (recommended for production)
R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET=sadakai-images

# API Security
API_KEY=generate_strong_random_key

# Model Path
MODEL_PATH=/app/weights/best.pt
```

#### Frontend (.env)

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 🗄️ Database Setup

### Option 1: Neon (Serverless PostgreSQL)

1. Create account at https://neon.tech
2. Create new project
3. Copy connection string
4. Add to environment variables

### Option 2: Railway PostgreSQL

```bash
# Add PostgreSQL to Railway project
railway add -p postgres
```

### Option 3: Supabase

1. Create project at https://supabase.com
2. Get connection string from settings
3. Enable PostGIS extension:
   ```sql
   CREATE EXTENSION postgis;
   ```

## ☁️ Storage Setup

### Cloudflare R2 (Recommended - Free Egress)

1. Create Cloudflare account
2. Create R2 bucket
3. Get API credentials
4. Add to environment

### Alternative: AWS S3

```python
# Update storage service for S3
import boto3

s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name='us-east-1'
)
```

## 🔒 Security Checklist

- [ ] Enable HTTPS everywhere
- [ ] Set strong API keys
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Enable database encryption
- [ ] Set up monitoring (Sentry)
- [ ] Configure backups
- [ ] Use environment variables for secrets

## 📊 Monitoring

### Sentry Integration

```bash
# Install Sentry SDK
pip install sentry-sdk

# Configure in main.py
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1
)
```

### LogRocket

```bash
# Add to layout.tsx
import LogRocket from 'logrocket';
LogRocket.init('your-app-id');
```

## 🔄 CI/CD

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        run: |
          npm i -g vercel
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## 📈 Performance Optimization

### Frontend

1. **Enable Image Optimization**
   ```javascript
   // next.config.js
   images: {
     domains: ['your-bucket.r2.cloudflarestorage.com'],
   }
   ```

2. **Add Caching Headers**
   ```javascript
   // next.config.js
   async headers() {
     return [
       {
         source: '/:path*',
         headers: [
           { key: 'Cache-Control', value: 'public, max-age=3600' }
         ]
       }
     ]
   }
   ```

### Backend

1. **Enable Gzip Compression**
2. **Use Redis for Caching** (optional)
3. **Configure Worker Processes**
   ```bash
   gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## 🆘 Troubleshooting

### Common Issues

#### Frontend Build Fails

```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

#### API Returns 500

- Check logs: `railway logs`
- Verify DATABASE_URL
- Check model weights exist

#### Map Not Loading

- Verify API is accessible
- Check CORS settings
- Ensure map tiles accessible

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test database connection
4. Contact maintainer

## 🔄 Updating

### Frontend Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild
npm run build
```

### Backend Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild Docker image
docker-compose build api

# Restart services
docker-compose restart api
```

---

**Need help?** Open an issue on GitHub or contact the maintainer.
