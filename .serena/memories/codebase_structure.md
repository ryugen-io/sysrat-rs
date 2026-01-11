# sysrat-rs - Codebase Structure

## Root Directory
```
sysrat-rs/
├── Cargo.toml          # Workspace definition
├── Cargo.lock
├── sysrat.toml         # Main app configuration
├── deny.toml           # cargo-deny security config
├── justfile            # Task runner commands
├── start.py/stop.py/status.py/rebuild.py  # Server management scripts
```

## Frontend (`frontend/`)
```
frontend/
├── Cargo.toml          # cdylib crate
├── build.rs            # Build-time code generation
├── index.html          # WASM entry point
├── keybinds.toml       # Keybind configuration
├── assets/             # ASCII art assets
├── themes/             # Theme TOML files (9 themes)
├── build_helpers/      # Build-time utilities
│   ├── theme/          # Theme code generation
│   ├── ascii.rs        # ASCII art embedding
│   ├── keybinds.rs     # Keybind code generation
│   └── statusline.rs   # Status line generation
└── src/
    ├── lib.rs          # Library entry (main function)
    ├── api/            # Backend API client
    │   ├── configs.rs  # Config file operations
    │   ├── containers.rs # Container operations
    │   └── types.rs    # API response types
    ├── events/         # Event handlers
    │   ├── container_list/ # Container list events
    │   ├── editor/     # Editor events (vim modes)
    │   ├── file_list.rs
    │   └── menu.rs
    ├── keybinds/       # Keybind management
    ├── state/          # Application state
    │   ├── app.rs      # Main AppState
    │   ├── refresh/    # State refresh logic
    │   └── *.rs        # Pane-specific state
    ├── storage/        # localStorage persistence
    ├── theme/          # Theme loading and types
    │   ├── types/      # Color, font, icon types
    │   └── *.rs        # Component-specific themes
    ├── ui/             # UI rendering
    │   ├── container_details/
    │   ├── menu/
    │   ├── status_line/
    │   └── *.rs        # Component renderers
    └── utils/          # Error handling utilities
```

## Backend (`server/`)
```
server/
├── Cargo.toml
└── src/
    ├── main.rs         # Entry point, router setup
    ├── version.rs      # Version info
    ├── config/         # Configuration loading
    │   ├── app_config.rs  # Main config loader
    │   ├── models.rs   # Config models
    │   └── scanner.rs  # Directory scanner
    └── routes/         # API route handlers
        ├── types.rs    # API response types
        ├── configs/    # Config file handlers
        │   ├── handlers.rs
        │   └── validation.rs
        └── containers/ # Container handlers
            ├── handlers.rs
            ├── actions.rs
            ├── details.rs
            └── parser/  # Docker output parsing
```

## Tooling (`sys/`)
```
sys/
├── env/               # Environment files
├── rust/              # Rust tooling scripts
│   ├── rustfmt.py, clippy.py, check.py, test_rust.py, audit.py, clean.py
├── html/              # HTML formatting/linting
├── layout/            # Layout configuration (statusline.toml)
├── theme/             # Theme utilities
└── utils/             # General utilities
    ├── precommit.py   # Pre-commit checks
    ├── lines.py       # Line counting
    └── *.py           # Various helpers
```
