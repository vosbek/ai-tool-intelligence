#!/bin/bash
# setup.sh - Complete setup script for AI Tool Intelligence Platform

set -e  # Exit on any error

echo "🚀 Setting up AI Tool Intelligence Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3 is required but not installed"
    print_info "Install Python 3.9+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(echo "$PYTHON_VERSION 3.9" | awk '{print ($1 >= $2)}')" != "1" ]; then
    print_error "Python 3.9+ required, found $PYTHON_VERSION"
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is required but not installed"
    print_info "Install Node.js 18+ from https://nodejs.org"
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is required but not installed"
    exit 1
fi

if ! command_exists git; then
    print_error "Git is required but not installed"
    exit 1
fi

print_status "Prerequisites check passed"

# Create project structure
print_info "Creating project structure..."
mkdir -p backend/{uploads,backups,logs}
mkdir -p frontend/src
mkdir -p scripts
mkdir -p docs
mkdir -p docker

# Backend setup
print_info "Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Create requirements.txt with all dependencies
cat > requirements.txt << 'EOF'
# Core Flask dependencies
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0

# Strands Agents (AI research)
strands-agents==0.1.0
strands-agents-tools==0.1.0

# Web scraping and parsing
beautifulsoup4==4.12.2
requests==2.31.0
lxml==4.9.3

# Data processing
pandas==2.1.0
numpy==1.24.3

# Configuration and utilities
python-dotenv==1.0.0
click==8.1.7
schedule==1.2.0
psutil==5.9.5

# Development and testing
pytest==7.4.0
pytest-flask==1.2.1
python-dateutil==2.8.2

# Production server
gunicorn==21.2.0
EOF

echo "Installing Python dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -r requirements.txt

print_status "Python dependencies installed"

# Create environment configuration template
cat > .env.example << 'EOF'
# AWS Configuration (REQUIRED for Bedrock)
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here

# Optional: GitHub token for enhanced API limits
GITHUB_TOKEN=your-github-token-here

# Optional: Database URL (defaults to SQLite)
DATABASE_URL=sqlite:///ai_tools.db

# Optional: Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Application settings
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
EOF

# Create default configuration
cat > config.json << 'EOF'
{
  "strands_agent": {
    "model_provider": "bedrock",
    "model_id": "us.anthropic.claude-3-7-sonnet-20241109-v1:0",
    "temperature": 0.1,
    "max_tokens": 4000,
    "timeout_seconds": 300,
    "rate_limit_delay": 5,
    "max_retries": 3
  },
  "batch_processing": {
    "max_concurrent_tools": 3,
    "daily_limit": 50,
    "weekly_limit": 200,
    "priority_categories": ["Agentic IDEs", "AI Code Assistants"],
    "exclude_weekends": false,
    "start_hour": 6,
    "end_hour": 22
  },
  "notifications": {
    "enable_email": false,
    "email_recipients": [],
    "enable_slack": false,
    "slack_webhook_url": "",
    "alert_on_failures": true,
    "daily_summary": true,
    "weekly_report": true
  },
  "debug_mode": true,
  "log_level": "INFO",
  "data_retention_days": 90,
  "backup_enabled": true
}
EOF

print_status "Backend configuration created"

# Frontend setup
print_info "Setting up React frontend..."
cd ../frontend

# Check if we need to create React app
if [ ! -f "package.json" ]; then
    echo "Creating React application..."
    npx create-react-app . --template typescript
    
    # Wait for creation to complete
    sleep 5
fi

# Install additional frontend dependencies
echo "Installing frontend dependencies..."
npm install axios recharts lucide-react date-fns

# Add proxy to package.json for development
python3 << 'EOF'
import json

try:
    with open('package.json', 'r') as f:
        package_data = json.load(f)
    
    package_data['proxy'] = 'http://localhost:5000'
    
    with open('package.json', 'w') as f:
        json.dump(package_data, f, indent=2)
    
    print("✅ Frontend configuration updated")
except Exception as e:
    print(f"❌ Error updating package.json: {e}")
EOF

print_status "Frontend setup complete"

# Scripts setup
print_info "Setting up utility scripts..."
cd ../scripts

# Create startup script
cat > start.sh << 'EOF'
#!/bin/bash
# start.sh - Start the AI Tool Intelligence platform

echo "🚀 Starting AI Tool Intelligence Platform..."

# Check if backend dependencies are installed
if [ ! -d "../backend/venv" ]; then
    echo "❌ Backend not set up. Run ./setup.sh first"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "../frontend/node_modules" ]; then
    echo "❌ Frontend not set up. Run ./setup.sh first"
    exit 1
fi

# Start backend
echo "Starting Flask backend..."
cd ../backend
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env from template - PLEASE CONFIGURE YOUR AWS CREDENTIALS!"
    cp .env.example .env
    echo ""
    echo "🔧 IMPORTANT: Edit backend/.env with your AWS credentials before using the research features"
    echo ""
fi

python app.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting React frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo ""
echo "✅ Platform started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:5000"
echo ""
echo "📖 Next steps:"
echo "1. Configure AWS credentials in backend/.env"
echo "2. Enable Claude 3.7 Sonnet access in AWS Bedrock console"
echo "3. Open http://localhost:3000 to start adding tools"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait
EOF

chmod +x start.sh

# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
# monitor.sh - Monitor system status

echo "📊 AI Tool Intelligence System Status"
echo "====================================="

cd ../backend
if [ -d "venv" ]; then
    source venv/bin/activate
    python config.py status
else
    echo "❌ Backend not set up. Run ./setup.sh first"
fi
EOF

chmod +x monitor.sh

# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
# backup.sh - Backup system data

echo "🗄️ Creating system backup..."

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="../backend/backups/backup_$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

cd ../backend

# Backup database if it exists
if [ -f "ai_tools.db" ]; then
    cp ai_tools.db "$BACKUP_DIR/"
    echo "✅ Database backed up"
fi

# Backup configuration
if [ -f "config.json" ]; then
    cp config.json "$BACKUP_DIR/"
    echo "✅ Configuration backed up"
fi

# Backup environment template (without secrets)
if [ -f ".env" ]; then
    grep -v "SECRET\|PASSWORD\|TOKEN\|KEY" .env > "$BACKUP_DIR/env_template" 2>/dev/null || true
    echo "✅ Environment template backed up"
fi

# Create backup info
cat > "$BACKUP_DIR/backup_info.txt" << EOF
Backup created: $(date)
Platform version: MVP
Database: $([ -f "ai_tools.db" ] && echo "SQLite $(du -h ai_tools.db 2>/dev/null | cut -f1)" || echo "Not found")
EOF

echo "✅ Backup created: $BACKUP_DIR"
EOF

chmod +x backup.sh

# Create research management script
cat > research.sh << 'EOF'
#!/bin/bash
# research.sh - Manage research operations

cd ../backend
if [ ! -d "venv" ]; then
    echo "❌ Backend not set up. Run ./setup.sh first"
    exit 1
fi

source venv/bin/activate

case "$1" in
    "status")
        python config.py research
        ;;
    "failed")
        python config.py failed
        ;;
    "retry")
        python config.py retry
        ;;
    "process")
        if [ -z "$2" ]; then
            echo "Usage: ./research.sh process <tool-names>"
            echo "Example: ./research.sh process 'Cursor,GitHub Copilot'"
            exit 1
        fi
        python batch_processor.py process "$2"
        ;;
    "category")
        if [ -z "$2" ]; then
            echo "Usage: ./research.sh category <category-name>"
            echo "Example: ./research.sh category 'Agentic IDEs'"
            exit 1
        fi
        python batch_processor.py category "$2"
        ;;
    "scheduler")
        echo "Starting research scheduler..."
        python batch_processor.py scheduler
        ;;
    *)
        echo "Usage: ./research.sh <command>"
        echo ""
        echo "Commands:"
        echo "  status    - Show research queue status"
        echo "  failed    - List failed tools"
        echo "  retry     - Retry all failed tools"
        echo "  process   - Process specific tools"
        echo "  category  - Process tools in category"
        echo "  scheduler - Start automated scheduler"
        echo ""
        echo "Examples:"
        echo "  ./research.sh status"
        echo "  ./research.sh process 'Cursor,GitHub Copilot'"
        echo "  ./research.sh category 'Agentic IDEs'"
        ;;
esac
EOF

chmod +x research.sh

print_status "Scripts setup complete"

# Test backend setup
print_info "Testing backend setup..."
cd ../backend
source venv/bin/activate

# Test basic imports
python3 << 'EOF'
try:
    from strands import Agent
    from strands.models import BedrockModel
    from strands_tools import http_request
    print("✅ Strands Agents imported successfully")
except ImportError as e:
    print(f"❌ Strands Agents import failed: {e}")
    exit(1)

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    print("✅ Flask dependencies imported successfully")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    print_status "Backend dependencies verified"
else
    print_error "Backend dependency verification failed"
    exit 1
fi

# Final setup message
cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure AWS credentials:"
echo "   cp backend/.env.example backend/.env"
echo "   nano backend/.env  # Add your AWS credentials"
echo ""
echo "2. Enable AWS Bedrock access:"
echo "   - Go to AWS Bedrock Console → Model access"
echo "   - Request access for Claude 3.7 Sonnet in us-west-2"
echo "   - Wait for approval (usually instant)"
echo ""
echo "3. Start the platform:"
echo "   ./scripts/start.sh"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "🔧 Useful commands:"
echo "   ./scripts/start.sh      # Start the platform"
echo "   ./scripts/monitor.sh    # Check system status"
echo "   ./scripts/backup.sh     # Create backup"
echo "   ./scripts/research.sh   # Manage research"
echo ""
echo "📖 For detailed documentation, see README.md"
echo ""
print_warning "Remember to configure your AWS credentials in backend/.env before using research features!"
