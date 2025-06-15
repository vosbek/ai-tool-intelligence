#!/bin/bash
#
# Backup script for AI Tool Intelligence Platform on Ubuntu
# 
# This script creates a backup of system data and configuration

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

echo -e "${BLUE}🗄️  Creating AI Tool Intelligence Platform Backup...${NC}"

# Create backup directory with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$PROJECT_ROOT/backend/backups/backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

print_info "Backup directory: $BACKUP_DIR"

cd "$PROJECT_ROOT/backend"

# Function to safely copy file if it exists
safe_copy() {
    local src="$1"
    local dst="$2"
    local desc="$3"
    
    if [ -f "$src" ]; then
        cp "$src" "$dst"
        print_success "$desc backed up"
        return 0
    else
        print_warning "$desc not found: $src"
        return 1
    fi
}

# Function to safely copy directory if it exists
safe_copy_dir() {
    local src="$1"
    local dst="$2"
    local desc="$3"
    
    if [ -d "$src" ]; then
        cp -r "$src" "$dst"
        print_success "$desc backed up"
        return 0
    else
        print_warning "$desc not found: $src"
        return 1
    fi
}

# Backup database
print_step "Backing up database..."
safe_copy "ai_tools.db" "$BACKUP_DIR/ai_tools.db" "SQLite database"

# Backup configuration files
print_step "Backing up configuration..."
safe_copy "config.json" "$BACKUP_DIR/config.json" "Backend configuration"
safe_copy "../ubuntu/config.json" "$BACKUP_DIR/ubuntu_config.json" "Ubuntu configuration"

# Backup environment template (without secrets)
print_step "Backing up environment template..."
if [ -f ".env" ]; then
    # Create sanitized environment file (remove sensitive data)
    grep -v -E "SECRET|PASSWORD|TOKEN|KEY|CREDENTIAL" .env > "$BACKUP_DIR/env_template.txt" 2>/dev/null || true
    print_success "Environment template backed up (secrets excluded)"
else
    print_warning "Environment file not found"
fi

# Backup requirements files
print_step "Backing up dependency files..."
safe_copy "requirements.txt" "$BACKUP_DIR/requirements.txt" "Python requirements"
safe_copy "../frontend/package.json" "$BACKUP_DIR/package.json" "Frontend package.json"
safe_copy "../frontend/package-lock.json" "$BACKUP_DIR/package-lock.json" "Frontend package-lock.json"

# Backup logs (last 1000 lines only to avoid huge backups)
print_step "Backing up recent logs..."
mkdir -p "$BACKUP_DIR/logs"

if [ -f "../ubuntu/logs/backend.log" ]; then
    tail -n 1000 "../ubuntu/logs/backend.log" > "$BACKUP_DIR/logs/backend.log"
    print_success "Backend logs backed up (last 1000 lines)"
fi

if [ -f "../ubuntu/logs/frontend.log" ]; then
    tail -n 1000 "../ubuntu/logs/frontend.log" > "$BACKUP_DIR/logs/frontend.log"
    print_success "Frontend logs backed up (last 1000 lines)"
fi

# Backup any custom scripts or configurations
print_step "Backing up custom files..."
safe_copy_dir "../ubuntu" "$BACKUP_DIR/ubuntu_scripts" "Ubuntu scripts"

# Create backup manifest
print_step "Creating backup manifest..."
cat > "$BACKUP_DIR/backup_info.txt" << EOF
AI Tool Intelligence Platform Backup
====================================

Backup created: $(date)
Platform version: MVP
Ubuntu system: $(lsb_release -d 2>/dev/null | cut -f2 || echo "Unknown")
Backup location: $BACKUP_DIR

Database: $([ -f "ai_tools.db" ] && echo "SQLite $(du -h ai_tools.db 2>/dev/null | cut -f1)" || echo "Not found")
Python version: $(python3 --version 2>/dev/null || echo "Not found")
Node.js version: $(node --version 2>/dev/null || echo "Not found")

Backup contents:
$(ls -la "$BACKUP_DIR" 2>/dev/null | grep -v "^total" | tail -n +2)

System info:
- Hostname: $(hostname)
- Uptime: $(uptime)
- Disk usage: $(df -h "$PROJECT_ROOT" | tail -1)
- Memory: $(free -h | grep '^Mem:')

Restore instructions:
1. Stop the platform: ./ubuntu/stop.sh
2. Copy database: cp backup_*/ai_tools.db ../backend/
3. Copy configuration: cp backup_*/config.json ../backend/
4. Copy environment template: cp backup_*/env_template.txt ../backend/.env
5. Edit .env with your AWS credentials
6. Start platform: ./ubuntu/start.sh
EOF

print_success "Backup manifest created"

# Calculate backup size
print_step "Finalizing backup..."
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
FILE_COUNT=$(find "$BACKUP_DIR" -type f | wc -l)

print_success "Backup completed successfully!"
echo
print_info "Backup location: $BACKUP_DIR"
print_info "Backup size: $BACKUP_SIZE"
print_info "Files backed up: $FILE_COUNT"

# List backup contents
echo
print_step "Backup contents:"
ls -la "$BACKUP_DIR" | grep -v "^total"

echo
print_info "💡 Backup tips:"
print_info "• Regular backups: Run this script weekly"
print_info "• Before updates: Always backup before major changes"
print_info "• Test restores: Periodically test backup restoration"
print_info "• External storage: Copy backups to external location for safety"

# Offer to compress backup
echo
read -p "Compress backup to tar.gz? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Compressing backup..."
    cd "$PROJECT_ROOT/backend/backups"
    tar -czf "backup_$TIMESTAMP.tar.gz" "backup_$TIMESTAMP"
    if [ $? -eq 0 ]; then
        COMPRESSED_SIZE=$(du -sh "backup_$TIMESTAMP.tar.gz" | cut -f1)
        print_success "Backup compressed to: backup_$TIMESTAMP.tar.gz ($COMPRESSED_SIZE)"
        
        # Ask if user wants to remove uncompressed version
        read -p "Remove uncompressed backup directory? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "backup_$TIMESTAMP"
            print_success "Uncompressed backup directory removed"
        fi
    else
        print_error "Compression failed"
    fi
fi

echo
print_success "Backup operation completed!"