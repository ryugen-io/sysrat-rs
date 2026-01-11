# sysrat-rs - Suggested Commands

## Build & Development

### Full Build
```bash
just rebuild              # Format + build backend (auditable) + build frontend (trunk)
just rebuild-backend      # Backend only
just rebuild-frontend     # Frontend only
just rebuild-no-server    # Build without starting server
```

### Server Management
```bash
just start    # Start server (background)
just stop     # Stop server
just status   # Check server status
just logs     # View server logs (tail -f server.log)
```

## Code Quality

### Rust Checks
```bash
just fmt      # Format Rust code (rustfmt)
just clippy   # Run clippy linter
just check    # Run cargo check
just test     # Run tests
just audit    # Security audit (cargo-deny)
just clean    # Clean build artifacts
just rust-checks  # Run all Rust checks (fmt + clippy + check + test)
```

### Python Checks
```bash
just pylint       # Python linting (ruff)
just pycompile    # Python syntax check
just pyclean      # Clean Python cache
just python-checks  # All Python checks
```

### HTML Checks
```bash
just htmllint         # HTML validation
just htmlformat       # HTML formatting
just htmlformat-check # HTML format check (no changes)
just html-checks      # All HTML checks
```

### All Quality Checks
```bash
just all-checks   # Rust + Python + HTML checks
just pc           # Pre-commit (full output)
just pc-summary   # Pre-commit (summary only)
```

## Utilities
```bash
just lines        # Count lines of code
just loc          # Alias for lines
just fix-nerdfonts    # Fix Nerd Font icons
just remove-emojis    # Remove emojis from files
just venv             # Python venv management
just xdg-paths        # Show XDG paths
```

## Direct Commands (without just)
```bash
# Server
./start.py
./stop.py
./status.py
./rebuild.py [--backend-only|--frontend-only|--no-server]

# Rust
python3 sys/rust/rustfmt.py --recursive
python3 sys/rust/clippy.py --recursive
python3 sys/rust/check.py --recursive
python3 sys/rust/test_rust.py --recursive

# Cargo
cargo build -p sysrat-server
cargo build -p sysrat-frontend --target wasm32-unknown-unknown

# Trunk (frontend)
trunk build frontend/index.html --release
```

## Environment Variables
```bash
SYSRAT_ENV_FILE=path/to/.env   # Custom env file
SERVER_HOST=0.0.0.0            # Server bind host
SERVER_PORT=3000               # Server port
```

## Standard Linux Tools
```bash
git, ls, cd, grep, find, tail, cat  # Available as usual
```
