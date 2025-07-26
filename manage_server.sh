#!/bin/bash

# Dify RAG MCP Server Management Script
# Usage: ./manage_server.sh {start|stop|restart|status} [transport_type]
# Transport types: stdio, sse, websocket (default: stdio)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.server.pid"
LOG_FILE="$SCRIPT_DIR/server.log"
PYTHON_SCRIPT="$SCRIPT_DIR/src/main.py"

# Default transport type
TRANSPORT_TYPE="stdio"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if server is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to get server status
get_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_success "Server is running (PID: $pid)"
        
        # Try to get transport info from log
        if [ -f "$LOG_FILE" ]; then
            local transport_info=$(tail -20 "$LOG_FILE" | grep -i "transport\|listening\|server started" | tail -1)
            if [ -n "$transport_info" ]; then
                print_info "Transport info: $transport_info"
            fi
        fi
        return 0
    else
        print_warning "Server is not running"
        return 1
    fi
}

# Function to start server
start_server() {
    if is_running; then
        print_warning "Server is already running"
        get_status
        return 1
    fi
    
    print_info "Starting Dify RAG MCP Server with transport: $TRANSPORT_TYPE"
    
    # Check if Python script exists
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        print_error "Python script not found: $PYTHON_SCRIPT"
        return 1
    fi
    
    # Start server in background
    cd "$SCRIPT_DIR"
    nohup python "$PYTHON_SCRIPT" --transport "$TRANSPORT_TYPE" > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 2
    if is_running; then
        print_success "Server started successfully (PID: $pid)"
        print_info "Log file: $LOG_FILE"
        
        # Show transport-specific info
        case $TRANSPORT_TYPE in
            "sse")
                print_info "SSE endpoint: http://localhost:8000/sse/"
                ;;
            "websocket")
                print_info "WebSocket endpoint: ws://localhost:8000/ws"
                ;;
            "stdio")
                print_info "STDIO transport - communicate via stdin/stdout"
                ;;
        esac
        return 0
    else
        print_error "Failed to start server"
        rm -f "$PID_FILE"
        if [ -f "$LOG_FILE" ]; then
            print_error "Last few lines from log:"
            tail -10 "$LOG_FILE"
        fi
        return 1
    fi
}

# Function to stop server
stop_server() {
    if ! is_running; then
        print_warning "Server is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    print_info "Stopping server (PID: $pid)"
    
    # Try graceful shutdown first
    kill "$pid" 2>/dev/null
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt 10 ] && ps -p "$pid" > /dev/null 2>&1; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        print_warning "Graceful shutdown failed, forcing termination"
        kill -9 "$pid" 2>/dev/null
        sleep 1
    fi
    
    # Clean up
    rm -f "$PID_FILE"
    
    if ps -p "$pid" > /dev/null 2>&1; then
        print_error "Failed to stop server"
        return 1
    else
        print_success "Server stopped successfully"
        return 0
    fi
}

# Function to restart server
restart_server() {
    print_info "Restarting server..."
    stop_server
    sleep 2
    start_server
}

# Function to show usage
show_usage() {
    echo "Usage: $0 {start|stop|restart|status} [transport_type]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the MCP server"
    echo "  stop     - Stop the MCP server"
    echo "  restart  - Restart the MCP server"
    echo "  status   - Show server status"
    echo ""
    echo "Transport types:"
    echo "  stdio     - Standard input/output (default)"
    echo "  sse       - Server-Sent Events (HTTP)"
    echo "  websocket - WebSocket"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start with stdio transport"
    echo "  $0 start sse      # Start with SSE transport"
    echo "  $0 restart stdio  # Restart with stdio transport"
    echo "  $0 status         # Show current status"
}

# Main script logic
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

COMMAND="$1"

# Set transport type if provided
if [ $# -ge 2 ]; then
    case "$2" in
        "stdio"|"sse"|"websocket")
            TRANSPORT_TYPE="$2"
            ;;
        *)
            print_error "Invalid transport type: $2"
            show_usage
            exit 1
            ;;
    esac
fi

# Execute command
case "$COMMAND" in
    "start")
        start_server
        ;;
    "stop")
        stop_server
        ;;
    "restart")
        restart_server
        ;;
    "status")
        get_status
        ;;
    "help"|"--help"|"h")
        show_usage
        ;;
    *)
        print_error "Invalid command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

exit $?