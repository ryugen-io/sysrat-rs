use serde::Deserialize;

/// Icon configuration for menu items
#[derive(Debug, Clone, Deserialize)]
pub struct IconConfig {
    pub config_files: String,
    pub container: String,
}

/// Default icon configuration (Unicode symbols)
pub fn default_icon_config() -> IconConfig {
    IconConfig {
        config_files: "▪".to_string(), // Black small square (U+25AA)
        container: "▪".to_string(),    // Black small square (U+25AA)
    }
}
