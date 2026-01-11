#!/bin/bash
# CI Line Counter - Count lines in changed files
# Analyzes shell scripts, Python, and YAML files with clean logging
# STYLECHECK_IGNORE - CI workflow script, different standards

set -e
set -o pipefail

# Source CI logger
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/ci-logger.sh"

# File extensions to analyze
readonly EXTENSIONS=("sh" "py" "yml" "yaml")

# Count lines in a file with basic comment detection
count_lines() {
    local file="$1"
    local ext="${file##*.}"

    # Count total lines
    local total=$(wc -l < "$file" 2> /dev/null || echo "0")

    # Count comment-only lines based on file type
    local comments=0
    case "$ext" in
        sh)
            # Shell: lines starting with #
            comments=$(grep -cE '^\s*#' "$file" 2>/dev/null) || comments=0
            ;;
        py)
            # Python: lines starting with #
            comments=$(grep -cE '^\s*#' "$file" 2>/dev/null) || comments=0
            ;;
        yml | yaml)
            # YAML: lines starting with #
            comments=$(grep -cE '^\s*#' "$file" 2>/dev/null) || comments=0
            ;;
    esac

    # Count blank lines
    local blank
    blank=$(grep -cE '^\s*$' "$file" 2>/dev/null) || blank=0

    # Code lines = total - comments - blank
    local code=$((total - comments - blank))

    echo "$code $comments $blank $total"
}

# Analyze a list of files
analyze_files() {
    local files=("$@")

    if [ ${#files[@]} -eq 0 ]; then
        log_warn "No files to analyze"
        return 0
    fi

    local total_code=0
    local total_comments=0
    local total_blank=0
    local total_lines=0
    local file_count=0

    log_step "lines" "Analyzing changed files..."

    for file in "${files[@]}"; do
        # Skip if file doesn't exist
        if [ ! -f "$file" ]; then
            continue
        fi

        # Check if file extension is in our list
        local ext="${file##*.}"
        local should_analyze=false
        for valid_ext in "${EXTENSIONS[@]}"; do
            if [ "$ext" = "$valid_ext" ]; then
                should_analyze=true
                break
            fi
        done

        if [ "$should_analyze" = false ]; then
            continue
        fi

        read -r code comments blank total <<< "$(count_lines "$file")"

        total_code=$((total_code + code))
        total_comments=$((total_comments + comments))
        total_blank=$((total_blank + blank))
        total_lines=$((total_lines + total))
        file_count=$((file_count + 1))

        # Log file stats
        local rel_file="${file#./}"
        log_info "$(printf "%-40s  %4d lines (%d code, %d comments, %d blank)" \
            "$rel_file" "$total" "$code" "$comments" "$blank")"
    done

    if [ $file_count -eq 0 ]; then
        log_info "No analyzable files found"
        return 0
    fi

    # Calculate average
    local avg_code=$((total_code / file_count))

    # Print summary
    echo ""
    log_step "summary" "Line Count Summary"
    log_info "$(printf "Files analyzed:  %6d" "$file_count")"
    log_info "$(printf "Code lines:      %6d" "$total_code")"
    log_info "$(printf "Comment lines:   %6d" "$total_comments")"
    log_info "$(printf "Blank lines:     %6d" "$total_blank")"
    log_info "$(printf "Total lines:     %6d" "$total_lines")"
    log_info "$(printf "Average/file:    %6d lines" "$avg_code")"

    log_success "Line count analysis complete!"
}

# Main execution
main() {
    # Get changed files from git if no arguments provided
    local files=()

    if [ $# -eq 0 ]; then
        # Get files changed in this commit/PR
        mapfile -t files < <(git diff --name-only HEAD~1 2> /dev/null || git ls-files)
    else
        files=("$@")
    fi

    analyze_files "${files[@]}"
}

main "$@"
