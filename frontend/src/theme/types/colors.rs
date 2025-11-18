use serde::Deserialize;

/// Base RGB color definitions (all optional to support different theme palettes)
#[derive(Debug, Clone, Deserialize)]
pub struct BaseColors {
    // Catppuccin-style colors (optional)
    pub lavender: Option<[u8; 3]>,
    pub mauve: Option<[u8; 3]>,
    pub sapphire: Option<[u8; 3]>,
    pub green: Option<[u8; 3]>,
    pub yellow: Option<[u8; 3]>,
    pub peach: Option<[u8; 3]>,
    pub red: Option<[u8; 3]>,
    pub text: Option<[u8; 3]>,
    pub subtext0: Option<[u8; 3]>,
    pub overlay1: Option<[u8; 3]>,
    pub surface1: Option<[u8; 3]>,
    pub mantle: Option<[u8; 3]>,

    // Allow any additional colors from theme files
    #[serde(flatten)]
    pub extra: std::collections::HashMap<String, [u8; 3]>,
}

impl BaseColors {
    /// Get a color by name with fallback logic
    pub fn get(&self, name: &str) -> [u8; 3] {
        match name {
            "lavender" => self.lavender,
            "mauve" => self.mauve,
            "sapphire" => self.sapphire,
            "green" => self.green,
            "yellow" => self.yellow,
            "peach" => self.peach,
            "red" => self.red,
            "text" => self.text,
            "subtext0" => self.subtext0,
            "overlay1" => self.overlay1,
            "surface1" => self.surface1,
            "mantle" => self.mantle,
            _ => None,
        }
        .or_else(|| self.extra.get(name).copied())
        .unwrap_or([128, 128, 128]) // Default gray if color not found
    }
}

/// Semantic color mappings to base colors
#[derive(Debug, Clone, Deserialize)]
pub struct SemanticMappings {
    pub accent: String,
    pub selected: String,
    pub modified: String,
    pub success: String,
    pub error: String,
    pub normal_mode: String,
    pub insert_mode: String,
    pub dim: String,
}
