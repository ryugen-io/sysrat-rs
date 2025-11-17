use super::ThemeConfig;
use crate::state::VimMode;
use ratzilla::ratatui::style::{Modifier, Style};

/// Theme styles for the status line widget
pub struct StatusLineTheme;

impl StatusLineTheme {
    pub fn background(theme: &ThemeConfig) -> Style {
        theme.standard_background()
    }

    pub fn mode_text(vim_mode: VimMode) -> &'static str {
        match vim_mode {
            VimMode::Normal => "NORMAL",
            VimMode::Insert => "INSERT",
        }
    }

    pub fn mode_style(theme: &ThemeConfig, vim_mode: VimMode) -> Style {
        let color = match vim_mode {
            VimMode::Normal => theme.normal_mode(),
            VimMode::Insert => theme.insert_mode(),
        };
        Style::default().fg(color).add_modifier(Modifier::BOLD)
    }

    pub fn filename_style(theme: &ThemeConfig) -> Style {
        theme.standard_normal_item()
    }

    pub fn modified_style(theme: &ThemeConfig) -> Style {
        Style::default().fg(theme.modified())
    }

    pub fn no_file_style(theme: &ThemeConfig) -> Style {
        theme.standard_label()
    }

    pub fn status_message_style(theme: &ThemeConfig) -> Style {
        Style::default().fg(theme.success())
    }

    pub fn error_message_style(theme: &ThemeConfig) -> Style {
        Style::default().fg(theme.error())
    }

    pub fn help_text_style(theme: &ThemeConfig) -> Style {
        theme.standard_label()
    }

    pub fn label_style(theme: &ThemeConfig) -> Style {
        theme.standard_label()
    }

    pub fn value_style(theme: &ThemeConfig) -> Style {
        theme.standard_value()
    }
}
