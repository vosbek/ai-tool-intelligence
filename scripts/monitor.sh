#!/bin/bash
# monitor.sh - Monitor system status

echo "📊 AI Tool Intelligence System Status"
echo "====================================="

cd ../backend
if [ -d "venv" ]; then
    source venv/bin/activate
    if [ -f "config.py" ]; then
        python config.py status
    else
        echo "⚠️  config.py not found - using basic status check"
        
        # Basic health check
        echo "Backend Health Check:"
        if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
            echo "✅ Backend is running (http://localhost:5000)"
        else
            echo "❌ Backend is not responding"
        fi
        
        echo ""
        echo "Frontend Health Check:"
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo "✅ Frontend is running (http://localhost:3000)"
        else
            echo "❌ Frontend is not responding"
        fi
        
        echo ""
        echo "Database Check:"
        if [ -f "ai_tools.db" ]; then
            echo "✅ Database file exists"
            DB_SIZE=$(du -h ai_tools.db | cut -f1)
            echo "📁 Database size: $DB_SIZE"
        else
            echo "❌ Database file not found"
        fi
    fi
else
    echo "❌ Backend not set up. Run ./setup.sh first"
fi