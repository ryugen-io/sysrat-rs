use serde::Deserialize;

/// Base RGB color definitions
#[derive(Debug, Clone, Deserialize)]
pub struct BaseColors {
    pub lavender: [u8; 3],
    pub mauve: [u8; 3],
    pub sapphire: [u8; 3],
    pub green: [u8; 3],
    pub yellow: [u8; 3],
    pub peach: [u8; 3],
    pub red: [u8; 3],
    pub text: [u8; 3],
    pub subtext0: [u8; 3],
    pub overlay1: [u8; 3],
    pub surface1: [u8; 3],
    pub mantle: [u8; 3],
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
