# Deployment Guide - Predictive Maintenance System

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Deploy to Render](#deploy-to-render)
4. [Deploy to Railway](#deploy-to-railway)
5. [Deploy to AWS](#deploy-to-aws)
6. [Production Checklist](#production-checklist)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Pre-Deployment Checklist

- [ ] All tests passing locally
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] Security audit completed
- [ ] API documentation reviewed
- [ ] Frontend build tested
- [ ] Docker images build successfully
- [ ] No sensitive data in repository
- [ ] SSL/TLS certificates obtained
- [ ] Backup strategy defined

---

## Environment Setup

### Production Environment Variables

**Backend (.env)**
```env
# Environment
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/db_name
DB_ECHO=false
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=50

# API
API_TITLE=Predictive Maintenance API
API_VERSION=1.0.0
CORS_ORIGINS=https://yourdomain.com

# Security
JWT_SECRET_KEY=your-very-long-random-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Logging
LOG_LEVEL=INFO

# Features
ENABLE_DOCS=false  # Disable Swagger in production
ENABLE_ML_PREDICTIONS=false
```

**Frontend (.env)**
```env
VITE_API_URL=https://api.yourdomain.com/api/v1
VITE_APP_NAME=Predictive Maintenance System
VITE_THEME_DEFAULT=light
VITE_ENABLE_ANALYTICS=false
```

---

## Deploy to Render

### Step 1: Prepare Repository

```bash
# Ensure .gitignore includes sensitive files
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "node_modules/" >> .gitignore
echo ".venv/" >> .gitignore

git add .gitignore
git commit -m "Update .gitignore for production"
git push
```

### Step 2: Create PostgreSQL Database on Render

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "PostgreSQL"
3. Configure:
   - Name: `predictive-maintenance-db`
   - Region: Select closest to your users
   - PostgreSQL Version: 15
4. Click "Create Database"
5. Copy connection string from dashboard

### Step 3: Deploy Backend Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `predictive-maintenance-api`
   - **Environment**: Docker
   - **Root Directory**: `backend`
   - **Build Command**: (leave default)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Click "Advanced" and add environment variables:
   ```
   DATABASE_URL=<paste PostgreSQL connection string>
   ENVIRONMENT=production
   JWT_SECRET_KEY=<generate random key>
   DEBUG=false
   CORS_ORIGINS=https://<your-frontend-domain>
   ```
5. Select "Free" or "Paid" plan
6. Click "Create Web Service"

### Step 4: Deploy Frontend Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `predictive-maintenance-ui`
   - **Environment**: Docker
   - **Root Directory**: `frontend`
   - **Build Command**: (leave default)
   - **Start Command**: (leave default)
4. Click "Advanced" and add environment variables:
   ```
   VITE_API_URL=https://<your-api-domain>/api/v1
   ```
5. Click "Create Web Service"

### Step 5: Database Initialization

```bash
# SSH into Render PostgreSQL (via Web Service shell)
# Or use psql locally:
psql postgresql://user:password@host:5432/db_name < database/SCHEMA.sql
```

### Step 6: Configure Custom Domain

1. In Render dashboard, go to your service
2. Click "Settings"
3. Under "Custom Domain", enter your domain
4. Update DNS records with CNAME provided

---

## Deploy to Railway

### Step 1: Install Railway CLI

```bash
npm i -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
# Opens browser for authentication
```

### Step 3: Create Project

```bash
cd predictive-maintenance
railway init
# Select "Create a new project"
# Give it a name: "predictive-maintenance"
```

### Step 4: Add PostgreSQL

```bash
railway add
# Select "PostgreSQL"
# Select "PostgreSQL" again to confirm
```

### Step 5: Configure Services

```bash
# Create railway.json in root
cat > railway.json << 'EOF'
{
  "name": "predictive-maintenance",
  "services": [
    {
      "name": "backend",
      "root": "./backend",
      "buildCommand": "pip install -r requirements.txt",
      "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    },
    {
      "name": "frontend",
      "root": "./frontend",
      "buildCommand": "npm install && npm run build",
      "startCommand": "npm run preview"
    }
  ]
}
EOF
```

### Step 6: Deploy

```bash
railway up
```

This will:
- Deploy PostgreSQL
- Deploy Backend
- Deploy Frontend
- Provide public URLs for each service

### Step 7: Set Environment Variables

```bash
railway env add DATABASE_URL postgresql://...
railway env add JWT_SECRET_KEY your-secret-key
railway env add VITE_API_URL https://your-api-url/api/v1
railway up
```

---

## Deploy to AWS

### Using EC2 + RDS

#### Step 1: Create RDS PostgreSQL Database
```bash
# AWS Console → RDS → Create Database
# Engine: PostgreSQL 15
# DB Instance class: db.t3.micro (free tier)
# Storage: 20 GB
# Public accessibility: Yes
# Security group: Allow 5432 from app security group
```

#### Step 2: Create EC2 Instance
```bash
# AWS Console → EC2 → Launch Instance
# AMI: Ubuntu Server 22.04 LTS
# Instance type: t3.micro (free tier)
# Security group: Allow 80, 443, 8000

# Connect via SSH
ssh -i key.pem ubuntu@instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip docker.io docker-compose git nginx

# Add user to docker group
sudo usermod -aG docker ubuntu

# Clone repository
cd /home/ubuntu
git clone <your-repo-url>
cd predictive-maintenance
```

#### Step 3: Deploy Application
```bash
# Create .env file
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit with actual values
nano backend/.env
nano frontend/.env

# Build and run with docker-compose
docker-compose -f docker/docker-compose.yml up -d
```

#### Step 4: Configure Nginx
```bash
# Create nginx config
sudo tee /etc/nginx/sites-available/predictive-maintenance > /dev/null << 'EOF'
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/predictive-maintenance /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

#### Step 5: Enable HTTPS with Let's Encrypt
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
sudo systemctl restart nginx
```

---

## Production Checklist

### Security
- [ ] Change default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Enable database backups
- [ ] Rotate secrets regularly
- [ ] Use environment variables (never hardcode)
- [ ] Implement audit logging
- [ ] Regular security updates

### Performance
- [ ] Configure database connection pooling
- [ ] Enable API caching
- [ ] Optimize database queries
- [ ] Enable CDN for static assets
- [ ] Implement API rate limiting
- [ ] Monitor response times
- [ ] Set up database indexes
- [ ] Enable compression

### Reliability
- [ ] Set up automated backups
- [ ] Configure monitoring/alerting
- [ ] Implement health checks
- [ ] Set up error tracking (Sentry)
- [ ] Configure log aggregation
- [ ] Test disaster recovery
- [ ] Document runbooks
- [ ] Set up uptime monitoring

### Compliance
- [ ] Privacy policy documentation
- [ ] Data retention policies
- [ ] Encryption standards
- [ ] Access control policies
- [ ] Audit trail logging
- [ ] GDPR compliance (if applicable)
- [ ] Regular security audits
- [ ] Staff training

---

## Monitoring & Maintenance

### Set Up Monitoring

```bash
# Option 1: Sentry (Error Tracking)
pip install sentry-sdk
# Configure in app.main

# Option 2: DataDog / New Relic
# Follow provider-specific setup

# Option 3: Open Source Stack
# Prometheus + Grafana + Loki
```

### Database Backups

```bash
# Automatic backup script
# /home/ubuntu/backup.sh
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgresql"
DB_NAME="predictive_maintenance"
DB_USER="app_user"
DB_HOST="your-rds-endpoint"

mkdir -p $BACKUP_DIR

pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

# Schedule with cron
# 0 2 * * * /home/ubuntu/backup.sh
```

### Log Monitoring

```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Or with Render/Railway CLI
render logs <service-id>
railway logs
```

### Performance Monitoring

```sql
-- Check slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname != 'pg_catalog'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Update Strategy

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build

# Restart services (zero downtime rolling restart)
docker-compose up -d --no-deps --build
```

---

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
psql $DATABASE_URL

# Check connection pool
SELECT count(*) as available_connections FROM pg_stat_activity;
```

### High Memory Usage
```bash
# Check memory limits
docker stats

# Increase pool size in .env
DB_POOL_SIZE=50
```

### Slow API Responses
```bash
# Check database query performance
EXPLAIN ANALYZE SELECT * FROM machines WHERE status = 'active';

# Add indexes if needed
CREATE INDEX idx_machines_status ON machines(status);
```

### Deploy Failures
```bash
# Check application logs
docker-compose logs backend

# Check build output
docker build -t test ./backend

# Verify environment variables
docker-compose config
```

---

**Version**: 1.0.0  
**Last Updated**: May 2024
