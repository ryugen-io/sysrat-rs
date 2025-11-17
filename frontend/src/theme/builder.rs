use super::types::ThemeConfig;
use ratzilla::ratatui::style::{Modifier, Style};

/// Standard style builders that accept a runtime theme
///
/// These provide reusable style patterns for component themes.
/// This ensures consistency across the application.
impl ThemeConfig {
    /// Standard style for focused borders
    pub fn standard_border_focused(&self) -> Style {
        Style::default().fg(self.accent())
    }

    /// Standard style for unfocused borders
    pub fn standard_border_unfocused(&self) -> Style {
        Style::default().fg(self.overlay1())
    }

    /// Standard style for selected/highlighted items
    pub fn standard_selected_item(&self) -> Style {
        Style::default()
            .fg(self.selected())
            .add_modifier(Modifier::BOLD)
    }

    /// Standard style for normal items
    pub fn standard_normal_item(&self) -> Style {
        Style::default().fg(self.text())
    }

    /// Standard style for titles
    pub fn standard_title(&self) -> Style {
        Style::default()
            .fg(self.accent())
            .add_modifier(Modifier::BOLD)
    }

    /// Standard style for labels (dimmed text)
    pub fn standard_label(&self) -> Style {
        Style::default().fg(self.dim())
    }

    /// Standard style for values
    pub fn standard_value(&self) -> Style {
        Style::default().fg(self.selected())
    }

    /// Standard background style
    pub fn standard_background(&self) -> Style {
        Style::default().bg(self.mantle())
    }

    /// Standard highlight background
    pub fn standard_highlight_bg(&self) -> Style {
        Style::default().bg(self.surface1())
    }

    /// Standard style for ASCII art (uses background color as foreground AND background)
    /// This makes Braille pattern characters completely invisible
    pub fn standard_ascii_art(&self) -> Style {
        Style::default().fg(self.mantle()).bg(self.mantle())
    }
}
