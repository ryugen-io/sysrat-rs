use crate::{api::ContainerDetails, theme::ThemeConfig};
use ratzilla::ratatui::{
    style::Style,
    text::{Line, Span},
};

pub(super) fn add_basic_info(
    lines: &mut Vec<Line<'static>>,
    details: &ContainerDetails,
    theme: &ThemeConfig,
) {
    lines.push(Line::from(vec![
        Span::styled("ID: ", Style::default().fg(theme.dim())),
        Span::styled(details.id.clone(), Style::default().fg(theme.text())),
    ]));
    lines.push(Line::from(vec![
        Span::styled("Name: ", Style::default().fg(theme.dim())),
        Span::styled(details.name.clone(), Style::default().fg(theme.text())),
    ]));
    lines.push(Line::from(vec![
        Span::styled("Image: ", Style::default().fg(theme.dim())),
        Span::styled(details.image.clone(), Style::default().fg(theme.accent())),
    ]));
    lines.push(Line::from(""));

    let state_color = match details.state.as_str() {
        "running" => theme.success(),
        _ => theme.modified(),
    };
    lines.push(Line::from(vec![
        Span::styled("State: ", Style::default().fg(theme.dim())),
        Span::styled(details.state.clone(), Style::default().fg(state_color)),
    ]));

    if let Some(health) = &details.health {
        lines.push(Line::from(vec![
            Span::styled("Health: ", Style::default().fg(theme.dim())),
            Span::styled(health.clone(), Style::default().fg(theme.success())),
        ]));
    }
    lines.push(Line::from(""));
}
