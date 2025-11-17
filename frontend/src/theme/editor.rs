use super::ThemeConfig;
use crate::state::VimMode;
use ratzilla::ratatui::style::Style;

/// Theme styles for the text editor widget
pub struct EditorTheme;

impl EditorTheme {
    pub fn border_style(theme: &ThemeConfig, vim_mode: VimMode, is_focused: bool) -> Style {
        if is_focused {
            match vim_mode {
                VimMode::Normal => Style::default().fg(theme.normal_mode()),
                VimMode::Insert => Style::default().fg(theme.insert_mode()),
            }
        } else {
            theme.standard_border_unfocused()
        }
    }
}
