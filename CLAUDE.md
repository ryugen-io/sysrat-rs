# CLAUDE.md - AI Assistant Guide for Config Manager

This document provides comprehensive guidance for AI assistants working on the Config Manager codebase. It covers architecture, development workflows, conventions, and best practices.

**Last Updated:** 2025-11-15
**Version:** 0.1.0

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Architecture](#codebase-architecture)
3. [Directory Structure](#directory-structure)
4. [Development Workflows](#development-workflows)
5. [Code Conventions](#code-conventions)
6. [Testing Guidelines](#testing-guidelines)
7. [Security Considerations](#security-considerations)
8. [Common Tasks](#common-tasks)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Config Manager** is a full-stack web-based configuration management system written in Rust. It provides:

- **Configuration File Management**: Browse, edit, and save system configuration files (nginx, Docker, SSH, etc.)
- **Docker Container Management**: List, inspect, start, stop, and restart containers
- **Modern TUI Interface**: WASM-based terminal UI using Ratatui
- **Security-First Design**: Extension whitelisting, readonly flags, and audit logging

### Tech Stack

- **Backend**: Rust + Axum (async web framework)
- **Frontend**: Rust + WASM + Ratzilla (terminal UI in the browser)
- **Build Tools**: Cargo, Trunk (WASM bundler), Just (task runner)
- **Runtime**: Tokio (async runtime)

### Key Metrics

- **Total Lines of Code**: ~1,802 lines
- **Rust Edition**: 2024
- **Minimum Rust Version**: 1.85+

---

## Codebase Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│      Browser / WASM Runtime             │
│  ┌─────────────────────────────────────┐│
│  │  Frontend (Ratzilla TUI)            ││
│  │  - Ratatui for rendering            ││
│  │  - Vim-style key event handling     ││
│  │  - State management (AppState)      ││
│  │  - Browser localStorage persistence ││
│  └─────────────────────────────────────┘│
└──────────────┬──────────────────────────┘
               │ HTTP API (JSON)
┌──────────────▼──────────────────────────┐
│    Backend Server (Axum + Tokio)       │
│  ┌─────────────────────────────────────┐│
│  │  API Routes                         ││
│  │  ├─ /api/configs (file mgmt)        ││
│  │  └─ /api/containers (Docker)        ││
│  ├─────────────────────────────────────┤│
│  │  Config Manager                     ││
│  │  ├─ File loading & validation       ││
│  │  ├─ Directory scanning              ││
│  │  └─ Extension whitelisting          ││
│  ├─────────────────────────────────────┤│
│  │  Docker Integration (CLI)           ││
│  └─────────────────────────────────────┘│
└──────────────┬──────────────────────────┘
               │
         ┌─────┴──────────────────────┐
         ▼                             ▼
   ┌──────────────┐          ┌───────────────┐
   │  File System │          │  Docker API   │
   └──────────────┘          └───────────────┘
```

### Monorepo Structure

This is a **Cargo workspace** with two independent projects:

1. **server/** - Backend API server (Axum)
2. **frontend/** - WASM-based TUI frontend (Ratzilla)

Both share the `Cargo.lock` file but have separate `Cargo.toml` manifests.

---

## Directory Structure

```
/home/user/configmanager-rs/
├── Cargo.toml                  # Workspace root
├── Cargo.lock                  # Locked dependency versions
├── config-manager.toml         # Application configuration
├── .env.example                # Environment variable template
├── deny.toml                   # Security audit config
├── justfile                    # Task automation
├── rebuild.sh                  # Full build script
├── start.sh & stop.sh          # Server lifecycle scripts
│
├── server/                     # Backend API server
│   ├── Cargo.toml             # Server dependencies
│   └── src/
│       ├── main.rs            # Entry point, server setup
│       ├── version.rs         # Version information
│       ├── config/            # Configuration management
│       │   ├── mod.rs
│       │   ├── app_config.rs  # AppConfig struct
│       │   ├── models.rs      # Config data models
│       │   └── scanner.rs     # Directory scanning
│       └── routes/            # HTTP route handlers
│           ├── mod.rs
│           ├── types.rs       # API request/response types
│           ├── configs/       # Config file CRUD
│           │   ├── mod.rs
│           │   ├── handlers.rs
│           │   └── validation.rs
│           └── containers/    # Docker operations
│               ├── mod.rs
│               ├── handlers.rs
│               ├── details.rs
│               ├── actions.rs
│               └── parser/    # Docker output parsing
│
└── frontend/                   # WASM TUI frontend
    ├── Cargo.toml             # WASM dependencies
    ├── build.rs               # Build-time code generation
    ├── theme.toml             # Catppuccin Mocha colors
    ├── keybinds.toml          # Keybind configuration
    ├── index.html             # Entry HTML
    ├── build_helpers/         # Build-time utilities
    └── src/
        ├── lib.rs             # WASM entry point
        ├── api/               # API client layer
        │   ├── mod.rs
        │   ├── types.rs       # Shared API types
        │   ├── configs.rs     # Config API calls
        │   └── containers.rs  # Container API calls
        ├── events/            # Keyboard event handling
        │   ├── mod.rs         # Global dispatcher
        │   ├── menu.rs
        │   ├── file_list.rs
        │   ├── editor/        # Text editor events
        │   └── container_list/
        ├── state/             # Application state
        │   ├── mod.rs
        │   ├── app.rs         # Main AppState
        │   ├── pane.rs        # Pane & VimMode enums
        │   ├── menu.rs
        │   ├── file_list.rs
        │   ├── editor.rs
        │   ├── container_list.rs
        │   ├── refresh/       # Background refresh logic
        │   └── status_helper.rs
        ├── ui/                # Ratatui rendering
        │   ├── mod.rs         # Main render function
        │   ├── menu.rs
        │   ├── file_list.rs
        │   ├── editor.rs
        │   ├── container_list.rs
        │   ├── container_details/
        │   └── status_line/
        ├── storage/           # Browser persistence
        │   ├── mod.rs
        │   ├── types.rs
        │   ├── local.rs
        │   └── generic.rs
        ├── theme/             # Color theming
        │   └── mod.rs
        ├── keybinds/          # Keybind loading
        │   ├── mod.rs
        │   ├── types.rs
        │   └── help_text.rs
        └── utils/             # Utility functions
            ├── mod.rs
            └── error.rs
```

### Key Entry Points

| Component | File | Purpose |
|-----------|------|---------|
| **Backend** | `server/src/main.rs:1` | Axum server setup, listens on `0.0.0.0:3000` |
| **Frontend** | `frontend/src/lib.rs:1` | WASM entry point, initializes Ratzilla terminal |
| **Config** | `config-manager.toml:1` | Application configuration (files, extensions) |
| **Build** | `rebuild.sh:1` | Full build orchestration script |

---

## Development Workflows

### Prerequisites

Install required tools:

```bash
# Rust toolchain (1.85+)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# WASM bundler
cargo install trunk

# Security audit tool
cargo install cargo-auditable

# Task runner (optional but recommended)
cargo install just
```

### Quick Start

```bash
# Full rebuild and start server
./rebuild.sh

# Or using Just
just rebuild
```

Access the application at: `http://localhost:3000`

### Build Options

```bash
# Build backend only
./rebuild.sh --backend-only
just build-backend

# Build frontend only
./rebuild.sh --frontend-only
just build-frontend

# Build without starting server
./rebuild.sh --no-server

# Skip code formatting
./rebuild.sh --skip-format
```

### Development Cycle

1. **Make changes** to source code
2. **Format code**: `just fmt` (or auto-format in `rebuild.sh`)
3. **Lint**: `just clippy` (check for warnings)
4. **Build**: `just rebuild` or `./rebuild.sh`
5. **Test manually** via the web interface
6. **Commit** with descriptive messages

### Server Lifecycle

```bash
# Start server (background process)
./start.sh
# PID saved to .server.pid
# Logs to server.log

# Stop server
./stop.sh

# View logs
tail -f server.log

# Check if running
cat .server.pid
ps -p $(cat .server.pid)
```

### Build System Deep Dive

#### Backend Build (server/)

```bash
# Development build with auditable
cargo auditable build --bin config-manager-server

# Release build with auditable
cargo auditable build --release --bin config-manager-server

# Binary location: target/release/config-manager-server
```

**Note**: `cargo-auditable` embeds dependency metadata for security audits.

#### Frontend Build (frontend/)

```bash
cd frontend

# Development build
trunk build

# Release build (optimized WASM)
trunk build --release

# Output: frontend/dist/
#   - index.html
#   - *.wasm
#   - JavaScript loader
```

**Build Process**:
1. `build.rs` runs at compile time:
   - Extracts dependency versions
   - Reads `theme.toml` and injects colors as env vars
   - Sets build date and git hash
2. Trunk compiles Rust to WASM
3. Outputs bundled assets to `dist/`
4. Backend serves `dist/` at root path `/`

---

## Code Conventions

### Rust Edition and Style

- **Edition**: 2024 (both server and frontend)
- **Formatting**: Standard `rustfmt` (run `just fmt` or `cargo fmt --all`)
- **Linting**: Clippy with `-D warnings` (fail on warnings)

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Files** | `snake_case.rs` | `app_config.rs` |
| **Modules** | `snake_case` | `mod config` |
| **Structs** | `PascalCase` | `AppState`, `FileInfo` |
| **Enums** | `PascalCase` | `Pane`, `VimMode` |
| **Functions** | `snake_case` | `fetch_file_list()` |
| **Constants** | `SCREAMING_SNAKE_CASE` | `SERVER_PORT` |
| **Variables** | `snake_case` | `file_content` |

### Module Organization

Each module should have a `mod.rs` that re-exports public items:

```rust
// config/mod.rs
mod app_config;
mod models;
mod scanner;

pub use app_config::AppConfig;
pub use models::{Config, ConfigFile, ConfigDirectory};
```

### Error Handling

- Use `Result<T, E>` for fallible operations
- Backend: Return HTTP status codes (400, 404, 500)
- Frontend: Use `utils::error::format_error()` for display
- Log errors with context: `log_error("Failed to read file: {}", e)`

### Comments and Documentation

- Document public APIs with doc comments (`///`)
- Explain complex logic with inline comments (`//`)
- Add module-level documentation in `mod.rs` files

Example:

```rust
/// Fetches the list of configuration files from the server.
///
/// # Errors
///
/// Returns an error if the HTTP request fails or the response
/// cannot be parsed.
pub async fn fetch_file_list() -> Result<Vec<FileInfo>, String> {
    // ...
}
```

### State Management Conventions

**Backend**:
- Use Axum's `State` extractor for shared state
- `AppConfig` is `Arc<AppConfig>` for thread-safe sharing

**Frontend**:
- All state in `AppState` struct
- Use `Rc<RefCell<AppState>>` for shared mutable state in WASM
- Save to localStorage after every state change

### API Conventions

**Request/Response Format**:
- Always use JSON (`application/json`)
- Error responses: `{ "error": "message" }`
- Success responses: `{ "success": true, ... }`

**Endpoint Naming**:
- Plural nouns for collections: `/api/configs`
- ID-based paths: `/api/containers/:id/details`
- Action verbs as path segments: `/api/containers/:id/start`

---

## Testing Guidelines

### Current State

⚠️ **No automated tests exist currently.**

The project relies on:
1. Manual testing via the web interface
2. Integration testing through full-stack interaction
3. `cargo clippy` for static analysis
4. `cargo fmt` for style consistency

### Testing Recommendations for Contributors

When adding features, consider adding:

1. **Unit Tests**: For individual functions
   ```rust
   #[cfg(test)]
   mod tests {
       use super::*;

       #[test]
       fn test_parse_container_id() {
           // ...
       }
   }
   ```

2. **Integration Tests**: For API endpoints
   ```rust
   // server/tests/api_tests.rs
   #[tokio::test]
   async fn test_list_configs() {
       // ...
   }
   ```

3. **Manual Test Plan**: Document test steps for complex features

### Running Lints

```bash
# Format check
cargo fmt --all -- --check

# Clippy (fails on warnings)
just clippy
cargo clippy --all-targets -- -D warnings
```

---

## Security Considerations

### File Access Controls

1. **Extension Whitelist** (`config-manager.toml`):
   ```toml
   [settings]
   allowed_extensions = ["conf", "toml", "txt", "sh", ...]
   ```
   - Only whitelisted extensions can be edited
   - Prevents execution of arbitrary files

2. **Readonly Files**:
   ```toml
   [[files]]
   path = "/etc/docker/daemon.json"
   readonly = true  # Cannot be modified via API
   ```

3. **Configuration Validation**:
   - Files must be declared in `config-manager.toml`
   - No arbitrary path access
   - Path traversal prevention in `validation.rs`

### Credential Handling

**Never commit**:
- `.env` files (use `.env.example` instead)
- Certificates (`.pem`, `.key`, `.crt`)
- SSH keys
- Cloud credentials
- Database files

See `.gitignore:24-60` for full exclusion list.

### Docker Security

- Docker commands executed via CLI (not direct socket access)
- Requires Docker daemon and proper user permissions
- Container actions logged for audit trail

### Dependency Security

**cargo-deny** configured (`deny.toml`):
- Vulnerability scanning enabled
- License compliance checks
- Multiple version warnings

Run security audit:
```bash
cargo install cargo-deny
cargo deny check
```

### Environment Variables

```bash
# .env (create from .env.example)
SERVER_HOST=localhost  # For display URLs only
# SERVER_PORT=3000     # Optional, defaults to 3000
```

**Security Note**: `SERVER_HOST` affects UI display only, not actual binding (always `0.0.0.0:3000`).

---

## Common Tasks

### Adding a New Configuration File

1. Edit `config-manager.toml`:
   ```toml
   [[files]]
   path = "/etc/myapp/config.conf"
   name = "myapp-config"
   description = "My Application Configuration"
   readonly = false  # or true to prevent editing
   ```

2. Ensure extension is in `allowed_extensions`:
   ```toml
   [settings]
   allowed_extensions = ["conf", ...]
   ```

3. Restart server:
   ```bash
   ./stop.sh && ./start.sh
   ```

4. Refresh browser to see new file in list

### Adding a New Directory to Scan

1. Edit `config-manager.toml`:
   ```toml
   [[directories]]
   path = "~/.config/myapp"
   name = "myapp"
   depth = 3              # Max recursion depth
   types = ["conf", "txt"] # Filter by extension
   description = "My App Configuration Directory"
   readonly = false
   ```

2. Files will be auto-scanned on server start

### Adding a New API Endpoint

**Backend** (`server/src/routes/`):

1. Define handler in appropriate module:
   ```rust
   // routes/configs/handlers.rs
   pub async fn my_new_handler(
       State(config): State<Arc<AppConfig>>,
   ) -> Result<Json<MyResponse>, (StatusCode, String)> {
       // ...
   }
   ```

2. Add route in `server/src/main.rs`:
   ```rust
   let app = Router::new()
       .route("/api/my-endpoint", get(routes::my_new_handler))
       // ...
   ```

**Frontend** (`frontend/src/api/`):

1. Add API function in appropriate module:
   ```rust
   // api/configs.rs
   pub async fn fetch_my_data() -> Result<MyData, String> {
       let response = Request::get("/api/my-endpoint")
           .send()
           .await
           .map_err(|e| format_error(&e))?;
       // ...
   }
   ```

2. Call from event handler or init:
   ```rust
   // events/mod.rs or lib.rs
   spawn_local(async {
       let data = api::fetch_my_data().await?;
       // Update state
   });
   ```

### Modifying the TUI Layout

**File**: `frontend/src/ui/mod.rs:1`

Example: Change file list width from 25% to 30%:

```rust
// ui/mod.rs
let main_chunks = Layout::default()
    .direction(Direction::Horizontal)
    .constraints([
        Constraint::Percentage(30),  // Changed from 25
        Constraint::Percentage(69),  // Changed from 74
        Constraint::Percentage(1),
    ])
    .split(frame.size());
```

### Adding a New Keybind

1. Edit `frontend/keybinds.toml`:
   ```toml
   [file_list]
   my_new_action = "Ctrl-N"
   ```

2. Update `frontend/src/events/file_list.rs`:
   ```rust
   pub fn handle_file_list_key_event(state: &mut AppState, key: KeyEvent) {
       let keybinds = &state.keybinds.file_list;

       if key_matches(&key, &keybinds.my_new_action) {
           // Handle action
       }
   }
   ```

3. Rebuild frontend:
   ```bash
   just build-frontend
   ```

### Changing the Color Theme

Edit `frontend/theme.toml`:

```toml
[colors]
my_color = [255, 128, 0]  # RGB values

[semantic]
accent = "my_color"  # Use custom color
```

Theme is injected at build time via `frontend/build.rs`.

---

## API Reference

### Configuration File Management

#### List All Configuration Files

```
GET /api/configs
```

**Response**:
```json
{
  "files": [
    {
      "name": "nginx.conf",
      "description": "Nginx main configuration",
      "readonly": false
    }
  ]
}
```

#### Read Configuration File

```
GET /api/configs/:filename
```

**Response**:
```json
{
  "content": "# File contents here..."
}
```

**Errors**:
- `404`: File not found in configuration
- `400`: Invalid filename
- `500`: File read error

#### Write Configuration File

```
POST /api/configs/:filename
Content-Type: application/json

{
  "content": "# Updated file contents..."
}
```

**Response**:
```json
{
  "success": true
}
```

**Errors**:
- `400`: Readonly file, invalid filename, or validation error
- `500`: File write error

### Docker Container Management

#### List All Containers

```
GET /api/containers
```

**Response**:
```json
{
  "containers": [
    {
      "id": "abc123...",
      "name": "my-container",
      "state": "running",
      "status": "Up 2 hours"
    }
  ]
}
```

#### Get Container Details

```
GET /api/containers/:id/details
```

**Response**:
```json
{
  "details": {
    "id": "abc123...",
    "name": "my-container",
    "image": "nginx:latest",
    "state": "running",
    "ports": [
      {"container": "80", "host": "8080", "protocol": "tcp"}
    ],
    "volumes": [
      {"source": "/host/path", "destination": "/container/path"}
    ],
    "networks": ["bridge"],
    "environment": ["VAR=value"],
    "restart_policy": "always",
    "health": "healthy"
  }
}
```

#### Start Container

```
POST /api/containers/:id/start
```

**Response**:
```json
{
  "success": true,
  "message": "Container started successfully"
}
```

#### Stop Container

```
POST /api/containers/:id/stop
```

#### Restart Container

```
POST /api/containers/:id/restart
```

All container actions return:
```json
{
  "success": true,
  "message": "..."
}
```

**Errors**:
- `500`: Docker command failed (message includes stderr)

---

## Troubleshooting

### Build Issues

**Problem**: `cargo auditable` not found

```bash
# Solution:
cargo install cargo-auditable
```

**Problem**: `trunk` not found

```bash
# Solution:
cargo install trunk
```

**Problem**: WASM build fails with "target not installed"

```bash
# Solution:
rustup target add wasm32-unknown-unknown
```

### Runtime Issues

**Problem**: Port 3000 already in use

```bash
# Solution:
./stop.sh  # Stop existing server
# Or find and kill the process:
lsof -i :3000
kill <PID>
```

**Problem**: Server starts but port not listening

```bash
# Check logs:
tail -f server.log

# Verify config file exists:
ls -la config-manager.toml
```

**Problem**: Frontend shows "Failed to fetch"

- Check backend is running: `ps -p $(cat .server.pid)`
- Check browser console for errors (F12)
- Verify API endpoint in browser: `http://localhost:3000/api/configs`

### Configuration Issues

**Problem**: File not appearing in file list

1. Check `config-manager.toml` has entry:
   ```toml
   [[files]]
   path = "/path/to/file"
   name = "file-name"
   ```

2. Check file extension is in `allowed_extensions`:
   ```toml
   [settings]
   allowed_extensions = ["conf", ...]
   ```

3. Restart server: `./stop.sh && ./start.sh`

**Problem**: "Readonly file" error when saving

- Check `readonly` flag in `config-manager.toml`:
  ```toml
  [[files]]
  path = "/etc/nginx/nginx.conf"
  readonly = false  # Set to false to allow editing
  ```

### Docker Issues

**Problem**: Docker containers not listed

```bash
# Verify Docker is running:
docker ps

# Check Docker daemon permissions:
docker info
```

**Problem**: Container actions fail

- Ensure Docker daemon is running
- Check user has Docker permissions: `groups | grep docker`
- View server logs: `tail -f server.log`

### Development Issues

**Problem**: Changes not reflected in browser

1. Rebuild: `./rebuild.sh`
2. Hard refresh browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
3. Clear browser cache
4. Check `frontend/dist/` was updated

**Problem**: Clippy warnings fail build

```bash
# View warnings:
just clippy

# Fix auto-fixable issues:
cargo clippy --fix --all-targets

# Manual fixes required for remaining issues
```

---

## Best Practices for AI Assistants

### When Making Changes

1. **Always read files before editing**:
   - Use `Read` tool before `Edit` or `Write`
   - Understand context and existing patterns

2. **Follow existing code structure**:
   - Match indentation (spaces, not tabs)
   - Follow naming conventions
   - Preserve error handling patterns

3. **Update related files**:
   - Backend changes may require frontend updates
   - API changes need updates in both `server/routes/` and `frontend/api/`

4. **Test after changes**:
   - Run `just clippy` to catch issues
   - Run `just fmt` to format code
   - Rebuild and manually test: `./rebuild.sh`

5. **Document non-obvious logic**:
   - Add comments explaining "why", not just "what"
   - Update this file (CLAUDE.md) if architecture changes

### Common Pitfalls to Avoid

1. **Don't break the build**:
   - Always run `just clippy` before committing
   - Fix all warnings (project uses `-D warnings`)

2. **Don't bypass security**:
   - Never disable extension whitelisting
   - Don't remove readonly checks
   - Keep credentials out of version control

3. **Don't mix concerns**:
   - Keep API logic in `server/routes/`
   - Keep UI logic in `frontend/ui/`
   - Keep state management in `frontend/state/`

4. **Don't forget WASM constraints**:
   - Frontend can't do filesystem I/O directly
   - Must use `gloo-net` for HTTP, not `reqwest`
   - Use `wasm_bindgen` for browser API access

5. **Don't hardcode paths**:
   - Use `config-manager.toml` for file paths
   - Use environment variables for runtime config

### File References

When referencing code locations, use the format: `file:line`

Examples:
- Server entry point: `server/src/main.rs:1`
- AppState definition: `frontend/src/state/app.rs:1`
- Config loading: `server/src/config/app_config.rs:1`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-11-15 | Initial CLAUDE.md creation |

---

## Additional Resources

- **Axum Documentation**: https://docs.rs/axum/
- **Ratatui Book**: https://ratatui.rs/
- **Ratzilla GitHub**: https://github.com/EdJoPaTo/ratzilla
- **Trunk Documentation**: https://trunkrs.dev/
- **WASM Book**: https://rustwasm.github.io/book/

---

## Contact and Support

For issues or questions:
- **Repository**: Check GitHub issues
- **Logs**: Review `server.log` for runtime errors
- **Build Errors**: Run `just clippy` for detailed diagnostics

---

**End of CLAUDE.md**
