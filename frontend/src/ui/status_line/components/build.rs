use crate::theme::{ThemeConfig, status_line::StatusLineTheme};
use ratzilla::ratatui::{style::Style, text::Span};

pub fn render_build_date(style: Option<&str>, theme: &ThemeConfig) -> Option<Span<'static>> {
    let text = env!("BUILD_DATE");
    let s = get_style(style, theme);
    Some(Span::styled(text, s))
}

pub fn render_build_hash(style: Option<&str>, theme: &ThemeConfig) -> Option<Span<'static>> {
    let text = env!("BUILD_HASH");
    let s = get_style(style, theme);
    Some(Span::styled(text, s))
}

pub fn render_rust_version(style: Option<&str>, theme: &ThemeConfig) -> Option<Span<'static>> {
    let text = env!("RUST_VERSION");
    let s = get_style(style, theme);
    Some(Span::styled(text, s))
}

pub fn render_rust_edition(style: Option<&str>, theme: &ThemeConfig) -> Option<Span<'static>> {
    let text = env!("RUST_EDITION");
    let s = get_style(style, theme);
    Some(Span::styled(text, s))
}

pub fn render_dependency(
    name: &str,
    style: Option<&str>,
    theme: &ThemeConfig,
) -> Option<Span<'static>> {
    let version = match name.to_lowercase().as_str() {
        "ratzilla" => env!("RATZILLA_VERSION"),
        "ratatui" => env!("RATATUI_VERSION"),
        "axum" => env!("AXUM_VERSION"),
        "tachyonfx" => env!("TACHYONFX_VERSION"),
        _ => "unknown",
    };
    let s = get_style(style, theme);
    Some(Span::styled(version, s))
}

fn get_style(style_name: Option<&str>, theme: &ThemeConfig) -> Style {
    match style_name {
        Some("label") => StatusLineTheme::label_style(theme),
        Some("value") => StatusLineTheme::value_style(theme),
        Some("error") => StatusLineTheme::error_message_style(theme),
        _ => StatusLineTheme::background(theme),
    }
}
