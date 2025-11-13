pub mod container_list;
pub mod editor;
pub mod file_list;
pub mod menu;
pub mod status_line;

use ratzilla::ratatui::style::Color;

// Theme colors loaded from theme.toml at build time
pub struct Theme;

// Helper macro to parse RGB from build-time environment variable
macro_rules! rgb_from_env {
    ($env:literal) => {{
        const RGB_STR: &str = env!($env);
        const fn parse_rgb(s: &str) -> (u8, u8, u8) {
            let bytes = s.as_bytes();
            let mut r = 0u8;
            let mut g = 0u8;
            let mut idx = 0;
            let mut current = 0;
            let mut part = 0;

            while idx < bytes.len() {
                if bytes[idx] >= b'0' && bytes[idx] <= b'9' {
                    current = current * 10 + (bytes[idx] - b'0') as u8;
                } else if bytes[idx] == b',' {
                    match part {
                        0 => r = current,
                        1 => g = current,
                        _ => {}
                    }
                    current = 0;
                    part += 1;
                }
                idx += 1;
            }
            let b = current;
            (r, g, b)
        }

        const RGB: (u8, u8, u8) = parse_rgb(RGB_STR);
        Color::Rgb(RGB.0, RGB.1, RGB.2)
    }};
}

impl Theme {
    // Base colors loaded from theme.toml
    pub const LAVENDER: Color = rgb_from_env!("THEME_COLOR_LAVENDER");
    pub const MAUVE: Color = rgb_from_env!("THEME_COLOR_MAUVE");
    pub const SAPPHIRE: Color = rgb_from_env!("THEME_COLOR_SAPPHIRE");
    pub const GREEN: Color = rgb_from_env!("THEME_COLOR_GREEN");
    pub const YELLOW: Color = rgb_from_env!("THEME_COLOR_YELLOW");
    pub const PEACH: Color = rgb_from_env!("THEME_COLOR_PEACH");
    pub const RED: Color = rgb_from_env!("THEME_COLOR_RED");
    pub const TEXT: Color = rgb_from_env!("THEME_COLOR_TEXT");
    pub const SUBTEXT0: Color = rgb_from_env!("THEME_COLOR_SUBTEXT0");
    pub const OVERLAY1: Color = rgb_from_env!("THEME_COLOR_OVERLAY1");
    pub const SURFACE1: Color = rgb_from_env!("THEME_COLOR_SURFACE1");
    pub const MANTLE: Color = rgb_from_env!("THEME_COLOR_MANTLE");

    // Semantic colors (mapped to base colors)
    pub const ACCENT: Color = Self::LAVENDER;
    pub const SELECTED: Color = Self::YELLOW;
    pub const MODIFIED: Color = Self::PEACH;
    pub const SUCCESS: Color = Self::GREEN;
    pub const ERROR: Color = Self::RED;
    pub const NORMAL_MODE: Color = Self::SAPPHIRE;
    pub const INSERT_MODE: Color = Self::MAUVE;
    pub const DIM: Color = Self::SUBTEXT0;
}
