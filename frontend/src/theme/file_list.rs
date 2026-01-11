use super::{SELECTED_PREFIX, ThemeConfig};
use ratzilla::ratatui::style::Style;

/// Theme styles for the file list widget
pub struct FileListTheme;

impl FileListTheme {
    pub fn border_focused(theme: &ThemeConfig) -> Style {
        theme.standard_border_focused()
    }

    pub fn border_unfocused(theme: &ThemeConfig) -> Style {
        theme.standard_border_unfocused()
    }

    pub fn selected_item_style(theme: &ThemeConfig) -> Style {
        theme.standard_selected_item()
    }

    pub fn normal_item_style(theme: &ThemeConfig) -> Style {
        theme.standard_normal_item()
    }

    pub fn header_style(theme: &ThemeConfig) -> Style {
        theme.standard_title()
    }

    pub fn selected_prefix() -> &'static str {
        SELECTED_PREFIX
    }
}
