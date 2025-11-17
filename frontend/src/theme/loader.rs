use super::types::ThemeConfig;
use crate::storage;

/// Embedded default themes (Catppuccin variants)
const THEME_MOCHA: &str = include_str!("../../themes/mocha.toml");
const THEME_LATTE: &str = include_str!("../../themes/latte.toml");
const THEME_FRAPPE: &str = include_str!("../../themes/frappe.toml");
const THEME_MACCHIATO: &str = include_str!("../../themes/macchiato.toml");

/// Available theme names (defaults + user custom themes scanned at build time)
const THEME_NAMES: &[&str] = &["mocha", "latte", "frappe", "macchiato"];

/// Get list of available theme names
pub fn available_themes() -> &'static [&'static str] {
    THEME_NAMES
}

/// Load theme by name from embedded themes
pub fn load_theme_by_name(name: &str) -> Result<ThemeConfig, String> {
    let toml_content = match name {
        "mocha" => THEME_MOCHA,
        "latte" => THEME_LATTE,
        "frappe" => THEME_FRAPPE,
        "macchiato" => THEME_MACCHIATO,
        _ => return Err(format!("Unknown theme: {}", name)),
    };

    parse_theme_toml(toml_content)
}

/// Parse theme from TOML string
pub fn parse_theme_toml(toml: &str) -> Result<ThemeConfig, String> {
    toml::from_str(toml).map_err(|e| format!("Failed to parse theme TOML: {}", e))
}

/// Load theme preference from localStorage
pub fn load_theme_preference() -> Option<String> {
    storage::load_theme_preference()
}

/// Save theme preference to localStorage
pub fn save_theme_preference(name: &str) {
    storage::save_theme_preference(name);
}

/// Load the current theme (from localStorage or default)
pub fn load_current_theme() -> ThemeConfig {
    if let Some(theme_name) = load_theme_preference()
        && let Ok(theme) = load_theme_by_name(&theme_name)
    {
        return theme;
    }

    // Fallback to default mocha theme
    load_theme_by_name("mocha").expect("Default theme (mocha) must exist")
}

/// Get next theme name (for cycling)
pub fn next_theme_name(current: &str) -> &'static str {
    let themes = available_themes();
    if themes.is_empty() {
        return "mocha";
    }

    if let Some(idx) = themes.iter().position(|&t| t == current) {
        themes[(idx + 1) % themes.len()]
    } else {
        themes[0]
    }
}
