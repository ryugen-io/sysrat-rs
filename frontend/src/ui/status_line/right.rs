use crate::{state::AppState, theme::status_line::StatusLineTheme};
use ratzilla::ratatui::{
    Frame,
    layout::{Alignment, Rect},
    text::{Line, Span},
    widgets::Paragraph,
};

pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let build_date = env!("BUILD_DATE");
    let build_hash = env!("BUILD_HASH");
    let rust_edition = env!("RUST_EDITION");
    let rust_version = env!("RUST_VERSION");
    let ratzilla_version = env!("RATZILLA_VERSION");
    let ratatui_version = env!("RATATUI_VERSION");
    let axum_version = env!("AXUM_VERSION");

    let spans = vec![
        Span::styled(" last build: ", StatusLineTheme::label_style(theme)),
        Span::styled(build_date, StatusLineTheme::value_style(theme)),
        Span::styled(" (", StatusLineTheme::label_style(theme)),
        Span::styled(build_hash, StatusLineTheme::value_style(theme)),
        Span::styled(")", StatusLineTheme::label_style(theme)),
        Span::styled(" | Rust ", StatusLineTheme::label_style(theme)),
        Span::styled(rust_version, StatusLineTheme::value_style(theme)),
        Span::styled(" (Edition ", StatusLineTheme::label_style(theme)),
        Span::styled(rust_edition, StatusLineTheme::value_style(theme)),
        Span::styled(")", StatusLineTheme::label_style(theme)),
        Span::styled(" | Ratzilla v", StatusLineTheme::label_style(theme)),
        Span::styled(ratzilla_version, StatusLineTheme::value_style(theme)),
        Span::styled(" | Ratatui v", StatusLineTheme::label_style(theme)),
        Span::styled(ratatui_version, StatusLineTheme::value_style(theme)),
        Span::styled(" | Axum v", StatusLineTheme::label_style(theme)),
        Span::styled(axum_version, StatusLineTheme::value_style(theme)),
    ];

    let tech_line = Paragraph::new(Line::from(spans))
        .style(StatusLineTheme::background(theme))
        .alignment(Alignment::Left);

    f.render_widget(tech_line, area);
}
