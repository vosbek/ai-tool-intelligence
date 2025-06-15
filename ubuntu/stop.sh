#!/bin/bash
#
# Stop script for AI Tool Intelligence Platform on Ubuntu
# 
# This script stops both the backend and frontend services

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

echo -e "${BLUE}🛑 Stopping AI Tool Intelligence Platform...${NC}"

STOPPED_SERVICES=0

# Stop backend
if [ -f "$PROJECT_ROOT/ubuntu/pids/backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/ubuntu/pids/backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        print_step "Stopping backend (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            print_warning "Backend not responding, force killing..."
            kill -9 "$BACKEND_PID" 2>/dev/null || true
        fi
        
        print_success "Backend stopped"
        STOPPED_SERVICES=$((STOPPED_SERVICES + 1))
    else
        print_info "Backend not running"
    fi
    rm -f "$PROJECT_ROOT/ubuntu/pids/backend.pid"
else
    print_info "Backend PID file not found"
fi

# Stop frontend
if [ -f "$PROJECT_ROOT/ubuntu/pids/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/ubuntu/pids/frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        print_step "Stopping frontend (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            print_warning "Frontend not responding, force killing..."
            kill -9 "$FRONTEND_PID" 2>/dev/null || true
        fi
        
        print_success "Frontend stopped"
        STOPPED_SERVICES=$((STOPPED_SERVICES + 1))
    else
        print_info "Frontend not running"
    fi
    rm -f "$PROJECT_ROOT/ubuntu/pids/frontend.pid"
else
    print_info "Frontend PID file not found"
fi

# Also check for any lingering Python/Node processes on our ports
print_step "Checking for lingering processes..."

# Check port 5000 (backend)
BACKEND_PIDS=$(lsof -ti:5000 2>/dev/null || true)
if [ -n "$BACKEND_PIDS" ]; then
    print_warning "Found processes on port 5000, killing them..."
    echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null || true
fi

# Check port 3000 (frontend)
FRONTEND_PIDS=$(lsof -ti:3000 2>/dev/null || true)
if [ -n "$FRONTEND_PIDS" ]; then
    print_warning "Found processes on port 3000, killing them..."
    echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null || true
fi

# Clean up PID directory
rm -rf "$PROJECT_ROOT/ubuntu/pids"

if [ $STOPPED_SERVICES -gt 0 ]; then
    print_success "All services stopped successfully"
else
    print_info "No services were running"
fi

echo
print_info "Platform stopped. Use ./ubuntu/start.sh to start again."