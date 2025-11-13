use crate::theme::status_line::StatusLineTheme;
use ratzilla::ratatui::{
    Frame,
    layout::{Alignment, Rect},
    text::{Line, Span},
    widgets::Paragraph,
};

pub fn render(f: &mut Frame, area: Rect) {
    let build_date = env!("BUILD_DATE");
    let rust_edition = env!("RUST_EDITION");
    let rust_version = env!("RUST_VERSION");
    let ratzilla_version = env!("RATZILLA_VERSION");
    let ratatui_version = env!("RATATUI_VERSION");
    let axum_version = env!("AXUM_VERSION");

    let spans = vec![
        Span::styled(" last build: ", StatusLineTheme::label_style()),
        Span::styled(build_date, StatusLineTheme::value_style()),
        Span::styled(" | Rust ", StatusLineTheme::label_style()),
        Span::styled(rust_version, StatusLineTheme::value_style()),
        Span::styled(" (Edition ", StatusLineTheme::label_style()),
        Span::styled(format!("{})", rust_edition), StatusLineTheme::value_style()),
        Span::styled(" | Ratzilla v", StatusLineTheme::label_style()),
        Span::styled(ratzilla_version, StatusLineTheme::value_style()),
        Span::styled(" | Ratatui v", StatusLineTheme::label_style()),
        Span::styled(ratatui_version, StatusLineTheme::value_style()),
        Span::styled(" | Axum v", StatusLineTheme::label_style()),
        Span::styled(axum_version, StatusLineTheme::value_style()),
    ];

    let tech_line = Paragraph::new(Line::from(spans))
        .style(StatusLineTheme::background())
        .alignment(Alignment::Left);

    f.render_widget(tech_line, area);
}
