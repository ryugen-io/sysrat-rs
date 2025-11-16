#!/bin/bash
# Lint shell scripts for common issues
# Basic linting without external tools

set -e
set -o pipefail

# Catppuccin Mocha color palette
readonly RED='\033[38;2;243;139;168m'
readonly GREEN='\033[38;2;166;227;161m'
readonly YELLOW='\033[38;2;249;226;175m'
readonly BLUE='\033[38;2;137;180;250m'
readonly MAUVE='\033[38;2;203;166;247m'
readonly SAPPHIRE='\033[38;2;116;199;236m'
readonly NC='\033[0m'

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
log_success() {
    echo -e "${GREEN}${CHECK}  ${NC}$1"
}

log_error() {
    echo -e "${RED}${CROSS}  ${NC}$1"
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_info() {
    echo -e "${BLUE}  ${NC}$1"
}

echo -e "${MAUVE}[lint]${NC} Linting shell scripts..."
echo ""

total_scripts=0
passed_scripts=0
total_issues=0

# Check each shell script
for script in *.sh; do
    [ -f "$script" ] || continue
    total_scripts=$((total_scripts + 1))

    echo -e "${BLUE}Checking ${NC}$script"
    issues=0

    # 1. Syntax check
    if ! bash -n "$script" 2>/dev/null; then
        log_error "Syntax error detected"
        issues=$((issues + 1))
    fi

    # 2. Check for set -e or set -o pipefail
    if ! grep -q "set -e" "$script" && ! grep -q "set -o errexit" "$script"; then
        log_warn "Missing 'set -e' (consider adding for safety)"
    fi

    if ! grep -q "set -o pipefail" "$script"; then
        log_warn "Missing 'set -o pipefail' (consider adding for pipe safety)"
    fi

    # 3. Check for shebang
    if ! head -n 1 "$script" | grep -q "^#!"; then
        log_error "Missing shebang line"
        issues=$((issues + 1))
    fi

    # 4. Check for unquoted variables (disabled - too many false positives)
    # This produces warnings for safe cases like echo -e "${COLOR}text${NC}"
    # Manual review is better than automated checking for this

    # 5. Check executable permission
    if [ ! -x "$script" ]; then
        log_warn "Script is not executable (chmod +x $script)"
    fi

    # 6. Check for 'local' in functions (skip - too many false positives)
    # Simple logging functions don't need local variables
    # This check is better handled by the Python linter (shellcheck_test.py)

    if [ $issues -eq 0 ]; then
        log_success "Passed basic linting"
        passed_scripts=$((passed_scripts + 1))
    else
        log_error "$issues critical issue(s) found"
        total_issues=$((total_issues + issues))
    fi

    echo ""
done

# Summary
echo -e "${GREEN}Summary:${NC}"
echo ""
printf "${BLUE}  Total scripts:     ${NC}%d\n" "$total_scripts"
printf "${GREEN}  Passed:            ${NC}%d\n" "$passed_scripts"
printf "${RED}  Critical issues:   ${NC}%d\n" "$total_issues"
echo ""

if [ $total_issues -eq 0 ]; then
    log_success "All shell scripts passed linting!"
    exit 0
else
    log_error "Some scripts have critical issues"
    exit 1
fi
