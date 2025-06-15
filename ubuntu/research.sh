#!/bin/bash
#
# Research management script for AI Tool Intelligence Platform on Ubuntu
# 
# This script provides easy management of research operations

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

# Function to show usage
show_usage() {
    echo "Usage: $0 <command> [arguments]"
    echo
    echo "Commands:"
    echo "  status              Show research queue status"
    echo "  failed              List failed tools and reasons"
    echo "  retry               Retry all failed tools"
    echo "  process <tools>     Process specific tools (comma-separated names)"
    echo "  category <name>     Process all tools in a category"
    echo "  scheduler           Start automated research scheduler"
    echo "  stats               Show research statistics"
    echo "  clean               Clean up old research data"
    echo
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 process 'Cursor,GitHub Copilot'"
    echo "  $0 category 'Agentic IDEs'"
    echo "  $0 retry"
    echo "  $0 scheduler"
}

# Check if backend is set up
if [ ! -d "$PROJECT_ROOT/backend/venv" ]; then
    print_error "Backend not set up. Run ./ubuntu/setup.sh first"
    exit 1
fi

# Change to backend directory and activate virtual environment
cd "$PROJECT_ROOT/backend"
source venv/bin/activate

# Check if command was provided
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

COMMAND="$1"

case "$COMMAND" in
    "status")
        print_step "Checking research queue status..."
        if [ -f "config.py" ]; then
            python config.py research
        else
            print_error "config.py not found"
            exit 1
        fi
        ;;
    
    "failed")
        print_step "Listing failed tools..."
        if [ -f "config.py" ]; then
            python config.py failed
        else
            print_error "config.py not found"
            exit 1
        fi
        ;;
    
    "retry")
        print_step "Retrying all failed tools..."
        if [ -f "config.py" ]; then
            python config.py retry
        else
            print_error "config.py not found"
            exit 1
        fi
        ;;
    
    "process")
        if [ -z "$2" ]; then
            print_error "Usage: $0 process <tool-names>"
            print_info "Example: $0 process 'Cursor,GitHub Copilot'"
            exit 1
        fi
        print_step "Processing specific tools: $2"
        if [ -f "batch_processor.py" ]; then
            python batch_processor.py process "$2"
        else
            print_error "batch_processor.py not found"
            exit 1
        fi
        ;;
    
    "category")
        if [ -z "$2" ]; then
            print_error "Usage: $0 category <category-name>"
            print_info "Example: $0 category 'Agentic IDEs'"
            exit 1
        fi
        print_step "Processing tools in category: $2"
        if [ -f "batch_processor.py" ]; then
            python batch_processor.py category "$2"
        else
            print_error "batch_processor.py not found"
            exit 1
        fi
        ;;
    
    "scheduler")
        print_step "Starting research scheduler..."
        print_info "Press Ctrl+C to stop the scheduler"
        if [ -f "batch_processor.py" ]; then
            python batch_processor.py scheduler
        else
            print_error "batch_processor.py not found"
            exit 1
        fi
        ;;
    
    "stats")
        print_step "Generating research statistics..."
        if [ -f "ai_tools.db" ]; then
            python -c "
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('ai_tools.db')
cursor = conn.cursor()

# Total tools
cursor.execute('SELECT COUNT(*) FROM tools')
total_tools = cursor.fetchone()[0]

# Researched tools
cursor.execute('SELECT COUNT(*) FROM tools WHERE last_researched IS NOT NULL')
researched_tools = cursor.fetchone()[0]

# Failed tools
cursor.execute('SELECT COUNT(*) FROM tools WHERE research_status = \"failed\"')
failed_tools = cursor.fetchone()[0]

# Recent research (last 7 days)
week_ago = (datetime.now() - timedelta(days=7)).isoformat()
cursor.execute('SELECT COUNT(*) FROM tools WHERE last_researched > ?', (week_ago,))
recent_research = cursor.fetchone()[0]

# Categories
cursor.execute('SELECT category, COUNT(*) FROM tools GROUP BY category ORDER BY COUNT(*) DESC')
categories = cursor.fetchall()

print(f'📊 Research Statistics')
print(f'=====================')
print(f'Total tools: {total_tools}')
print(f'Researched: {researched_tools} ({researched_tools/total_tools*100:.1f}%)' if total_tools > 0 else 'Researched: 0')
print(f'Failed: {failed_tools}')
print(f'Recent (7 days): {recent_research}')
print()
print('Categories:')
for category, count in categories:
    print(f'  {category}: {count}')

conn.close()
"
        else
            print_error "Database not found. Platform may not be initialized."
            exit 1
        fi
        ;;
    
    "clean")
        print_step "Cleaning up old research data..."
        print_warning "This will remove research data older than 30 days"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ -f "ai_tools.db" ]; then
                python -c "
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('ai_tools.db')
cursor = conn.cursor()

# Remove old research data (keep basic tool info)
month_ago = (datetime.now() - timedelta(days=30)).isoformat()
cursor.execute('''
    UPDATE tools 
    SET research_data = NULL, 
        competitive_analysis = NULL,
        last_researched = NULL
    WHERE last_researched < ?
''', (month_ago,))

cleaned = cursor.rowcount
conn.commit()
conn.close()

print(f'✅ Cleaned research data for {cleaned} tools older than 30 days')
"
                print_success "Cleanup completed"
            else
                print_error "Database not found"
                exit 1
            fi
        else
            print_info "Cleanup cancelled"
        fi
        ;;
    
    *)
        print_error "Unknown command: $COMMAND"
        echo
        show_usage
        exit 1
        ;;
esac