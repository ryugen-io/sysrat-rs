use super::ThemeConfig;
use ratzilla::ratatui::style::{Color, Modifier, Style};

/// Theme styles for the container list widget
pub struct ContainerListTheme;

impl ContainerListTheme {
    pub fn id_style(theme: &ThemeConfig) -> Style {
        theme.standard_value()
    }

    pub fn name_style(theme: &ThemeConfig) -> Style {
        theme.standard_normal_item()
    }

    pub fn status_info_style(theme: &ThemeConfig) -> Style {
        theme.standard_label()
    }

    pub fn status_color(theme: &ThemeConfig, state: &str) -> Color {
        match state {
            "running" => theme.success(),
            "exited" => theme.overlay1(),
            _ => theme.selected(),
        }
    }

    pub fn border_focused(theme: &ThemeConfig) -> Style {
        theme.standard_border_focused()
    }

    pub fn border_unfocused(theme: &ThemeConfig) -> Style {
        theme.standard_border_unfocused()
    }

    pub fn highlight_style(theme: &ThemeConfig) -> Style {
        theme
            .standard_highlight_bg()
            .fg(theme.text())
            .add_modifier(Modifier::BOLD)
    }
}
