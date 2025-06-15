#!/bin/bash
#
# Complete setup script for AI Tool Intelligence Platform on Ubuntu
# 
# This script sets up the AI Tool Intelligence Platform including Python backend, 
# React frontend, and all dependencies on Ubuntu systems.
#
# Usage:
#   ./setup.sh                 # Sets up entire platform with default settings
#   ./setup.sh --skip-python   # Skips Python installation check
#   ./setup.sh --skip-node     # Skips Node.js installation check
#   ./setup.sh --force         # Forces recreation of virtual environment

set -e  # Exit on any error

# Parse command line arguments
SKIP_PYTHON=false
SKIP_NODE=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-python)
            SKIP_PYTHON=true
            shift
            ;;
        --skip-node)
            SKIP_NODE=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo "Unknown option $1"
            echo "Usage: $0 [--skip-python] [--skip-node] [--force]"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions for colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    python3 --version 2>/dev/null | sed 's/Python //' | head -1
}

# Function to get Node.js version
get_node_version() {
    node --version 2>/dev/null | sed 's/v//' | head -1
}

# Function to compare versions
version_compare() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

echo -e "${GREEN}"
cat << 'EOF'
🚀 AI Tool Intelligence Platform Setup for Ubuntu
================================================================
This script will set up your AI development tool research platform.

Prerequisites that will be checked:
- Python 3.9+ with pip
- Node.js 18+ with npm
- Git
- curl and wget

The script will:
1. ✅ Check all prerequisites
2. 🐍 Set up Python virtual environment and dependencies  
3. ⚛️  Set up React frontend with dependencies
4. 📁 Create necessary directories and files
5. 🔧 Configure environment templates
6. 📜 Install Ubuntu management scripts

EOF
echo -e "${NC}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_step "Checking prerequisites..."

# Check Python
if [ "$SKIP_PYTHON" = false ]; then
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        print_info "Install with: sudo apt update && sudo apt install python3 python3-pip python3-venv"
        exit 1
    fi

    PYTHON_VERSION=$(get_python_version)
    if ! version_compare "$PYTHON_VERSION" "3.9.0"; then
        print_error "Python 3.9+ required, found Python $PYTHON_VERSION"
        print_info "Install newer Python with: sudo apt install python3.11 python3.11-venv python3.11-pip"
        exit 1
    fi
    print_success "Python $PYTHON_VERSION found"

    # Check pip
    if ! python3 -m pip --version >/dev/null 2>&1; then
        print_error "pip not found. Install with: sudo apt install python3-pip"
        print_info "Or try: python3 -m ensurepip --default-pip"
        exit 1
    fi
    print_success "pip found"
fi

# Check Node.js
if [ "$SKIP_NODE" = false ]; then
    if ! command_exists node; then
        print_error "Node.js is required but not installed"
        print_info "Install with: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
        exit 1
    fi

    NODE_VERSION=$(get_node_version)
    if ! version_compare "$NODE_VERSION" "18.0.0"; then
        print_error "Node.js 18+ required, found Node.js $NODE_VERSION"
        print_info "Install newer Node.js with: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
        exit 1
    fi
    print_success "Node.js $NODE_VERSION found"

    # Check npm
    if ! command_exists npm; then
        print_error "npm not found. Reinstall Node.js"
        exit 1
    fi
    print_success "npm found"
fi

# Check Git
if ! command_exists git; then
    print_error "Git not found. Install with: sudo apt install git"
    exit 1
fi
print_success "Git found"

# Check curl and wget
if ! command_exists curl; then
    print_error "curl not found. Install with: sudo apt install curl"
    exit 1
fi

if ! command_exists wget; then
    print_error "wget not found. Install with: sudo apt install wget"
    exit 1
fi

print_success "Prerequisites check passed"

# Create project structure
print_step "Creating project structure..."
DIRECTORIES=(
    "$PROJECT_ROOT/backend/uploads"
    "$PROJECT_ROOT/backend/backups"
    "$PROJECT_ROOT/backend/logs"
    "$PROJECT_ROOT/frontend/src"
    "$PROJECT_ROOT/ubuntu/logs"
    "$PROJECT_ROOT/docs"
)

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_info "Created directory: $dir"
    fi
done

# Backend setup
print_step "Setting up Python backend..."
cd "$PROJECT_ROOT/backend"

# Create virtual environment
if [ ! -d "venv" ] || [ "$FORCE" = true ]; then
    if [ "$FORCE" = true ] && [ -d "venv" ]; then
        print_info "Removing existing virtual environment..."
        rm -rf venv
    fi
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        print_info "Try installing: sudo apt install python3-venv"
        exit 1
    fi
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
if [ ! -f "venv/bin/activate" ]; then
    print_error "Virtual environment activation script not found"
    print_info "Virtual environment may not have been created properly"
    exit 1
fi
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
print_info "Installing Python dependencies (this may take a few minutes)..."
{
    # First upgrade pip and install basic build tools
    python -m pip install --upgrade pip setuptools wheel
    
    # Install AWS SDK first (required for Strands Agents)
    pip install boto3 botocore
    
    # Install Strands Agents separately with better error handling
    print_info "Installing Strands Agents SDK..."
    pip install strands-agents strands-agents-tools
    
    # Install remaining dependencies
    pip install -r requirements.txt
    
    print_success "Python dependencies installed successfully"
} || {
    print_error "Failed to install Python dependencies"
    print_info "Common solutions:"
    print_info "1. Ensure AWS credentials are available"
    print_info "2. Try: pip install --upgrade pip setuptools wheel"
    print_info "3. Check internet connection"
    print_info "4. Some packages may require build-essential: sudo apt install build-essential"
    exit 1
}

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_warning "IMPORTANT: Edit backend/.env with your AWS credentials before using research features!"
fi

# Test basic imports
print_info "Testing Python dependencies..."
{
    python -c "from flask import Flask; from flask_sqlalchemy import SQLAlchemy; print('✅ Flask dependencies OK')"
    
    # Test Strands Agents with better error reporting
    python -c "
try:
    from strands import Agent
    from strands.models import BedrockModel
    print('✅ Strands Agents core available')
    try:
        from strands_tools import calculator
        print('✅ Strands Agents tools available')
    except ImportError as e:
        print('⚠️  Strands tools partially available:', str(e))
except ImportError as e:
    print('❌ Strands Agents not available:', str(e))
"
} || {
    print_warning "Some dependencies may have issues, but basic functionality should work"
}

print_success "Backend setup complete"

# Frontend setup  
print_step "Setting up React frontend..."
cd "$PROJECT_ROOT/frontend"

# Install frontend dependencies
print_info "Installing frontend dependencies..."
{
    npm install
    print_success "Frontend dependencies installed successfully"
} || {
    print_error "Failed to install frontend dependencies"
    print_info "Try running: npm cache clean --force"
    exit 1
}

# Add proxy configuration to package.json if not present
if [ -f "package.json" ]; then
    # Use node to update package.json
    node -e "
const fs = require('fs');
const path = 'package.json';
const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));
if (!pkg.proxy) {
    pkg.proxy = 'http://localhost:5000';
    fs.writeFileSync(path, JSON.stringify(pkg, null, 2));
    console.log('Added proxy configuration to package.json');
}
"
fi

print_success "Frontend setup complete"

# Create Ubuntu-specific configuration
print_step "Creating Ubuntu configuration..."
cd "$PROJECT_ROOT/ubuntu"

# Create configuration file
cat > config.json << EOF
{
    "project_root": "$PROJECT_ROOT",
    "python_path": "$(which python3)",
    "node_path": "$(which node)",
    "npm_path": "$(which npm)",
    "backend_port": 5000,
    "frontend_port": 3000,
    "auto_open_browser": true,
    "log_level": "INFO",
    "created": "$(date -Iseconds)"
}
EOF
print_info "Created Ubuntu configuration file"

# Test backend startup
print_step "Testing backend startup..."
cd "$PROJECT_ROOT/backend"
source venv/bin/activate

# Start backend in background for testing
python app.py &
TEST_PID=$!
sleep 3

# Test health endpoint
if kill -0 $TEST_PID 2>/dev/null; then
    if curl -s "http://localhost:5000/api/health" | grep -q "healthy"; then
        print_success "Backend test successful"
    else
        print_warning "Backend started but health check failed"
    fi
    
    # Stop test process
    kill $TEST_PID 2>/dev/null || true
    wait $TEST_PID 2>/dev/null || true
else
    print_warning "Backend test failed - check logs when you start the platform"
fi

# Final instructions
cd "$PROJECT_ROOT"

echo
echo -e "${GREEN}"
cat << 'EOF'
🎉 Setup Complete!
================================================================

Your AI Tool Intelligence Platform is ready to use!

📋 Next Steps:
1. Configure AWS credentials:
   • Edit: backend/.env
   • Add your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   • Set AWS_REGION=us-west-2

2. Enable AWS Bedrock access:
   • Go to AWS Bedrock Console → Model access
   • Request access for Claude 3.5 Sonnet in us-west-2 region
   • Wait for approval (usually instant)

3. Start the platform:
   ./ubuntu/start.sh

4. Open your browser:
   http://localhost:3000

🔧 Available Ubuntu Scripts:
   ./ubuntu/start.sh         # Start the platform
   ./ubuntu/stop.sh          # Stop all services  
   ./ubuntu/status.sh        # Check system status
   ./ubuntu/backup.sh        # Create system backup
   ./ubuntu/research.sh      # Manage research operations
   ./ubuntu/logs.sh          # View application logs
   ./ubuntu/reset.sh         # Reset to clean state

📖 Documentation:
   • README.md - Full documentation
   • backend/.env.example - Configuration template
   • frontend/package.json - Frontend dependencies

💡 Quick Start:
   1. ./ubuntu/start.sh
   2. Open http://localhost:3000
   3. Click "Add New Tool"
   4. Enter tool info and click "Research"

EOF
echo -e "${NC}"

print_warning "Remember to configure your AWS credentials in backend/.env before using research features!"

# Ask about creating desktop shortcut
echo
read -p "Create desktop shortcut for easy access? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    DESKTOP_DIR="$HOME/Desktop"
    if [ -d "$DESKTOP_DIR" ]; then
        cat > "$DESKTOP_DIR/AI Tool Intelligence.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AI Tool Intelligence Platform
Comment=Start AI Tool Intelligence Platform
Exec=gnome-terminal --working-directory="$PROJECT_ROOT" --command="./ubuntu/start.sh"
Icon=applications-development
Terminal=true
Categories=Development;
EOF
        chmod +x "$DESKTOP_DIR/AI Tool Intelligence.desktop"
        print_success "Desktop shortcut created"
    else
        print_warning "Desktop directory not found, skipping shortcut creation"
    fi
fi

print_success "Setup completed successfully! Run ./ubuntu/start.sh to begin."