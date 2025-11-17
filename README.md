# SysRat

**SysRat** is a full-stack web-based configuration management system written in Rust.

- **Backend**: Rust + Axum (async web framework)
- **Frontend**: WASM + Ratzilla (terminal UI in the browser)
- **Features**: Configuration file management, Docker container management

## Management Scripts

- [rebuild.py](rebuild.py) - Build and deploy (backend + frontend)
- [start.py](start.py) - Start the SysRat server
- [status.py](status.py) - Check server status and stats
- [stop.py](stop.py) - Stop the SysRat server

## Configuration

- [CLAUDE.md](CLAUDE.md) - Developer documentation and AI assistant guide
- [justfile](justfile) - Task runner commands
- [sys/env/.env.example](sys/env/.env.example) - Environment configuration template
- [sysrat.toml](sysrat.toml) - Application configuration

## Project Structure

- `frontend/` - WASM-based TUI frontend (Ratzilla)
- `server/` - Backend API server (Rust + Axum)

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
