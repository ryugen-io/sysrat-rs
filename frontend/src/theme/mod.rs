/// # Theme Design Pattern
///
/// This module defines the standardized theme system for the sysrat TUI.
///
/// ## Architecture
///
/// The theme system consists of three layers:
///
/// 1. **Base Colors** (`ThemeConfig` struct): RGB colors loaded from TOML (build-time or runtime)
/// 2. **Semantic Colors** (accessor methods): Meaningful color mappings (e.g., accent, error)
/// 3. **Component Themes** (e.g., `FileListTheme`, `MenuTheme`): Style builders for UI components
///
/// ## Theme Loading
///
/// Themes are loaded from embedded TOML files at runtime:
/// - Default themes embedded in WASM (mocha, latte, frappe, macchiato)
/// - User custom themes scanned from `~/.config/sysrat/themes/` at build time
/// - Theme preference stored in browser localStorage
/// - Fallback to Mocha theme if preference not found
///
/// ## Adding Custom Themes
///
/// 1. Create `~/.config/sysrat/themes/my-theme.toml`
/// 2. Rebuild frontend: `just build-frontend` or `./rebuild.py`
/// 3. Select theme from menu (automatically embedded in WASM)
///
/// ## Design Principles
///
/// Component theme modules should follow these conventions:
///
/// ### Standard Style Methods
///
/// Every focusable widget should implement:
/// - `border_focused(theme)` - Border style when the widget has focus
/// - `border_unfocused(theme)` - Border style when the widget is not focused
///
/// Every list-like widget should implement:
/// - `normal_item_style(theme)` - Style for regular list items
/// - `selected_item_style(theme)` - Style for the selected/highlighted item
/// - `selected_prefix()` - Text prefix for selected items (e.g., "> ")
// Component theme modules
pub mod container_list;
pub mod editor;
pub mod file_list;
pub mod menu;
pub mod status_line;

// Theme core modules
mod builder;
mod loader;
mod types;

// Public re-exports
pub use loader::{
    load_current_theme, load_theme_by_name, load_theme_preference, next_theme_name,
    save_theme_preference,
};
pub use types::ThemeConfig;

/// Common prefix for selected items in lists
pub const SELECTED_PREFIX: &str = "> ";

/// Common prefix for normal items in lists
pub const NORMAL_PREFIX: &str = "  ";
