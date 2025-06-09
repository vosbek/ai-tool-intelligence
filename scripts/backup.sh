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