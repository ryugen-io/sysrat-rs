# Config Manager - Just commands

# Rebuild project (format, build backend with auditable, build frontend with trunk)
rebuild:
    ./rebuild.sh

# Format all code
fmt:
    cargo fmt --all
    cd frontend && cargo fmt

# Run clippy on all targets
clippy:
    cargo clippy --all-targets -- -D warnings
    cd frontend && cargo clippy --all-targets -- -D warnings

# Build backend only
build-backend:
    cargo build --release

# Build backend with auditable
build-backend-auditable:
    cargo auditable build --release

# Build frontend only
build-frontend:
    cd frontend && trunk build --release

# Run backend server
run:
    cargo run --bin config-manager-server

# Clean build artifacts
clean:
    cargo clean
    cd frontend && cargo clean

# Count lines of code
loc:
    fish -c "locode rs"
