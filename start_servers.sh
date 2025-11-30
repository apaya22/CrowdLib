#!/bin/bash

# CrowdLib Master Start Server Script (macOS/Linux)
# Automatically launches frontend and backend servers in separate terminal windows
# Usage: bash start_servers.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running on supported OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Detected Linux"
        return 0
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Detected macOS"
        return 0
    else
        log_error "This script is optimized for macOS and Linux."
        echo "On Windows, please use: start_servers.bat"
        exit 1
    fi
}

# Check if backend run_server.sh exists
check_backend_script() {
    if [ ! -f "$SCRIPT_DIR/backend/run_server.sh" ]; then
        log_error "Backend run_server.sh not found at $SCRIPT_DIR/backend/run_server.sh"
        exit 1
    fi
    log_success "Found backend run_server.sh"
}

# Check if frontend exists
check_frontend() {
    if [ ! -d "$SCRIPT_DIR/frontend" ]; then
        log_error "Frontend directory not found at $SCRIPT_DIR/frontend"
        exit 1
    fi
    if [ ! -f "$SCRIPT_DIR/frontend/package.json" ]; then
        log_error "package.json not found in frontend directory"
        exit 1
    fi
    log_success "Found frontend directory"
}

# Check if node_modules are installed
check_dependencies() {
    if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
        log_error "Frontend dependencies not installed."
        echo "Please run: npm install (in frontend directory) or bash init.sh"
        exit 1
    fi
    log_success "Frontend dependencies are installed"

}

# Start backend server in a new terminal window
start_backend() {
    log_info "Starting backend server in a new terminal..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - use osascript to open new Terminal window
        osascript <<EOF
tell application "Terminal"
    do script "cd '$SCRIPT_DIR/backend' && bash run_server.sh"
    activate
end tell
EOF
    else
        # Linux - try different terminal emulators
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "cd '$SCRIPT_DIR/backend' && bash run_server.sh; exec bash"
        elif command -v konsole &> /dev/null; then
            konsole --workdir "$SCRIPT_DIR/backend" -e bash run_server.sh &
        elif command -v xterm &> /dev/null; then
            xterm -e bash -c "cd '$SCRIPT_DIR/backend' && bash run_server.sh; exec bash" &
        else
            log_error "No supported terminal emulator found (gnome-terminal, konsole, or xterm)"
            echo "Please start the backend manually:"
            echo "  cd backend && bash run_server.sh"
            return 1
        fi
    fi

    log_success "Backend server window opened"
    sleep 2
}

# Start frontend server in a new terminal window
start_frontend() {
    log_info "Starting frontend server in a new terminal..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - use osascript to open new Terminal window
        osascript <<EOF
tell application "Terminal"
    do script "cd '$SCRIPT_DIR/frontend' && npm run dev"
    activate
end tell
EOF
    else
        # Linux - try different terminal emulators
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "cd '$SCRIPT_DIR/frontend' && npm run dev; exec bash"
        elif command -v konsole &> /dev/null; then
            konsole --workdir "$SCRIPT_DIR/frontend" -e npm run dev &
        elif command -v xterm &> /dev/null; then
            xterm -e bash -c "cd '$SCRIPT_DIR/frontend' && npm run dev; exec bash" &
        else
            log_error "No supported terminal emulator found"
            echo "Please start the frontend manually:"
            echo "  cd frontend && npm run dev"
            return 1
        fi
    fi

    log_success "Frontend server window opened"
    sleep 2
}

# Main function
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║   CrowdLib Master Start Server Script   ║"
    echo "║   Starting Frontend & Backend Servers   ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""

    check_os
    check_backend_script
    check_frontend
    check_dependencies

    echo ""
    log_info "All checks passed! Starting servers..."
    echo ""

    # Start both servers
    start_backend
    start_frontend

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Servers Started Successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Backend Server: http://localhost:8000"
    echo "Frontend Server: http://localhost:5173"
    echo ""
    echo "To stop the servers, close the terminal windows or press Ctrl+C in each"
    echo ""
}

# Run main function
main
