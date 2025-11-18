use ratzilla::ratatui::style::Color;
use serde::Deserialize;

use super::{
    colors::{BaseColors, SemanticMappings},
    font::{FontConfig, default_font_config},
    icons::{IconConfig, default_icon_config},
};

/// Runtime theme configuration
///
/// Represents a theme loaded at runtime from TOML.
/// Unlike the build-time `Theme` constants, this struct
/// holds dynamically loaded color values.
#[derive(Debug, Clone, Deserialize)]
pub struct ThemeConfig {
    #[serde(rename = "colors")]
    pub base: BaseColors,
    pub semantic: SemanticMappings,
    #[serde(default = "default_font_config")]
    pub font: FontConfig,
    #[serde(default = "default_icon_config")]
    pub icons: IconConfig,
}

impl ThemeConfig {
    /// Get base color by name
    fn get_base_color(&self, name: &str) -> Color {
        let rgb = match name {
            "lavender" => self.base.lavender,
            "mauve" => self.base.mauve,
            "sapphire" => self.base.sapphire,
            "green" => self.base.green,
            "yellow" => self.base.yellow,
            "peach" => self.base.peach,
            "red" => self.base.red,
            "text" => self.base.text,
            "subtext0" => self.base.subtext0,
            "overlay1" => self.base.overlay1,
            "surface1" => self.base.surface1,
            "mantle" => self.base.mantle,
            _ => self.base.text, // Fallback
        };
        Color::Rgb(rgb[0], rgb[1], rgb[2])
    }

    // Semantic color accessors
    pub fn accent(&self) -> Color {
        self.get_base_color(&self.semantic.accent)
    }
    pub fn selected(&self) -> Color {
        self.get_base_color(&self.semantic.selected)
    }
    pub fn modified(&self) -> Color {
        self.get_base_color(&self.semantic.modified)
    }
    pub fn success(&self) -> Color {
        self.get_base_color(&self.semantic.success)
    }
    pub fn error(&self) -> Color {
        self.get_base_color(&self.semantic.error)
    }
    pub fn normal_mode(&self) -> Color {
        self.get_base_color(&self.semantic.normal_mode)
    }
    pub fn insert_mode(&self) -> Color {
        self.get_base_color(&self.semantic.insert_mode)
    }
    pub fn dim(&self) -> Color {
        self.get_base_color(&self.semantic.dim)
    }
    pub fn text(&self) -> Color {
        Color::Rgb(self.base.text[0], self.base.text[1], self.base.text[2])
    }
    pub fn overlay1(&self) -> Color {
        Color::Rgb(
            self.base.overlay1[0],
            self.base.overlay1[1],
            self.base.overlay1[2],
        )
    }
    pub fn mantle(&self) -> Color {
        Color::Rgb(
            self.base.mantle[0],
            self.base.mantle[1],
            self.base.mantle[2],
        )
    }
    pub fn surface1(&self) -> Color {
        Color::Rgb(
            self.base.surface1[0],
            self.base.surface1[1],
            self.base.surface1[2],
        )
    }
}
