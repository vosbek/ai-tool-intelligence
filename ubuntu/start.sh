#!/bin/bash
#
# Start script for AI Tool Intelligence Platform on Ubuntu
# 
# This script starts both the backend and frontend services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}🚀 Starting AI Tool Intelligence Platform...${NC}"

# Check if backend dependencies are installed
if [ ! -d "$PROJECT_ROOT/backend/venv" ]; then
    print_error "Backend not set up. Run ./ubuntu/setup.sh first"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    print_error "Frontend not set up. Run ./ubuntu/setup.sh first"
    exit 1
fi

# Create PID directory
mkdir -p "$PROJECT_ROOT/ubuntu/pids"

# Function to cleanup on exit
cleanup() {
    echo
    print_step "Stopping services..."
    
    # Stop backend
    if [ -f "$PROJECT_ROOT/ubuntu/pids/backend.pid" ]; then
        BACKEND_PID=$(cat "$PROJECT_ROOT/ubuntu/pids/backend.pid")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            kill "$BACKEND_PID" 2>/dev/null || true
            rm -f "$PROJECT_ROOT/ubuntu/pids/backend.pid"
        fi
    fi
    
    # Stop frontend
    if [ -f "$PROJECT_ROOT/ubuntu/pids/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_ROOT/ubuntu/pids/frontend.pid")
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            kill "$FRONTEND_PID" 2>/dev/null || true
            rm -f "$PROJECT_ROOT/ubuntu/pids/frontend.pid"
        fi
    fi
    
    print_success "Services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Start backend
print_step "Starting Flask backend..."
cd "$PROJECT_ROOT/backend"
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning "Creating .env from template - PLEASE CONFIGURE YOUR AWS CREDENTIALS!"
    cp .env.example .env
    echo
    print_info "🔧 IMPORTANT: Edit backend/.env with your AWS credentials before using the research features"
    echo
fi

# Start backend in background
python app.py > "$PROJECT_ROOT/ubuntu/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$PROJECT_ROOT/ubuntu/pids/backend.pid"
print_success "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
print_info "Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    print_error "Backend failed to start. Check logs:"
    tail -n 10 "$PROJECT_ROOT/ubuntu/logs/backend.log"
    exit 1
fi

# Test backend health
for i in {1..10}; do
    if curl -s "http://localhost:5000/api/health" >/dev/null 2>&1; then
        print_success "Backend health check passed"
        break
    fi
    if [ $i -eq 10 ]; then
        print_warning "Backend health check failed, but continuing..."
    fi
    sleep 1
done

# Start frontend
print_step "Starting React frontend..."
cd "$PROJECT_ROOT/frontend"

# Set environment variables for production build
export BROWSER=none  # Don't auto-open browser in terminal

npm start > "$PROJECT_ROOT/ubuntu/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$PROJECT_ROOT/ubuntu/pids/frontend.pid"
print_success "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to start
print_info "Waiting for frontend to initialize..."
sleep 10

# Check if frontend is running
if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    print_error "Frontend failed to start. Check logs:"
    tail -n 10 "$PROJECT_ROOT/ubuntu/logs/frontend.log"
    cleanup
    exit 1
fi

echo
print_success "Platform started successfully!"
echo
echo -e "${CYAN}🌐 Frontend: http://localhost:3000${NC}"
echo -e "${CYAN}🔌 Backend API: http://localhost:5000${NC}"
echo
print_info "📖 Next steps:"
print_info "1. Configure AWS credentials in backend/.env"
print_info "2. Enable Claude 3.5 Sonnet access in AWS Bedrock console"
print_info "3. Open http://localhost:3000 to start adding tools"
echo
print_info "📋 Log files:"
print_info "• Backend: ubuntu/logs/backend.log"
print_info "• Frontend: ubuntu/logs/frontend.log"
echo
print_warning "Press Ctrl+C to stop both services"

# Open browser if in desktop environment
if [ -n "$DISPLAY" ] && command -v xdg-open >/dev/null 2>&1; then
    sleep 2
    xdg-open "http://localhost:3000" 2>/dev/null &
fi

# Wait for processes
while kill -0 "$BACKEND_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do
    sleep 1
done

# If we get here, one of the processes died
print_error "One of the services stopped unexpectedly"
cleanup