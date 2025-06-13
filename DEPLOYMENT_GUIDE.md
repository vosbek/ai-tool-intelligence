# AI Tool Intelligence Platform - Comprehensive Deployment Guide

> **Enterprise-grade deployment guide for production environments**

This guide provides detailed instructions for deploying the AI Tool Intelligence Platform in production environments across different platforms and architectures.

## 📋 **Deployment Overview**

The AI Tool Intelligence Platform is a complete enterprise system consisting of:

- **Backend API**: Flask application with all enterprise features
- **Frontend Dashboard**: React-based admin and monitoring interface
- **Database**: SQLite (development) or PostgreSQL/MySQL (production)
- **Real-time Monitoring**: Built-in system health and performance monitoring
- **Admin Interface**: Complete administrative control and data management
- **Alert System**: Multi-channel notifications and monitoring

## 🎯 **Deployment Options**

### **Option 1: Docker Deployment (Recommended)**
- **Best for**: Production environments, easy scaling, consistent deployments
- **Setup Time**: 15-30 minutes
- **Complexity**: Low to Medium

### **Option 2: Manual Deployment**
- **Best for**: Development, custom environments, detailed control
- **Setup Time**: 30-60 minutes
- **Complexity**: Medium

### **Option 3: Cloud Deployment**
- **Best for**: High availability, scalability, managed infrastructure
- **Setup Time**: 45-90 minutes
- **Complexity**: Medium to High

---

## 🐳 **Option 1: Docker Deployment (Recommended)**

### **Prerequisites**
- Docker 20.10+ and Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space
- Network access for container downloads

### **Step 1: Prepare Environment**

```bash
# Clone repository
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# Create production environment file
cp backend/.env.example .env.production

# Edit production configuration
nano .env.production
```

**Production Environment Configuration:**
```bash
# Core Configuration
DATABASE_URL=postgresql://username:password@postgres:5432/ai_tools_prod
SECRET_KEY=your-super-secure-production-key-here
FLASK_ENV=production

# AWS Configuration (Required)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Feature Configuration
ENHANCED_FEATURES_ENABLED=true
ENABLE_REAL_TIME_MONITORING=true
ENABLE_MONITORING=true
MONITORING_INTERVAL_SECONDS=60

# Security & Logging
LOG_DIR=/app/logs
LOG_LEVEL=INFO
SKIP_AWS_VALIDATION=false

# Alert Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-notifications@company.com
SMTP_PASSWORD=your-app-specific-password
SMTP_USE_TLS=true

# Slack Integration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Performance Configuration
MAX_CONCURRENT_TOOLS=5
API_RATE_LIMIT=100
BATCH_SIZE_LIMIT=50
```

### **Step 2: Production Docker Configuration**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15-alpine
    container_name: ai-tools-postgres
    environment:
      POSTGRES_DB: ai_tools_prod
      POSTGRES_USER: ai_tools_user
      POSTGRES_PASSWORD: secure_password_change_me
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ai_tools_user -d ai_tools_prod"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis (for caching and session storage)
  redis:
    image: redis:7-alpine
    container_name: ai-tools-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: ai-tools-backend
    env_file:
      - .env.production
    environment:
      - DATABASE_URL=postgresql://ai_tools_user:secure_password_change_me@postgres:5432/ai_tools_prod
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "5000:5000"
    volumes:
      - ./logs:/app/logs
      - ./backups:/app/backups
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: ai-tools-frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://backend:5000
      - REACT_APP_ENV=production
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: ai-tools-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  # Monitoring (Prometheus)
  prometheus:
    image: prom/prometheus:latest
    container_name: ai-tools-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

  # Monitoring Dashboard (Grafana)
  grafana:
    image: grafana/grafana:latest
    container_name: ai-tools-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin_password_change_me
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    name: ai-tools-network
```

### **Step 3: Production Dockerfiles**

**Backend Dockerfile.prod:**
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Set permissions
RUN chmod +x docker-entrypoint.sh

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start application
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

**Frontend Dockerfile.prod:**
```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.frontend.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### **Step 4: Deploy Production Environment**

```bash
# Deploy all services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Initialize database
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app import app, db
from migrations.migrate_to_enhanced_schema import run_migration
with app.app_context():
    db.create_all()
    run_migration()
    print('Database initialized')
"
```

### **Step 5: Verify Deployment**

```bash
# Health checks
curl http://localhost/api/health
curl -H "X-Admin-User: admin" http://localhost/api/admin/dashboard
curl -H "X-Monitor-User: admin" http://localhost/api/monitoring/health

# Access interfaces
# Frontend: http://localhost
# Admin API: http://localhost/api/admin/*
# Monitoring: http://localhost/api/monitoring/*
# Grafana: http://localhost:3001 (admin/admin_password_change_me)
# Prometheus: http://localhost:9090
```

---

## 🔧 **Option 2: Manual Deployment**

### **Prerequisites**
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.10+ and Node.js 18+
- PostgreSQL 13+ or MySQL 8+
- Nginx or Apache
- SSL certificates (Let's Encrypt recommended)

### **Step 1: System Preparation**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx certbot python3-certbot-nginx git curl

# Create application user
sudo useradd -m -s /bin/bash ai-tools
sudo usermod -aG sudo ai-tools
```

### **Step 2: Database Setup**

```bash
# PostgreSQL setup
sudo -u postgres psql

-- Create database and user
CREATE DATABASE ai_tools_prod;
CREATE USER ai_tools_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_tools_prod TO ai_tools_user;
ALTER USER ai_tools_user CREATEDB;
\q

# Test connection
psql -h localhost -U ai_tools_user -d ai_tools_prod -c "SELECT version();"
```

### **Step 3: Application Deployment**

```bash
# Switch to application user
sudo su - ai-tools

# Clone repository
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create production configuration
cp .env.example .env.production
nano .env.production

# Configure environment variables (same as Docker example above)

# Initialize database
python -c "
from app import app, db
from migrations.migrate_to_enhanced_schema import run_migration
with app.app_context():
    db.create_all()
    run_migration()
    print('Database initialized')
"

# Frontend setup
cd ../frontend
npm install
npm run build
```

### **Step 4: Process Management (Systemd)**

**Backend Service (`/etc/systemd/system/ai-tools-backend.service`):**
```ini
[Unit]
Description=AI Tools Intelligence Platform Backend
After=network.target postgresql.service

[Service]
Type=exec
User=ai-tools
Group=ai-tools
WorkingDirectory=/home/ai-tools/ai-tool-intelligence/backend
Environment=PATH=/home/ai-tools/ai-tool-intelligence/backend/venv/bin
EnvironmentFile=/home/ai-tools/ai-tool-intelligence/backend/.env.production
ExecStart=/home/ai-tools/ai-tool-intelligence/backend/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable ai-tools-backend
sudo systemctl start ai-tools-backend
sudo systemctl status ai-tools-backend
```

### **Step 5: Nginx Configuration**

**Site Configuration (`/etc/nginx/sites-available/ai-tools`):**
```nginx
upstream backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Frontend
    location / {
        root /home/ai-tools/ai-tool-intelligence/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }

    # WebSocket support (if needed)
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Logs
    access_log /var/log/nginx/ai-tools-access.log;
    error_log /var/log/nginx/ai-tools-error.log;
}
```

```bash
# Enable site and restart nginx
sudo ln -s /etc/nginx/sites-available/ai-tools /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## ☁️ **Option 3: Cloud Deployment**

### **AWS Deployment**

#### **Infrastructure as Code (Terraform)**

**main.tf:**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "ai_tools_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "ai-tools-vpc"
  }
}

# Subnets
resource "aws_subnet" "public_subnet_1" {
  vpc_id                  = aws_vpc.ai_tools_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "ai-tools-public-1"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.ai_tools_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "ai-tools-public-2"
  }
}

resource "aws_subnet" "private_subnet_1" {
  vpc_id            = aws_vpc.ai_tools_vpc.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "ai-tools-private-1"
  }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id            = aws_vpc.ai_tools_vpc.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "ai-tools-private-2"
  }
}

# RDS Database
resource "aws_db_instance" "ai_tools_db" {
  identifier = "ai-tools-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true
  
  db_name  = "ai_tools_prod"
  username = "ai_tools_user"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.ai_tools_db_subnet_group.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "ai-tools-final-snapshot"
  
  tags = {
    Name = "ai-tools-database"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "ai_tools_cluster" {
  name = "ai-tools-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Application Load Balancer
resource "aws_lb" "ai_tools_alb" {
  name               = "ai-tools-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]

  enable_deletion_protection = false

  tags = {
    Name = "ai-tools-alb"
  }
}
```

#### **ECS Task Definitions**

**backend-task.json:**
```json
{
  "family": "ai-tools-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "ai-tools-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ai-tools-backend:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:ssm:region:account:parameter/ai-tools/database-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:ssm:region:account:parameter/ai-tools/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-tools-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/api/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### **Google Cloud Platform Deployment**

#### **Cloud Run Deployment**

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-tools-backend backend/

gcloud run deploy ai-tools-backend \
    --image gcr.io/PROJECT_ID/ai-tools-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars FLASK_ENV=production \
    --set-secrets DATABASE_URL=ai-tools-db-url:latest \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10

# Build and deploy frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-tools-frontend frontend/

gcloud run deploy ai-tools-frontend \
    --image gcr.io/PROJECT_ID/ai-tools-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 80
```

### **Azure Deployment**

#### **Azure Container Instances**

```bash
# Create resource group
az group create --name ai-tools-rg --location eastus

# Create container registry
az acr create --resource-group ai-tools-rg --name aitoolsregistry --sku Basic

# Build and push images
az acr build --registry aitoolsregistry --image ai-tools-backend backend/
az acr build --registry aitoolsregistry --image ai-tools-frontend frontend/

# Deploy container group
az container create \
    --resource-group ai-tools-rg \
    --name ai-tools-app \
    --registry-login-server aitoolsregistry.azurecr.io \
    --registry-username $(az acr credential show --name aitoolsregistry --query username -o tsv) \
    --registry-password $(az acr credential show --name aitoolsregistry --query passwords[0].value -o tsv) \
    --image aitoolsregistry.azurecr.io/ai-tools-backend:latest \
    --cpu 1 \
    --memory 2 \
    --ports 5000 \
    --environment-variables FLASK_ENV=production
```

---

## 🔒 **Security Configuration**

### **SSL/TLS Setup**

```bash
# Let's Encrypt SSL
sudo certbot --nginx -d your-domain.com

# Or use custom SSL certificates
sudo cp your-cert.pem /etc/ssl/certs/
sudo cp your-key.pem /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/your-key.pem
```

### **Firewall Configuration**

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw deny 5000   # Block direct backend access

# Fail2ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### **Environment Security**

```bash
# Secure environment files
chmod 600 .env.production
chown ai-tools:ai-tools .env.production

# Database security
sudo -u postgres psql -c "ALTER USER ai_tools_user WITH PASSWORD 'new_secure_password';"

# Application secrets
python -c "import secrets; print(secrets.token_urlsafe(32))"  # Generate SECRET_KEY
```

---

## 📊 **Monitoring & Logging**

### **Log Management**

```bash
# Logrotate configuration
sudo nano /etc/logrotate.d/ai-tools

/home/ai-tools/ai-tool-intelligence/backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ai-tools ai-tools
    postrotate
        systemctl reload ai-tools-backend
    endscript
}
```

### **Monitoring Setup**

#### **Prometheus Metrics**

Add to `backend/app.py`:
```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('app_request_duration_seconds', 'Request latency')

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
```

#### **Health Checks**

```bash
# Create health check script
cat > /home/ai-tools/health-check.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:5000/api/health || exit 1
curl -f http://localhost/api/admin/dashboard -H "X-Admin-User: healthcheck" || exit 1
curl -f http://localhost/api/monitoring/health -H "X-Monitor-User: healthcheck" || exit 1
EOF

chmod +x /home/ai-tools/health-check.sh

# Add to crontab
echo "*/5 * * * * /home/ai-tools/health-check.sh" | crontab -
```

---

## 🔄 **Backup & Recovery**

### **Database Backup**

```bash
# Automated backup script
cat > /home/ai-tools/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ai-tools/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ai_tools_backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

pg_dump -h localhost -U ai_tools_user -d ai_tools_prod > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /home/ai-tools/backup-db.sh

# Schedule daily backups
echo "0 2 * * * /home/ai-tools/backup-db.sh" | crontab -
```

### **Application Backup**

```bash
# Full application backup
tar -czf ai-tools-backup-$(date +%Y%m%d).tar.gz \
    --exclude=backend/venv \
    --exclude=frontend/node_modules \
    --exclude=backend/logs \
    ai-tool-intelligence/
```

### **Recovery Process**

```bash
# Database recovery
gunzip ai_tools_backup_YYYYMMDD_HHMMSS.sql.gz
psql -h localhost -U ai_tools_user -d ai_tools_prod < ai_tools_backup_YYYYMMDD_HHMMSS.sql

# Application recovery
tar -xzf ai-tools-backup-YYYYMMDD.tar.gz
# Follow deployment steps to reconfigure
```

---

## 🚀 **Performance Optimization**

### **Database Optimization**

```sql
-- PostgreSQL optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();

-- Create indexes for performance
CREATE INDEX CONCURRENTLY idx_tool_changes_detected_at ON tool_changes(detected_at);
CREATE INDEX CONCURRENTLY idx_tools_processing_status ON tools(processing_status);
CREATE INDEX CONCURRENTLY idx_data_quality_reports_entity ON data_quality_reports(entity_type, entity_id);
```

### **Application Optimization**

```python
# Add to backend/config.py
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_POOL_TIMEOUT = 20
SQLALCHEMY_POOL_RECYCLE = 1800
SQLALCHEMY_MAX_OVERFLOW = 20

# Enable query optimization
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### **Nginx Optimization**

```nginx
# Add to nginx configuration
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

# Caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
location /api/ {
    limit_req zone=api burst=20 nodelay;
}
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Database Connection Errors**
```bash
# Check database status
sudo systemctl status postgresql
psql -h localhost -U ai_tools_user -d ai_tools_prod -c "SELECT version();"

# Check connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

#### **High Memory Usage**
```bash
# Monitor memory
htop
free -h

# Check application memory
ps aux | grep python
ps aux | grep gunicorn

# Adjust worker processes
# In systemd service file: --workers 2 (instead of 4)
```

#### **SSL Certificate Issues**
```bash
# Renew Let's Encrypt certificates
sudo certbot renew --dry-run
sudo certbot renew

# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout | grep "Not After"
```

#### **Application Logs**
```bash
# View application logs
tail -f /home/ai-tools/ai-tool-intelligence/backend/logs/application.log
journalctl -u ai-tools-backend -f

# Check error logs
tail -f /var/log/nginx/ai-tools-error.log
```

### **Performance Issues**

#### **Slow Database Queries**
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### **High CPU Usage**
```bash
# Check CPU usage by process
top -p $(pgrep -f gunicorn | tr '\n' ',' | sed 's/,$//')

# Check for stuck processes
ps aux | grep -E "(python|gunicorn)" | grep -v grep
```

---

## 📞 **Support & Maintenance**

### **Regular Maintenance Tasks**

1. **Daily**: Check application health and logs
2. **Weekly**: Review monitoring metrics and alerts
3. **Monthly**: Update dependencies and security patches
4. **Quarterly**: Performance review and optimization

### **Maintenance Scripts**

```bash
# Daily health check
#!/bin/bash
echo "=== Daily Health Check ===" >> /var/log/ai-tools-health.log
date >> /var/log/ai-tools-health.log
curl -s http://localhost:5000/api/health | jq . >> /var/log/ai-tools-health.log
systemctl is-active ai-tools-backend >> /var/log/ai-tools-health.log
echo "=========================" >> /var/log/ai-tools-health.log
```

### **Emergency Contacts**

- **System Administrator**: [Your contact info]
- **Database Administrator**: [DBA contact]
- **Application Support**: [Dev team contact]
- **Infrastructure Team**: [Infrastructure contact]

---

**🎉 Your AI Tool Intelligence Platform is now deployed and ready for production use!**

This comprehensive deployment guide covers all aspects of production deployment. Choose the deployment option that best fits your infrastructure and requirements. Remember to regularly monitor, backup, and maintain your deployment for optimal performance and reliability.