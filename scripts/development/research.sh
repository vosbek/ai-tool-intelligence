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
        if [ -f "config.py" ]; then
            python config.py research
        else
            echo "📊 Basic Research Status:"
            if [ -f "ai_tools.db" ]; then
                echo "Database exists - checking tool status..."
                python3 << 'EOF'
import sqlite3
try:
    conn = sqlite3.connect('ai_tools.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT processing_status, COUNT(*) FROM tools GROUP BY processing_status")
    results = cursor.fetchall()
    
    print("\nTool Status Summary:")
    for status, count in results:
        print(f"  {status}: {count} tools")
    
    cursor.execute("SELECT COUNT(*) FROM tools")
    total = cursor.fetchone()[0]
    print(f"\nTotal tools: {total}")
    
    conn.close()
except Exception as e:
    print(f"Error reading database: {e}")
EOF
            else
                echo "❌ Database not found"
            fi
        fi
        ;;
    "failed")
        if [ -f "config.py" ]; then
            python config.py failed
        else
            echo "📋 Failed Tools:"
            python3 << 'EOF'
import sqlite3
try:
    conn = sqlite3.connect('ai_tools.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM tools WHERE processing_status = 'error'")
    failed_tools = cursor.fetchall()
    
    if failed_tools:
        for (name,) in failed_tools:
            print(f"  • {name}")
    else:
        print("  ✅ No failed tools")
    
    conn.close()
except Exception as e:
    print(f"Error reading database: {e}")
EOF
        fi
        ;;
    "retry")
        if [ -f "config.py" ]; then
            python config.py retry
        else
            echo "🔄 Retrying failed tools..."
            python3 << 'EOF'
import sqlite3
try:
    conn = sqlite3.connect('ai_tools.db')
    cursor = conn.cursor()
    
    cursor.execute("UPDATE tools SET processing_status = 'needs_update' WHERE processing_status = 'error'")
    updated = cursor.rowcount
    conn.commit()
    
    print(f"✅ Marked {updated} failed tools for retry")
    
    conn.close()
except Exception as e:
    print(f"Error updating database: {e}")
EOF
        fi
        ;;
    "process")
        if [ -z "$2" ]; then
            echo "Usage: ./research.sh process <tool-names>"
            echo "Example: ./research.sh process 'Cursor,GitHub Copilot'"
            exit 1
        fi
        if [ -f "batch_processor.py" ]; then
            python batch_processor.py process "$2"
        else
            echo "❌ batch_processor.py not found - manual processing not available in MVP"
            echo "💡 Use the web interface to research individual tools"
        fi
        ;;
    "category")
        if [ -z "$2" ]; then
            echo "Usage: ./research.sh category <category-name>"
            echo "Example: ./research.sh category 'Agentic IDEs'"
            exit 1
        fi
        if [ -f "batch_processor.py" ]; then
            python batch_processor.py category "$2"
        else
            echo "❌ batch_processor.py not found - batch processing not available in MVP"
            echo "💡 Use the web interface to research tools by category"
        fi
        ;;
    "scheduler")
        echo "Starting research scheduler..."
        if [ -f "batch_processor.py" ]; then
            python batch_processor.py scheduler
        else
            echo "❌ batch_processor.py not found - scheduler not available in MVP"
            echo "💡 Research tools manually through the web interface"
        fi
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