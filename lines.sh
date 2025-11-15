#!/bin/bash
# Line counter script for Config Manager
# Analyzes all .rs files with detailed statistics

set -e
set -o pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly DEFAULT_LIMIT=200

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;165;173;203m'    # #a5adcb - Dimmed text
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly CHART="󰈙"
readonly FILE=""
readonly WARN=""

# Logging functions
log_info() {
    echo -e "${BLUE}  ${NC}$1"
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_success() {
    echo -e "${SAPPHIRE}  ${NC}$1"
}

# Cleanup on exit
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo -e "\n${RED}${WARN}  ${NC}Analysis failed with exit code ${exit_code}" >&2
    fi
    cd "$SCRIPT_DIR"
}
trap cleanup EXIT

# Check required commands
check_dependencies() {
    local missing=()

    for cmd in find wc grep awk; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}${WARN}  ${NC}Missing dependencies: ${missing[*]}" >&2
        exit 1
    fi
}

# Count lines in a file, excluding comment-only lines
count_lines() {
    local file="$1"

    # Count total lines
    local total=$(wc -l < "$file")

    # Count comment-only lines (lines starting with // or ///)
    local comments=$(grep -cE '^\s*(//|///)' "$file" || true)

    # Count blank lines
    local blank=$(grep -cE '^\s*$' "$file" || true)

    # Code lines = total - comments - blank
    local code=$((total - comments - blank))

    echo "$code $comments $blank $total"
}

# Analyze files with threshold warnings
analyze_files() {
    local limit=$1
    local yellow_threshold=$((limit * 80 / 100))  # 80% of limit

    local rs_files
    rs_files=$(find "$SCRIPT_DIR" -name "*.rs" -not -path "*/target/*")

    if [ -z "$rs_files" ]; then
        log_warn "No .rs files found"
        exit 1
    fi

    local total_code=0
    local total_comments=0
    local total_blank=0
    local total_lines=0
    local file_count=0
    local max_code=0
    local max_file=""
    local min_code=999999
    local min_file=""
    local over_limit=0

    # Temporary file to store file data for sorting
    local temp_file=$(mktemp)

    # First pass: collect all file data
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            read -r code comments blank total <<< "$(count_lines "$file")"

            total_code=$((total_code + code))
            total_comments=$((total_comments + comments))
            total_blank=$((total_blank + blank))
            total_lines=$((total_lines + total))
            file_count=$((file_count + 1))

            # Track max
            if [ $code -gt $max_code ]; then
                max_code=$code
                max_file=$file
            fi

            # Track min
            if [ $code -lt $min_code ]; then
                min_code=$code
                min_file=$file
            fi

            # Count files over limit
            if [ $code -gt $limit ]; then
                over_limit=$((over_limit + 1))
            fi

            # Store: code|file for sorting
            echo "$code|$file" >> "$temp_file"
        fi
    done <<< "$rs_files"

    echo -e "${BLUE}${FILE}  File Analysis ${SUBTEXT}(limit: ${limit} lines, sorted by LOC):${NC}"
    echo ""

    # Second pass: display sorted by line count (descending)
    sort -t'|' -k1 -rn "$temp_file" | while IFS='|' read -r code file; do
        # Color code by size (green <80%, yellow 80%-100%, red >100%)
        local color icon
        if [ $code -gt $limit ]; then
            color=$RED
            icon="${WARN}"
        elif [ $code -gt $yellow_threshold ]; then
            color=$YELLOW
            icon="${WARN}"
        else
            color=$GREEN
            icon=" "
        fi

        # Display relative path for cleaner output
        local rel_file="${file#./}"
        printf "${color}${icon}  %4d lines${NC}  ${SUBTEXT}%s${NC}\n" "$code" "$rel_file"
    done

    # Cleanup temp file
    rm -f "$temp_file"

    # Calculate average
    local avg_code=0
    if [ $file_count -gt 0 ]; then
        avg_code=$((total_code / file_count))
    fi

    # Calculate percentages
    local code_pct=$(awk "BEGIN {printf \"%.1f\", ($total_code / $total_lines) * 100}")
    local comment_pct=$(awk "BEGIN {printf \"%.1f\", ($total_comments / $total_lines) * 100}")
    local blank_pct=$(awk "BEGIN {printf \"%.1f\", ($total_blank / $total_lines) * 100}")

    # Print summary
    echo ""
    echo -e "${GREEN}${CHART}  Summary:${NC}"
    echo ""
    printf "${TEXT}  Total files:     ${NC}%6d\n" "$file_count"
    printf "${TEXT}  Code lines:      ${NC}%6d ${SUBTEXT}(%s%%)${NC}\n" "$total_code" "$code_pct"
    printf "${TEXT}  Comment lines:   ${NC}%6d ${SUBTEXT}(%s%%)${NC}\n" "$total_comments" "$comment_pct"
    printf "${TEXT}  Blank lines:     ${NC}%6d ${SUBTEXT}(%s%%)${NC}\n" "$total_blank" "$blank_pct"
    printf "${YELLOW}  Total lines:     ${NC}%6d\n" "$total_lines"
    echo ""
    printf "${TEXT}  Average/file:    ${NC}%6d ${SUBTEXT}lines${NC}\n" "$avg_code"
    printf "${SAPPHIRE}  Largest file:    ${NC}%6d ${SUBTEXT}lines${NC} ${YELLOW}(%s)${NC}\n" "$max_code" "${max_file#./}"
    printf "${GREEN}  Smallest file:   ${NC}%6d ${SUBTEXT}lines${NC} ${TEXT}(%s)${NC}\n" "$min_code" "${min_file#./}"
    echo ""

    # Check if we have files over the limit
    if [ $over_limit -gt 0 ]; then
        log_warn "${over_limit} file(s) exceed ${limit} lines"
    else
        log_success "All files under ${limit} lines!"
    fi

    log_info "Comment lines include lines starting with ${TEXT}//${NC} or ${TEXT}///${NC}"
    log_info "Inline comments (code followed by //) are counted as code"
}

# Main execution
main() {
    # Parse optional line limit argument
    local limit=$DEFAULT_LIMIT
    if [ $# -gt 0 ]; then
        if [[ "$1" =~ ^[0-9]+$ ]]; then
            limit=$1
        else
            echo -e "${RED}${WARN}  ${NC}Error: Line limit must be a positive number" >&2
            echo "Usage: $0 [line_limit]" >&2
            echo "Example: $0 150" >&2
            exit 1
        fi
    fi

    echo -e "${MAUVE}[lines]${NC} ${BLUE}${CHART}${NC} Analyzing lines of code in Rust files..."
    echo ""

    check_dependencies
    analyze_files "$limit"

    echo ""
    log_success "Line count analysis complete!"
}

main "$@"
