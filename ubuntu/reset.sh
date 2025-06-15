#!/bin/bash
#
# Reset script for AI Tool Intelligence Platform on Ubuntu
# 
# This script resets the platform to a clean state

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

echo -e "${RED}🔄 AI Tool Intelligence Platform Reset${NC}"
echo "======================================"

print_warning "This will reset the platform to a clean state!"
print_warning "The following will be removed:"
print_warning "• All tool data and research results"
print_warning "• Application logs"
print_warning "• Temporary files and caches"
print_warning "• Virtual environment (will be recreated)"

echo
print_info "The following will be preserved:"
print_info "• Your AWS credentials (.env file)"
print_info "• Configuration files"
print_info "• Backup files"
print_info "• Source code"

echo
read -p "Are you sure you want to reset the platform? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Reset cancelled"
    exit 0
fi

echo
read -p "Create backup before reset? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    print_step "Creating backup..."
    "$SCRIPT_DIR/backup.sh"
    if [ $? -eq 0 ]; then
        print_success "Backup created successfully"
    else
        print_error "Backup failed. Continue with reset? (y/N): "
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo
print_step "Starting reset process..."

# Stop all services first
print_step "Stopping all services..."
"$SCRIPT_DIR/stop.sh"

# Remove database
print_step "Removing database..."
if [ -f "$PROJECT_ROOT/backend/ai_tools.db" ]; then
    rm -f "$PROJECT_ROOT/backend/ai_tools.db"
    print_success "Database removed"
else
    print_info "Database not found"
fi

# Remove logs
print_step "Clearing logs..."
if [ -d "$PROJECT_ROOT/ubuntu/logs" ]; then
    rm -rf "$PROJECT_ROOT/ubuntu/logs"
    mkdir -p "$PROJECT_ROOT/ubuntu/logs"
    print_success "Logs cleared"
fi

if [ -d "$PROJECT_ROOT/backend/logs" ]; then
    rm -rf "$PROJECT_ROOT/backend/logs"
    mkdir -p "$PROJECT_ROOT/backend/logs"
    print_success "Backend logs cleared"
fi

# Remove PID files
print_step "Cleaning up PID files..."
if [ -d "$PROJECT_ROOT/ubuntu/pids" ]; then
    rm -rf "$PROJECT_ROOT/ubuntu/pids"
    print_success "PID files removed"
fi

# Remove Python virtual environment
print_step "Removing Python virtual environment..."
if [ -d "$PROJECT_ROOT/backend/venv" ]; then
    rm -rf "$PROJECT_ROOT/backend/venv"
    print_success "Virtual environment removed"
else
    print_info "Virtual environment not found"
fi

# Remove Node.js cache and modules (optional)
echo
read -p "Remove frontend dependencies (will need to reinstall)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Removing frontend dependencies..."
    if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
        rm -rf "$PROJECT_ROOT/frontend/node_modules"
        print_success "Frontend dependencies removed"
    fi
    
    if [ -f "$PROJECT_ROOT/frontend/package-lock.json" ]; then
        rm -f "$PROJECT_ROOT/frontend/package-lock.json"
        print_success "Package lock file removed"
    fi
fi

# Clean npm cache
if command -v npm >/dev/null 2>&1; then
    print_step "Cleaning npm cache..."
    npm cache clean --force >/dev/null 2>&1
    print_success "npm cache cleaned"
fi

# Remove temporary files
print_step "Removing temporary files..."
find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -name "*.log" -delete 2>/dev/null || true
print_success "Temporary files removed"

# Preserve configuration files by backing them up temporarily
TEMP_CONFIG_DIR="/tmp/ai_tool_intelligence_config_$$"
mkdir -p "$TEMP_CONFIG_DIR"

if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    cp "$PROJECT_ROOT/backend/.env" "$TEMP_CONFIG_DIR/"
    print_info "Preserved .env file"
fi

if [ -f "$PROJECT_ROOT/backend/config.json" ]; then
    cp "$PROJECT_ROOT/backend/config.json" "$TEMP_CONFIG_DIR/"
    print_info "Preserved config.json file"
fi

if [ -f "$PROJECT_ROOT/ubuntu/config.json" ]; then
    cp "$PROJECT_ROOT/ubuntu/config.json" "$TEMP_CONFIG_DIR/"
    print_info "Preserved ubuntu config file"
fi

echo
print_step "Platform reset completed!"
print_success "The platform has been reset to a clean state"

echo
print_info "Next steps:"
print_info "1. Run ./ubuntu/setup.sh to reinstall dependencies"
print_info "2. Configure AWS credentials if needed"
print_info "3. Start the platform with ./ubuntu/start.sh"

# Restore configuration files
if [ -f "$TEMP_CONFIG_DIR/.env" ]; then
    mv "$TEMP_CONFIG_DIR/.env" "$PROJECT_ROOT/backend/"
    print_success "Restored .env file"
fi

if [ -f "$TEMP_CONFIG_DIR/config.json" ]; then
    mv "$TEMP_CONFIG_DIR/config.json" "$PROJECT_ROOT/backend/"
    print_success "Restored config.json file"
fi

if [ -f "$TEMP_CONFIG_DIR/config.json" ]; then
    mv "$TEMP_CONFIG_DIR/config.json" "$PROJECT_ROOT/ubuntu/"
    print_success "Restored ubuntu config file"
fi

# Clean up temporary directory
rm -rf "$TEMP_CONFIG_DIR"

echo
read -p "Run setup now to reinstall dependencies? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    print_step "Running setup..."
    "$SCRIPT_DIR/setup.sh"
else
    print_info "Run ./ubuntu/setup.sh when ready to reinstall dependencies"
fi

print_success "Reset operation completed!"