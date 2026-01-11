# sysrat-rs - Code Style and Conventions

## Rust Edition
- **Edition 2024** - Uses modern Rust features like let-chains

## Naming Conventions
- **Types (Structs/Enums):** PascalCase (`FileInfo`, `AppState`, `ContainerDetails`)
- **Functions/Methods:** snake_case (`load_content`, `save_to_storage`)
- **Variables:** snake_case (`app_config`, `server_port`)
- **Constants:** SCREAMING_SNAKE_CASE
- **Modules:** snake_case (`container_list`, `file_list`)

## Code Organization

### Imports (ordered by)
1. `super::` (parent module)
2. `crate::` (current crate)
3. External crates (alphabetical)

Example:
```rust
use super::{ContainerListState, EditorState, FileListState};
use crate::{api::ContainerDetails, keybinds::Keybinds};
use serde::Serialize;
```

### Struct Definitions
- Derive macros on separate line: `#[derive(Serialize, Clone)]`
- All fields `pub` for data types
- Doc comments (`///`) for important fields
- Serde attributes for optional fields:
```rust
#[serde(skip_serializing_if = "Option::is_none")]
pub theme: Option<String>,
```

### Error Handling
- Use `eprintln!()` for error output
- `std::process::exit(1)` for fatal errors
- Match expressions for Result handling
- Warning messages for non-fatal errors

### Modern Rust Patterns
- **Let-chains:** `if let Some(x) = a && let Some(y) = b { }`
- **impl Into<T>:** For flexible string parameters
- **Arc for shared state:** `Arc::new(cfg)` with `.with_state()`

### Async Code
- `#[tokio::main]` for async main
- All IO operations async
- Use `.await.unwrap()` or proper error handling

## Documentation
- Doc comments (`///`) for public API
- Inline comments sparingly, only for non-obvious logic
- No docstrings required for internal functions

## Module Structure
- `mod.rs` files re-export submodule items
- Keep related code in subdirectories (e.g., `events/editor/`)
- Separate concerns: state, events, ui, api

## Type Patterns
- API response types in `types.rs` files
- State types in `state/` module
- Theme types in `theme/types/`

## Attributes
- `#[allow(dead_code)]` for intentionally unused code
- `#[derive(...)]` macros: Serialize, Clone, Debug as needed
