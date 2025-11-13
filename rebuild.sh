#!/bin/bash
# Rebuild script for Config Manager
# Performs full build cycle: format, build backend and frontend

set -e
set -o pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly LOG_FILE="server.log"
readonly SERVER_PORT=3000
readonly SERVER_HOST="10.1.1.30"
readonly PID_FILE=".server.pid"

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Parse arguments
BUILD_BACKEND=true
BUILD_FRONTEND=true
START_SERVER=true
SKIP_FORMAT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            BUILD_FRONTEND=false
            shift
            ;;
        --frontend-only)
            BUILD_BACKEND=false
            shift
            ;;
        --no-server)
            START_SERVER=false
            shift
            ;;
        --skip-format)
            SKIP_FORMAT=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --backend-only   Only build backend"
            echo "  --frontend-only  Only build frontend"
            echo "  --no-server      Don't start server after build"
            echo "  --skip-format    Skip code formatting"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "[ERROR] Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Cleanup function
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Build failed with exit code $exit_code"
        log_info "Check the output above for details"
    fi
    cd "$SCRIPT_DIR"
}

# Set trap for cleanup
trap cleanup EXIT

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
check_requirements() {
    log_info "Checking requirements..."

    local missing_tools=()

    if ! command_exists cargo; then
        missing_tools+=("cargo")
    fi

    if ! command_exists trunk; then
        missing_tools+=("trunk")
    fi

    if ! command_exists cargo-auditable; then
        missing_tools+=("cargo-auditable")
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install with: cargo install trunk cargo-auditable"
        exit 1
    fi

    log_info "All required tools are available"
}

# Check if port is already in use
check_port() {
    if command_exists ss; then
        if ss -ltn | grep -q ":${SERVER_PORT} "; then
            return 0
        fi
    elif command_exists lsof; then
        if lsof -i ":${SERVER_PORT}" >/dev/null 2>&1; then
            return 0
        fi
    elif command_exists netstat; then
        if netstat -ltn | grep -q ":${SERVER_PORT} "; then
            return 0
        fi
    fi
    return 1
}

# Stop running servers
stop_servers() {
    log_info "Stopping running servers..."

    # Check if PID file exists and process is running
    if [ -f "$PID_FILE" ]; then
        local old_pid
        old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_info "Stopping server with PID $old_pid"
            kill "$old_pid" 2>/dev/null || true
            sleep 1
            # Force kill if still running
            if kill -0 "$old_pid" 2>/dev/null; then
                log_warn "Force killing server"
                kill -9 "$old_pid" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi

    # Fallback: kill by name
    if pgrep -f config-manager-server >/dev/null; then
        log_info "Killing servers by name"
        pkill -f config-manager-server || true
        sleep 1
    fi

    # Verify port is free
    if check_port; then
        log_warn "Port $SERVER_PORT is still in use, waiting..."
        sleep 2
        if check_port; then
            log_error "Port $SERVER_PORT is still occupied"
            log_info "Manual intervention may be required"
            exit 1
        fi
    fi
}

# Validate configuration
check_config() {
    if [ ! -f "config-manager.toml" ]; then
        log_error "config-manager.toml not found"
        log_info "Please create config-manager.toml with your configuration"
        exit 1
    fi
    log_info "Configuration file found"
}

# Build backend
build_backend() {
    log_info "Building backend..."

    if [ "$SKIP_FORMAT" = false ]; then
        log_info "Formatting backend code..."
        cargo fmt --all || {
            log_error "Backend formatting failed"
            exit 1
        }
    fi

    log_info "Building backend (dev profile)..."
    cargo build --bin config-manager-server || {
        log_error "Backend dev build failed"
        exit 1
    }

    log_info "Building backend (release profile with auditable)..."
    cargo auditable build --release --bin config-manager-server || {
        log_error "Backend release build failed"
        exit 1
    }

    log_info "Backend build successful"
}

# Build frontend
build_frontend() {
    log_info "Building frontend..."

    cd "$SCRIPT_DIR/frontend" || {
        log_error "Frontend directory not found"
        exit 1
    }

    if [ "$SKIP_FORMAT" = false ]; then
        log_info "Formatting frontend code..."
        cargo fmt || {
            log_error "Frontend formatting failed"
            exit 1
        }
    fi

    log_info "Building WASM frontend with Trunk (release)..."
    trunk build --release || {
        log_error "Frontend release build failed"
        exit 1
    }

    log_info "Building WASM frontend with Trunk (dev)..."
    trunk build || {
        log_error "Frontend dev build failed"
        exit 1
    }

    cd "$SCRIPT_DIR"
    log_info "Frontend build successful"
}

# Start server
start_server() {
    log_info "Starting server..."

    # Remove old log file
    rm -f "$LOG_FILE"

    # Start server in background
    nohup cargo run --bin config-manager-server > "$LOG_FILE" 2>&1 &
    local server_pid=$!

    # Save PID to file
    echo "$server_pid" > "$PID_FILE"

    # Wait for server to start
    sleep 2

    # Check if server is running
    if ! kill -0 "$server_pid" 2>/dev/null; then
        log_error "Server failed to start"
        log_info "Last 20 lines of log:"
        tail -n 20 "$LOG_FILE" 2>/dev/null || echo "No log file available"
        rm -f "$PID_FILE"
        exit 1
    fi

    # Check if port is listening
    local max_attempts=5
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if check_port; then
            log_info "Server started successfully (PID: $server_pid)"
            log_info "Access at http://${SERVER_HOST}:${SERVER_PORT}"
            log_info "Server logs: tail -f $LOG_FILE"
            log_info "Stop server: kill $server_pid"
            log_info "Refresh your browser to see changes"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done

    log_warn "Server process is running but port is not listening yet"
    log_info "Check logs with: tail -f $LOG_FILE"
}

# Main execution
main() {
    cd "$SCRIPT_DIR"

    log_info "Rebuilding Config Manager..."
    echo ""

    check_requirements
    check_config
    stop_servers

    echo ""

    if [ "$BUILD_BACKEND" = true ]; then
        build_backend
        echo ""
    fi

    if [ "$BUILD_FRONTEND" = true ]; then
        build_frontend
        echo ""
    fi

    log_info "Build complete!"
    echo ""

    if [ "$START_SERVER" = true ]; then
        start_server
    else
        log_info "Skipping server start (--no-server flag)"
    fi
}

# Run main function
main
