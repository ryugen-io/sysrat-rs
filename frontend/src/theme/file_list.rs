use super::Theme;
use ratzilla::ratatui::style::{Modifier, Style};

pub struct FileListTheme;

impl FileListTheme {
    pub fn border_focused() -> Style {
        Style::default().fg(Theme::ACCENT)
    }

    pub fn border_unfocused() -> Style {
        Style::default().fg(Theme::OVERLAY1)
    }

    pub fn selected_item_style() -> Style {
        Style::default()
            .fg(Theme::SELECTED)
            .add_modifier(Modifier::BOLD)
    }

    pub fn normal_item_style() -> Style {
        Style::default().fg(Theme::TEXT)
    }

    pub fn selected_prefix() -> &'static str {
        "> "
    }
}
