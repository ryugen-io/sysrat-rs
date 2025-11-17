# sysrat

**sysrat** is a full-stack web-based configuration management system written in Rust.

- **Backend**: 🖥️ Rust + Axum (async web framework)
- **Frontend**: 📊 WASM + Ratzilla (terminal UI in the browser)
- **Features**: Configuration file management, Docker container management

ℹ️ **Last Updated**: 2025-11-17 (`7b61d9c`)

## 🔨 Tech Stack

**Rust Edition 2024**

- **Backend**: 🖥️ Axum v0.7
- **Frontend**: 📊 Ratzilla v0.2 (Ratatui-based WASM TUI)
- **Build**: 🔨 Trunk (WASM bundler), Cargo (Rust toolchain)

## ✨ Features

### Status Line System

- 🎯 **Modular component system** with 13 component types
- 🎨 **TOML-configurable** (built-in + XDG user override)
- 📦 **Split components** (state.rs, build.rs, text.rs) - all under 90 LOC
- 🎛️ **Per-pane configuration** (Menu shows only build info in 1 line)
- 🏷️ **Themed build output** with `[statusline]` tag
- ✅ **All checks passed** (clippy -D warnings, fmt, test, audit)

## 🚀 Management Scripts

- 📄 [rebuild.py](rebuild.py) - Build and deploy (backend + frontend)
- 📄 [start.py](start.py) - Start the sysrat server
- 📄 [status.py](status.py) - Check server status and stats
- 📄 [stop.py](stop.py) - Stop the sysrat server

## 📄 Configuration

- 📄 [CLAUDE.md](CLAUDE.md) - Developer documentation and AI assistant guide
- 📄 [justfile](justfile) - Task runner commands
- 📄 [sys/env/.env.example](sys/env/.env.example) - Environment configuration template
- 📄 [sysrat.toml](sysrat.toml) - Application configuration

## 📁 Project Structure

- 📁 `frontend/` - WASM-based TUI frontend (Ratzilla)
- 📁 `server/` - Backend API server (Rust + Axum)

## Quick Start

```bash
# Build and start server
./rebuild.py

# Check status
./status.py

# Stop server
./stop.py
```

## Access

Once started, access the web interface at: **http://localhost:3000**

## Documentation

See [CLAUDE.md](CLAUDE.md) for comprehensive developer documentation.
