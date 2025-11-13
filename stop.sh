#!/bin/bash
# Stop the Config Manager server

set -e

readonly PID_FILE=".server.pid"
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

if [ ! -f "$PID_FILE" ]; then
    log_warn "No PID file found at $PID_FILE"
    log_info "Checking for running servers by name..."

    if pgrep -f config-manager-server >/dev/null; then
        log_info "Found running server, killing by name"
        pkill -f config-manager-server
        sleep 1
        log_info "Server stopped"
    else
        log_info "No running server found"
    fi
    exit 0
fi

SERVER_PID=$(cat "$PID_FILE")

if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    log_warn "Server with PID $SERVER_PID is not running"
    rm -f "$PID_FILE"
    exit 0
fi

log_info "Stopping server with PID $SERVER_PID..."
kill "$SERVER_PID" 2>/dev/null

sleep 1

if kill -0 "$SERVER_PID" 2>/dev/null; then
    log_warn "Server still running, force killing..."
    kill -9 "$SERVER_PID" 2>/dev/null
    sleep 1
fi

if kill -0 "$SERVER_PID" 2>/dev/null; then
    log_error "Failed to stop server"
    exit 1
fi

rm -f "$PID_FILE"
log_info "Server stopped successfully"
