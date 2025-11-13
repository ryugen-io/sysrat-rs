use super::Theme;
use crate::state::VimMode;
use ratzilla::ratatui::style::{Modifier, Style};

pub struct StatusLineTheme;

impl StatusLineTheme {
    pub fn background() -> Style {
        Style::default().bg(Theme::MANTLE)
    }

    pub fn mode_text(vim_mode: VimMode) -> &'static str {
        match vim_mode {
            VimMode::Normal => "NORMAL",
            VimMode::Insert => "INSERT",
        }
    }

    pub fn mode_style(vim_mode: VimMode) -> Style {
        let color = match vim_mode {
            VimMode::Normal => Theme::NORMAL_MODE,
            VimMode::Insert => Theme::INSERT_MODE,
        };
        Style::default().fg(color).add_modifier(Modifier::BOLD)
    }

    pub fn filename_style() -> Style {
        Style::default().fg(Theme::TEXT)
    }

    pub fn modified_style() -> Style {
        Style::default().fg(Theme::MODIFIED)
    }

    pub fn no_file_style() -> Style {
        Style::default().fg(Theme::SUBTEXT0)
    }

    pub fn status_message_style() -> Style {
        Style::default().fg(Theme::SUCCESS)
    }

    pub fn error_message_style() -> Style {
        Style::default().fg(Theme::ERROR)
    }

    pub fn help_text_style() -> Style {
        Style::default().fg(Theme::DIM)
    }

    pub fn label_style() -> Style {
        Style::default().fg(Theme::DIM)
    }

    pub fn value_style() -> Style {
        Style::default().fg(Theme::YELLOW)
    }
}
