use super::{NORMAL_PREFIX, SELECTED_PREFIX, ThemeConfig};
use ratzilla::ratatui::style::Style;

/// Theme styles for the main menu widget
pub struct MenuTheme;

impl MenuTheme {
    pub fn title_style(theme: &ThemeConfig) -> Style {
        theme.standard_title()
    }

    pub fn ascii_art_style(theme: &ThemeConfig) -> Style {
        theme.standard_ascii_art()
    }

    pub fn border_style(theme: &ThemeConfig) -> Style {
        theme.standard_border_focused()
    }

    pub fn selected_item_style(theme: &ThemeConfig) -> Style {
        theme.standard_selected_item()
    }

    pub fn normal_item_style(theme: &ThemeConfig) -> Style {
        theme.standard_normal_item()
    }

    pub fn selected_prefix() -> &'static str {
        SELECTED_PREFIX
    }

    pub fn normal_prefix() -> &'static str {
        NORMAL_PREFIX
    }
}
