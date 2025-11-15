#!/bin/bash
# Stop the Config Manager server

set -e
set -o pipefail

readonly PID_FILE=".server.pid"
readonly SERVER_PORT=3000
# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly NC='\033[0m'                         # No Color

log_info() {
    echo -e "${BLUE}  ${NC}$1"
}

log_warn() {
    echo -e "${YELLOW}  ${NC}$1"
}

log_error() {
    echo -e "${RED}  ${NC}$1" >&2
}

log_success() {
    echo -e "${GREEN}[stop]${NC} $1"
}

# Check if port is in use
check_port() {
    if command -v ss >/dev/null 2>&1; then
        if ss -ltn | grep -q ":${SERVER_PORT} "; then
            return 0
        fi
    elif command -v lsof >/dev/null 2>&1; then
        if lsof -i ":${SERVER_PORT}" >/dev/null 2>&1; then
            return 0
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -ltn | grep -q ":${SERVER_PORT} "; then
            return 0
        fi
    fi
    return 1
}

# Stop server by PID
stop_by_pid() {
    local pid=$1

    if ! kill -0 "$pid" 2>/dev/null; then
        return 1
    fi

    echo -e "${BLUE}[stop]${NC} Stopping server (PID: $pid)..."
    kill "$pid" 2>/dev/null || true

    # Wait up to 5 seconds for graceful shutdown
    local waited=0
    while kill -0 "$pid" 2>/dev/null && [ $waited -lt 5 ]; do
        sleep 1
        waited=$((waited + 1))
    done

    # Force kill if still running
    if kill -0 "$pid" 2>/dev/null; then
        log_warn "Server still running after ${waited}s, force killing..."
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi

    if kill -0 "$pid" 2>/dev/null; then
        return 1
    fi

    return 0
}

# Main logic
if [ ! -f "$PID_FILE" ]; then
    log_warn "No PID file found at $PID_FILE"
    log_info "Checking for running servers by process name..."

    if pgrep -f config-manager-server >/dev/null; then
        log_info "Found running server(s), killing by name..."
        pkill -f config-manager-server || true
        sleep 2

        if pgrep -f config-manager-server >/dev/null; then
            log_warn "Server still running, force killing..."
            pkill -9 -f config-manager-server || true
            sleep 1
        fi

        if pgrep -f config-manager-server >/dev/null; then
            log_error "Failed to stop server"
            exit 1
        fi

        log_success "Server stopped"
    else
        log_info "No running server found"
    fi

    # Check if port is still occupied
    if check_port; then
        log_warn "Port $SERVER_PORT is still occupied by another process"
        log_info "Check with: ss -ltnp | grep :$SERVER_PORT"
    fi

    exit 0
fi

# Stop by PID file
SERVER_PID=$(cat "$PID_FILE")

if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    log_warn "Server with PID $SERVER_PID is not running"
    rm -f "$PID_FILE"

    # Check if another instance is running
    if pgrep -f config-manager-server >/dev/null; then
        log_warn "Found different server instance running"
        log_info "Killing by process name..."
        pkill -f config-manager-server || true
        sleep 1
    fi

    # Check port
    if check_port; then
        log_warn "Port $SERVER_PORT is still occupied"
        log_info "Check with: ss -ltnp | grep :$SERVER_PORT"
    else
        log_info "Port $SERVER_PORT is free"
    fi

    exit 0
fi

if stop_by_pid "$SERVER_PID"; then
    rm -f "$PID_FILE"
    log_success "Server stopped successfully"

    # Verify port is free
    if check_port; then
        log_warn "Port $SERVER_PORT is still occupied"
        log_info "Another process may be using the port"
    fi
else
    log_error "Failed to stop server with PID $SERVER_PID"
    rm -f "$PID_FILE"
    exit 1
fi
