use super::types::ThemeConfig;
use crate::storage;

/// Available theme names (dynamically scanned at build time from frontend/themes/)
const THEME_NAMES_STR: &str = env!("THEME_NAMES");

/// Get list of available theme names
pub fn available_themes() -> Vec<&'static str> {
    THEME_NAMES_STR.split(',').collect()
}

/// Load theme by name from embedded themes
pub fn load_theme_by_name(name: &str) -> Result<ThemeConfig, String> {
    // Load the theme content at compile time using include_str!
    // All themes are embedded at build time
    let toml_content = match name {
        "mocha" => include_str!("../../themes/mocha.toml"),
        "latte" => include_str!("../../themes/latte.toml"),
        "frappe" => include_str!("../../themes/frappe.toml"),
        "macchiato" => include_str!("../../themes/macchiato.toml"),
        "dracula" => include_str!("../../themes/dracula.toml"),
        "gruvbox-dark" => include_str!("../../themes/gruvbox-dark.toml"),
        "gruvbox-light" => include_str!("../../themes/gruvbox-light.toml"),
        "cyberpunk" => include_str!("../../themes/cyberpunk.toml"),
        "synthwave" => include_str!("../../themes/synthwave.toml"),
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
pub fn next_theme_name(current: &str) -> String {
    let themes = available_themes();
    if themes.is_empty() {
        return "mocha".to_string();
    }

    if let Some(idx) = themes.iter().position(|&t| t == current) {
        themes[(idx + 1) % themes.len()].to_string()
    } else {
        themes[0].to_string()
    }
}
