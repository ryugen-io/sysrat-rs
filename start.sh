#!/bin/bash
# Start the Config Manager server without rebuilding

set -e

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load .env if it exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

readonly PID_FILE=".server.pid"
readonly LOG_FILE="server.log"
readonly SERVER_PORT=3000
readonly SERVER_HOST="${SERVER_HOST:-localhost}"

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
    echo -e "${SAPPHIRE}  ${NC}$1"
}

# Check if port is already in use
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

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    SERVER_PID=$(cat "$PID_FILE")
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        log_warn "Server is already running with PID $SERVER_PID"
        log_info "Access at http://${SERVER_HOST}:${SERVER_PORT}"
        log_info "Stop server: ./stop.sh or kill $SERVER_PID"
        exit 0
    else
        log_warn "Stale PID file found, removing..."
        rm -f "$PID_FILE"
    fi
fi

# Check if port is occupied
if check_port; then
    log_error "Port $SERVER_PORT is already in use"
    log_info "Another process may be using the port"
    log_info "Check with: ss -ltnp | grep :$SERVER_PORT"
    exit 1
fi

# Check if binary exists
if [ ! -f "target/debug/config-manager-server" ]; then
    log_error "Server binary not found at target/debug/config-manager-server"
    log_info "Run ./rebuild.sh to build the server first"
    exit 1
fi

# Check if config exists
if [ ! -f "config-manager.toml" ]; then
    log_error "config-manager.toml not found"
    log_info "Please create config-manager.toml with your configuration"
    exit 1
fi

echo -e "${MAUVE}[start]${NC} Starting server..."

# Remove old log file
rm -f "$LOG_FILE"

# Start server in background
nohup cargo run --bin config-manager-server > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# Save PID to file
echo "$SERVER_PID" > "$PID_FILE"

# Wait for server to start
sleep 2

# Check if server is running
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    log_error "Server failed to start"
    log_info "Last 20 lines of log:"
    tail -n 20 "$LOG_FILE" 2>/dev/null || echo "No log file available"
    rm -f "$PID_FILE"
    exit 1
fi

# Check if port is listening
max_attempts=5
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if check_port; then
        echo ""
        echo -e "${GREEN}[start]${NC} Server running (PID: $SERVER_PID)"
        log_info "URL: http://${SERVER_HOST}:${SERVER_PORT}"
        log_info "Logs: tail -f $LOG_FILE"
        log_info "Stop: ./stop.sh"
        exit 0
    fi
    attempt=$((attempt + 1))
    sleep 1
done

log_warn "Server process is running but port is not listening yet"
log_info "Check logs with: tail -f $LOG_FILE"
log_info "Server PID: $SERVER_PID"
