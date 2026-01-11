# sysrat-rs - Project Overview

## Purpose
sysrat-rs is a TUI-based system configuration management tool with Docker container management capabilities. It provides a vim-like interface for editing system configuration files and managing Docker containers.

## Architecture
- **Workspace:** Rust workspace with 2 crates
- **Edition:** Rust 2024 (modern features like let-chains)

### Frontend (`sysrat-frontend`)
- WASM-based TUI application compiled to `cdylib`
- Uses `ratzilla` (ratatui fork for WASM) for terminal UI
- Communicates with backend via HTTP/JSON using `gloo-net`
- Features:
  - Vim-like keybindings (Normal/Insert mode)
  - Configurable themes (TOML-based)
  - File list browser
  - Container list with actions (start/stop/restart)
  - Text editor with `tui-textarea`

### Backend (`sysrat-server`)
- Axum 0.8.7 web server with Tokio async runtime
- Binary name: `sysrat`
- Serves static frontend from `frontend/dist`
- REST API endpoints:
  - `GET /api/configs` - List config files
  - `GET/POST /api/configs/{*filename}` - Read/Write configs
  - `GET /api/containers` - List Docker containers
  - `GET /api/containers/{id}/details` - Container details
  - `POST /api/containers/{id}/start|stop|restart` - Container actions

## Configuration
- Main config: `sysrat.toml` - Defines which files to manage
- Environment: `sys/env/.env` or `SYSRAT_ENV_FILE` env var
- Server: `SERVER_HOST` (default: 0.0.0.0), `SERVER_PORT` (default: 3000)

## Key Technologies
- **Frontend:** ratzilla, wasm-bindgen, web-sys, tui-textarea, gloo-net, serde
- **Backend:** axum, tokio, tower-http, serde, toml, walkdir
- **Tooling:** just (task runner), Python scripts, cargo-deny (security)
