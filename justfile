# Config Manager - Just commands

# Rebuild project (format, build backend with auditable, build frontend with trunk)
rebuild:
    ./rebuild.py

# Rebuild backend only
rebuild-backend:
    ./rebuild.py --backend-only

# Rebuild frontend only
rebuild-frontend:
    ./rebuild.py --frontend-only

# Rebuild without starting server
rebuild-no-server:
    ./rebuild.py --no-server

# Format all code
fmt:
    python3 sys/rust/rustfmt.py --recursive

# Run clippy on all targets
clippy:
    python3 sys/rust/clippy.py --recursive

# Run cargo check
check:
    python3 sys/rust/check.py --recursive

# Run tests
test:
    python3 sys/rust/test_rust.py --recursive

# Run security audit
audit:
    python3 sys/rust/audit.py --recursive

# Clean build artifacts
clean:
    python3 sys/rust/clean.py --recursive

# Start server (background process)
start:
    ./start.py

# Stop server
stop:
    ./stop.py

# Check server status
status:
    ./status.py

# View server logs
logs:
    tail -f server.log

# Count lines of code (entire repo, excludes build artifacts)
lines:
    python3 sys/utils/lines.py

# Alias for lines
loc: lines

# Python linting
pylint:
    python3 sys/utils/pylint.py --recursive

# Python syntax check (compile all .py files)
pycompile:
    python3 sys/utils/pycompile.py --recursive

# Clean Python cache files
pyclean:
    python3 sys/utils/pyclean.py --recursive

# Fix Nerd Font icons in files
fix-nerdfonts:
    python3 sys/utils/fix_nerdfonts.py

# Remove emojis from files
remove-emojis:
    python3 sys/utils/remove_emojis.py

# Create/manage Python virtual environment
venv:
    python3 sys/utils/venv.py

# Show XDG paths
xdg-paths:
    python3 sys/utils/xdg_paths.py

# Enable debug code
debug-enable:
    python3 sys/rust/debug.py enable

# Disable debug code
debug-disable:
    python3 sys/rust/debug.py disable

# Show debug status
debug-status:
    python3 sys/rust/debug.py status

# HTML linting and validation
htmllint:
    python3 sys/html/htmllint.py --recursive

# HTML formatting
htmlformat:
    python3 sys/html/htmlformat.py --recursive

# HTML formatting check (no modifications)
htmlformat-check:
    python3 sys/html/htmlformat.py --recursive --check

# Run all Rust checks (fmt, clippy, check, test)
rust-checks:
    @python3 sys/rust/rustfmt.py --recursive
    @echo -e "\033[38;2;186;194;222m────────────────────────────────────────\033[0m"
    @python3 sys/rust/clippy.py --recursive
    @echo -e "\033[38;2;186;194;222m────────────────────────────────────────\033[0m"
    @python3 sys/rust/check.py --recursive
    @echo -e "\033[38;2;186;194;222m────────────────────────────────────────\033[0m"
    @python3 sys/rust/test_rust.py --recursive

# Run all Python checks (pylint, pycompile)
python-checks:
    @echo -e "\033[38;2;186;194;222m────────────────────────────────────────\033[0m"
    @python3 sys/utils/pylint.py --recursive
    @echo -e "\033[38;2;186;194;222m────────────────────────────────────────\033[0m"
    @python3 sys/utils/pycompile.py --recursive

# Run all HTML checks (format, lint)
html-checks:
    @echo -e "\033[38;2;186;194;222m────────────────────────────────────────\033[0m"
    @python3 sys/html/htmlformat.py --recursive --check
    @echo -e "\033[38;2;186;194;222m────────────────────────────────────────\033[0m"
    @python3 sys/html/htmllint.py --recursive

# Run all checks (Rust + Python + HTML)
all-checks: rust-checks python-checks html-checks

# Pre-commit checks (full output)
pc:
    python3 sys/utils/precommit.py --verbose

# Pre-commit checks (summary only)
pc-summary:
    python3 sys/utils/precommit.py --summary

# Alias for backward compatibility
pre-commit: pc
