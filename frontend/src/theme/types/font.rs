use serde::Deserialize;

/// Font configuration for the theme
#[derive(Debug, Clone, Deserialize)]
pub struct FontConfig {
    pub family: String,
    pub fallback: String,
    pub size: u32,
    pub weight: u32,
    pub cdn_url: Option<String>,
}

/// Default font configuration (Fira Code)
pub fn default_font_config() -> FontConfig {
    FontConfig {
        family: "Fira Code".to_string(),
        fallback: "monospace".to_string(),
        size: 16,
        weight: 400,
        cdn_url: Some(
            "https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/fira_code.min.css".to_string(),
        ),
    }
}
