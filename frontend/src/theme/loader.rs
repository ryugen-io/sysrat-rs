use super::types::ThemeConfig;
use crate::storage;

/// Get list of available theme names
pub fn available_themes() -> Vec<&'static str> {
    generated::THEME_NAMES.to_vec()
}

/// Load theme by name from embedded themes
pub fn load_theme_by_name(name: &str) -> Result<ThemeConfig, String> {
    // DEBUG: Uncomment for theme loading diagnostics
    // web_sys::console::log_1(&wasm_bindgen::JsValue::from_str(&format!(
    //     "[DEBUG] Available themes: {:?}",
    //     generated::THEME_NAMES
    // )));
    // web_sys::console::log_1(&wasm_bindgen::JsValue::from_str(&format!(
    //     "[DEBUG] Trying to load theme: '{}'",
    //     name
    // )));

    // Load theme content from auto-generated code
    // This is generated at build time by frontend/build_helpers/theme/generator.rs
    let toml_content = generated::load_theme_content(name)?;

    // DEBUG: Uncomment for theme content diagnostics
    // web_sys::console::log_1(&wasm_bindgen::JsValue::from_str(&format!(
    //     "[DEBUG] Successfully loaded theme content for '{}'",
    //     name
    // )));

    // DEBUG: Uncomment for theme parsing diagnostics
    // let parsed = parse_theme_toml(toml_content);
    // match &parsed {
    //     Ok(_) => web_sys::console::log_1(&wasm_bindgen::JsValue::from_str(&format!(
    //         "[DEBUG] Successfully parsed theme '{}'",
    //         name
    //     ))),
    //     Err(e) => web_sys::console::error_1(&wasm_bindgen::JsValue::from_str(&format!(
    //         "[DEBUG] Failed to parse theme '{}': {}",
    //         name, e
    //     ))),
    // }
    // parsed

    parse_theme_toml(toml_content)
}

/// Auto-generated theme loader module
mod generated {
    include!(concat!(env!("OUT_DIR"), "/generated_theme_loader.rs"));
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
