#!/bin/bash
# CI Logging Helper - Clean [tag] style logging for GitHub Actions
# Usage: source this file in your workflow scripts
# STYLECHECK_IGNORE - CI workflow script, different standards
# LINTCHECK_IGNORE - CI workflow script, different standards

# Configuration
readonly LOG_DIR=".github/logs"
readonly LOG_FILE="${LOG_DIR}/$(date +%Y%m%d-%H%M%S)-workflow.log"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Icons from theme.sh (GitHub Actions compatible)
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
readonly ROCKET=""
readonly HAMMER=""
readonly CLEAN=""
readonly CHART="󰈙"
readonly PLAY=""
readonly FOLDER=""

# Log to both stdout and file with timestamp
log_to_file() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] $1" >> "${LOG_FILE}"
}

# Logging functions with [tag] style
log_success() {
    local msg="[success] ${CHECK}  $1"
    echo "${msg}"
    log_to_file "${msg}"
}

log_error() {
    local msg="[error] ${CROSS}  $1"
    echo "${msg}" >&2
    log_to_file "${msg}"
}

log_warn() {
    local msg="[warn] ${WARN}  $1"
    echo "${msg}"
    log_to_file "${msg}"
}

log_info() {
    local msg="[info] ${INFO}  $1"
    echo "${msg}"
    log_to_file "${msg}"
}

log_header() {
    echo ""
    echo "[workflow] $1"
    echo ""
    log_to_file "[workflow] $1"
}

log_step() {
    local tag="$1"
    shift
    echo ""
    echo "[${tag}] $*"
    echo ""
    log_to_file "[${tag}] $*"
}

# Export functions and variables
export -f log_success log_error log_warn log_info log_header log_step log_to_file
export LOG_FILE LOG_DIR
export CHECK CROSS WARN INFO ROCKET HAMMER CLEAN CHART PLAY FOLDER
