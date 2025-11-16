#!/bin/bash
# Check the current status and stats of the Config Manager server

set -e
set -o pipefail

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;186;194;222m'    # #bac2de - Subtext
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
readonly SERVER="󰒋"
readonly CHART="󰈙"
readonly CLOCK="󰥔"
readonly MEM="󰍛"
readonly CPU="󰻠"
readonly NET="󰈀"
readonly LOG=""
readonly PID_FILE=".server.pid"
readonly LOG_FILE="server.log"
readonly PORT="3000"

log_success() {
    echo -e "${GREEN}${CHECK}  ${NC}$1"
}

log_error() {
    echo -e "${RED}${CROSS}  ${NC}$1" >&2
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_info() {
    echo -e "${BLUE}${INFO}  ${NC}$1"
}

log_stat() {
    local icon=$1
    local label=$2
    local value=$3
    local color=$4
    printf "${SUBTEXT}%-2s  %-12s${NC} ${color}%s${NC}\n" "$icon" "$label:" "$value"
}

echo -e "${MAUVE}[status]${NC} Checking Config Manager server status..."
echo ""

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    log_error "Server is not running (no PID file found)"
    echo ""
    log_info "Start the server with: ${BLUE}./start.sh${NC}"
    exit 1
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is actually running
if ! ps -p "$PID" > /dev/null 2>&1; then
    log_error "Server is not running (PID $PID not found)"
    log_warn "Stale PID file detected, removing..."
    rm -f "$PID_FILE"
    echo ""
    log_info "Start the server with: ${BLUE}./start.sh${NC}"
    exit 1
fi

# Server is running!
log_success "Server is running"
echo ""

# Display server info header
echo -e "${MAUVE}${SERVER}  Server Information${NC}"
echo ""

# PID
log_stat "$INFO" "Process ID" "$PID" "$SAPPHIRE"

# Uptime
if command -v ps > /dev/null 2>&1; then
    UPTIME=$(ps -p "$PID" -o etime= 2>/dev/null | xargs || echo "unknown")
    log_stat "$CLOCK" "Uptime" "$UPTIME" "$GREEN"
fi

# Memory usage
if command -v ps > /dev/null 2>&1; then
    MEM_KB=$(ps -p "$PID" -o rss= 2>/dev/null | xargs || echo "0")
    if [ "$MEM_KB" != "0" ]; then
        MEM_MB=$((MEM_KB / 1024))
        log_stat "$MEM" "Memory" "${MEM_MB} MB" "$YELLOW"
    fi
fi

# CPU usage
if command -v ps > /dev/null 2>&1; then
    CPU_PERCENT=$(ps -p "$PID" -o %cpu= 2>/dev/null | xargs || echo "unknown")
    log_stat "$CPU" "CPU Usage" "${CPU_PERCENT}%" "$BLUE"
fi

# Port status
if command -v ss > /dev/null 2>&1; then
    if ss -tuln | grep -q ":$PORT "; then
        log_stat "$NET" "Port $PORT" "LISTENING" "$GREEN"
    else
        log_stat "$NET" "Port $PORT" "NOT LISTENING" "$RED"
    fi
elif command -v netstat > /dev/null 2>&1; then
    if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
        log_stat "$NET" "Port $PORT" "LISTENING" "$GREEN"
    else
        log_stat "$NET" "Port $PORT" "NOT LISTENING" "$RED"
    fi
fi

echo ""

# Log file info
if [ -f "$LOG_FILE" ]; then
    echo -e "${MAUVE}${LOG}  Recent Logs${NC}"
    echo ""

    LOG_LINES=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
    log_stat "$LOG" "Total Lines" "$LOG_LINES" "$SUBTEXT"

    echo ""
    echo -e "${SUBTEXT}Last 5 log entries:${NC}"
    echo ""

    tail -n 5 "$LOG_FILE" | while IFS= read -r line; do
        # Color code log levels
        if [[ "$line" =~ ERROR|ERRO|error ]]; then
            echo -e "${RED}  ${line}${NC}"
        elif [[ "$line" =~ WARN|warn ]]; then
            echo -e "${YELLOW}  ${line}${NC}"
        elif [[ "$line" =~ INFO|info ]]; then
            echo -e "${BLUE}  ${line}${NC}"
        else
            echo -e "${TEXT}  ${line}${NC}"
        fi
    done

    echo ""
    log_info "View full logs: ${BLUE}tail -f $LOG_FILE${NC}"
else
    log_warn "Log file not found: $LOG_FILE"
fi

echo ""

# Server URL
echo -e "${MAUVE}${NET}  Access${NC}"
echo ""
log_stat "$NET" "Server URL" "http://localhost:$PORT" "$SAPPHIRE"

echo ""
log_success "Server is healthy and running"
