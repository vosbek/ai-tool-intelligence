#!/bin/bash
#
# Status script for AI Tool Intelligence Platform on Ubuntu
# 
# This script shows the current status of all services

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

echo -e "${BLUE}📊 AI Tool Intelligence Platform Status${NC}"
echo "========================================"

# Check backend status
print_step "Checking backend status..."
if [ -f "$PROJECT_ROOT/ubuntu/pids/backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/ubuntu/pids/backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        print_success "Backend running (PID: $BACKEND_PID)"
        
        # Check backend health
        if curl -s "http://localhost:5000/api/health" >/dev/null 2>&1; then
            print_success "Backend health check: OK"
            
            # Get backend info
            BACKEND_INFO=$(curl -s "http://localhost:5000/api/health" 2>/dev/null)
            if [ -n "$BACKEND_INFO" ]; then
                echo "  Backend info: $BACKEND_INFO"
            fi
        else
            print_warning "Backend health check: FAILED"
        fi
        
        # Check port usage
        BACKEND_PORT=$(lsof -ti:5000 2>/dev/null | head -1)
        if [ -n "$BACKEND_PORT" ]; then
            print_info "Port 5000: In use by PID $BACKEND_PORT"
        fi
    else
        print_error "Backend PID file exists but process not running"
        rm -f "$PROJECT_ROOT/ubuntu/pids/backend.pid"
    fi
else
    print_error "Backend not running"
fi

echo

# Check frontend status
print_step "Checking frontend status..."
if [ -f "$PROJECT_ROOT/ubuntu/pids/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/ubuntu/pids/frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        print_success "Frontend running (PID: $FRONTEND_PID)"
        
        # Check frontend availability
        if curl -s "http://localhost:3000" >/dev/null 2>&1; then
            print_success "Frontend health check: OK"
        else
            print_warning "Frontend health check: FAILED"
        fi
        
        # Check port usage
        FRONTEND_PORT=$(lsof -ti:3000 2>/dev/null | head -1)
        if [ -n "$FRONTEND_PORT" ]; then
            print_info "Port 3000: In use by PID $FRONTEND_PORT"
        fi
    else
        print_error "Frontend PID file exists but process not running"
        rm -f "$PROJECT_ROOT/ubuntu/pids/frontend.pid"
    fi
else
    print_error "Frontend not running"
fi

echo

# Check system resources
print_step "System resources..."
MEMORY_USAGE=$(free -h | grep '^Mem:' | awk '{print $3 "/" $2}')
DISK_USAGE=$(df -h "$PROJECT_ROOT" | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')
LOAD_AVERAGE=$(uptime | awk -F'load average:' '{print $2}')

print_info "Memory usage: $MEMORY_USAGE"
print_info "Disk usage: $DISK_USAGE"
print_info "Load average:$LOAD_AVERAGE"

echo

# Check log files
print_step "Log files..."
if [ -f "$PROJECT_ROOT/ubuntu/logs/backend.log" ]; then
    BACKEND_LOG_SIZE=$(du -h "$PROJECT_ROOT/ubuntu/logs/backend.log" | cut -f1)
    BACKEND_LOG_LINES=$(wc -l < "$PROJECT_ROOT/ubuntu/logs/backend.log")
    print_info "Backend log: $BACKEND_LOG_SIZE ($BACKEND_LOG_LINES lines)"
    
    # Show last few lines if there are recent errors
    if tail -n 10 "$PROJECT_ROOT/ubuntu/logs/backend.log" | grep -i error >/dev/null; then
        print_warning "Recent errors found in backend log:"
        tail -n 10 "$PROJECT_ROOT/ubuntu/logs/backend.log" | grep -i error | head -3
    fi
else
    print_info "Backend log: Not found"
fi

if [ -f "$PROJECT_ROOT/ubuntu/logs/frontend.log" ]; then
    FRONTEND_LOG_SIZE=$(du -h "$PROJECT_ROOT/ubuntu/logs/frontend.log" | cut -f1)
    FRONTEND_LOG_LINES=$(wc -l < "$PROJECT_ROOT/ubuntu/logs/frontend.log")
    print_info "Frontend log: $FRONTEND_LOG_SIZE ($FRONTEND_LOG_LINES lines)"
    
    # Show last few lines if there are recent errors
    if tail -n 10 "$PROJECT_ROOT/ubuntu/logs/frontend.log" | grep -i error >/dev/null; then
        print_warning "Recent errors found in frontend log:"
        tail -n 10 "$PROJECT_ROOT/ubuntu/logs/frontend.log" | grep -i error | head -3
    fi
else
    print_info "Frontend log: Not found"
fi

echo

# Check configuration
print_step "Configuration..."
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    if grep -q "^AWS_ACCESS_KEY_ID=" "$PROJECT_ROOT/backend/.env" && grep -q "^AWS_SECRET_ACCESS_KEY=" "$PROJECT_ROOT/backend/.env"; then
        print_success "AWS credentials configured"
    else
        print_warning "AWS credentials not configured"
    fi
else
    print_warning "Environment file not found"
fi

if [ -f "$PROJECT_ROOT/ubuntu/config.json" ]; then
    print_success "Ubuntu configuration exists"
else
    print_warning "Ubuntu configuration not found"
fi

echo

# Check if setup is complete
print_step "Setup status..."
if [ -d "$PROJECT_ROOT/backend/venv" ]; then
    print_success "Backend virtual environment exists"
else
    print_error "Backend virtual environment missing - run ./ubuntu/setup.sh"
fi

if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    print_success "Frontend dependencies installed"
else
    print_error "Frontend dependencies missing - run ./ubuntu/setup.sh"
fi

echo

# Summary
print_step "Summary:"
BACKEND_STATUS="❌ STOPPED"
FRONTEND_STATUS="❌ STOPPED"

if [ -f "$PROJECT_ROOT/ubuntu/pids/backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/ubuntu/pids/backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        BACKEND_STATUS="✅ RUNNING"
    fi
fi

if [ -f "$PROJECT_ROOT/ubuntu/pids/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/ubuntu/pids/frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        FRONTEND_STATUS="✅ RUNNING"
    fi
fi

echo "Backend:  $BACKEND_STATUS"
echo "Frontend: $FRONTEND_STATUS"

if [[ "$BACKEND_STATUS" == *"RUNNING"* ]] && [[ "$FRONTEND_STATUS" == *"RUNNING"* ]]; then
    echo
    print_success "Platform is fully operational!"
    print_info "Access at: http://localhost:3000"
elif [[ "$BACKEND_STATUS" == *"STOPPED"* ]] && [[ "$FRONTEND_STATUS" == *"STOPPED"* ]]; then
    echo
    print_info "Platform is stopped. Use ./ubuntu/start.sh to start."
else
    echo
    print_warning "Platform is partially running. Use ./ubuntu/stop.sh then ./ubuntu/start.sh to restart."
fi