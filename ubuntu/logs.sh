#!/bin/bash
#
# Log viewer script for AI Tool Intelligence Platform on Ubuntu
# 
# This script provides easy access to view application logs

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
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo
    echo "Commands:"
    echo "  backend     Show backend logs"
    echo "  frontend    Show frontend logs"
    echo "  both        Show both logs (default)"
    echo "  errors      Show only error lines"
    echo "  live        Follow logs in real-time"
    echo
    echo "Options:"
    echo "  -n, --lines NUM    Show last N lines (default: 50)"
    echo "  -f, --follow       Follow logs in real-time"
    echo "  -e, --errors       Show only error lines"
    echo "  -h, --help         Show this help"
    echo
    echo "Examples:"
    echo "  $0                 # Show last 50 lines of both logs"
    echo "  $0 backend         # Show backend logs"
    echo "  $0 -n 100 frontend # Show last 100 lines of frontend logs"
    echo "  $0 --errors        # Show only error lines from both logs"
    echo "  $0 live            # Follow both logs in real-time"
}

# Default values
LINES=50
FOLLOW=false
ERRORS_ONLY=false
COMMAND="both"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--lines)
            LINES="$2"
            shift 2
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -e|--errors)
            ERRORS_ONLY=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        backend|frontend|both|errors|live)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Set follow mode for live command
if [ "$COMMAND" = "live" ]; then
    FOLLOW=true
    COMMAND="both"
fi

# Set errors only for errors command
if [ "$COMMAND" = "errors" ]; then
    ERRORS_ONLY=true
    COMMAND="both"
fi

# Log file paths
BACKEND_LOG="$PROJECT_ROOT/ubuntu/logs/backend.log"
FRONTEND_LOG="$PROJECT_ROOT/ubuntu/logs/frontend.log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/ubuntu/logs"

echo -e "${BLUE}📋 AI Tool Intelligence Platform Logs${NC}"
echo "======================================="

# Function to display logs
show_logs() {
    local logfile="$1"
    local name="$2"
    local color="$3"
    
    if [ ! -f "$logfile" ]; then
        print_warning "$name log file not found: $logfile"
        return
    fi
    
    echo -e "\n${color}=== $name Logs ===${NC}"
    
    if [ "$ERRORS_ONLY" = true ]; then
        if [ "$FOLLOW" = true ]; then
            tail -f "$logfile" | grep -i --color=always "error\|exception\|traceback\|failed\|fatal"
        else
            tail -n "$LINES" "$logfile" | grep -i --color=always "error\|exception\|traceback\|failed\|fatal"
        fi
    else
        if [ "$FOLLOW" = true ]; then
            tail -f "$logfile"
        else
            tail -n "$LINES" "$logfile"
        fi
    fi
}

# Function to show combined logs
show_combined_logs() {
    if [ "$FOLLOW" = true ]; then
        print_info "Following logs in real-time (press Ctrl+C to stop)..."
        if [ "$ERRORS_ONLY" = true ]; then
            (
                [ -f "$BACKEND_LOG" ] && tail -f "$BACKEND_LOG" | sed 's/^/[BACKEND] /' | grep -i --color=always "error\|exception\|traceback\|failed\|fatal" &
                [ -f "$FRONTEND_LOG" ] && tail -f "$FRONTEND_LOG" | sed 's/^/[FRONTEND] /' | grep -i --color=always "error\|exception\|traceback\|failed\|fatal" &
                wait
            )
        else
            (
                [ -f "$BACKEND_LOG" ] && tail -f "$BACKEND_LOG" | sed 's/^/[BACKEND] /' &
                [ -f "$FRONTEND_LOG" ] && tail -f "$FRONTEND_LOG" | sed 's/^/[FRONTEND] /' &
                wait
            )
        fi
    else
        if [ -f "$BACKEND_LOG" ] && [ -f "$FRONTEND_LOG" ]; then
            # Merge logs by timestamp and show most recent
            if [ "$ERRORS_ONLY" = true ]; then
                (
                    tail -n "$LINES" "$BACKEND_LOG" | sed 's/^/[BACKEND] /' | grep -i "error\|exception\|traceback\|failed\|fatal"
                    tail -n "$LINES" "$FRONTEND_LOG" | sed 's/^/[FRONTEND] /' | grep -i "error\|exception\|traceback\|failed\|fatal"
                ) | tail -n "$LINES"
            else
                (
                    tail -n "$LINES" "$BACKEND_LOG" | sed 's/^/[BACKEND] /'
                    tail -n "$LINES" "$FRONTEND_LOG" | sed 's/^/[FRONTEND] /'
                ) | tail -n "$LINES"
            fi
        else
            [ -f "$BACKEND_LOG" ] && show_logs "$BACKEND_LOG" "Backend" "$GREEN"
            [ -f "$FRONTEND_LOG" ] && show_logs "$FRONTEND_LOG" "Frontend" "$CYAN"
        fi
    fi
}

# Execute based on command
case $COMMAND in
    backend)
        show_logs "$BACKEND_LOG" "Backend" "$GREEN"
        ;;
    frontend)
        show_logs "$FRONTEND_LOG" "Frontend" "$CYAN"
        ;;
    both)
        if [ "$FOLLOW" = true ] || [ "$ERRORS_ONLY" = true ]; then
            show_combined_logs
        else
            show_logs "$BACKEND_LOG" "Backend" "$GREEN"
            show_logs "$FRONTEND_LOG" "Frontend" "$CYAN"
        fi
        ;;
esac

# Show log file info
if [ "$FOLLOW" = false ]; then
    echo
    print_step "Log file information:"
    
    if [ -f "$BACKEND_LOG" ]; then
        BACKEND_SIZE=$(du -h "$BACKEND_LOG" | cut -f1)
        BACKEND_LINES=$(wc -l < "$BACKEND_LOG")
        print_info "Backend log: $BACKEND_SIZE ($BACKEND_LINES lines)"
    fi
    
    if [ -f "$FRONTEND_LOG" ]; then
        FRONTEND_SIZE=$(du -h "$FRONTEND_LOG" | cut -f1)
        FRONTEND_LINES=$(wc -l < "$FRONTEND_LOG")
        print_info "Frontend log: $FRONTEND_SIZE ($FRONTEND_LINES lines)"
    fi
    
    echo
    print_info "Use '$0 live' to follow logs in real-time"
    print_info "Use '$0 errors' to show only error messages"
fi