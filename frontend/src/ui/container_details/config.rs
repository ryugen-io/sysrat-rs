use crate::{api::ContainerDetails, theme::ThemeConfig};
use ratzilla::ratatui::{
    style::Style,
    text::{Line, Span},
};

pub(super) fn add_config_info(
    lines: &mut Vec<Line<'static>>,
    details: &ContainerDetails,
    theme: &ThemeConfig,
) {
    lines.push(Line::from(vec![
        Span::styled("Restart: ", Style::default().fg(theme.dim())),
        Span::styled(
            details.restart_policy.clone(),
            Style::default().fg(theme.text()),
        ),
    ]));
    lines.push(Line::from(""));

    lines.push(Line::from(vec![
        Span::styled("Status: ", Style::default().fg(theme.dim())),
        Span::styled(details.status.clone(), Style::default().fg(theme.text())),
    ]));
    lines.push(Line::from(vec![
        Span::styled("Created: ", Style::default().fg(theme.dim())),
        Span::styled(details.created.clone(), Style::default().fg(theme.text())),
    ]));
    lines.push(Line::from(vec![
        Span::styled("Started: ", Style::default().fg(theme.dim())),
        Span::styled(details.started.clone(), Style::default().fg(theme.text())),
    ]));

    if !details.environment.is_empty() {
        lines.push(Line::from(""));
        lines.push(Line::from(Span::styled(
            "Environment:",
            Style::default().fg(theme.selected()),
        )));
        for env in details.environment.iter().take(10) {
            if let Some((key, _)) = env.split_once('=') {
                lines.push(Line::from(format!("  {}", key)));
            }
        }
        if details.environment.len() > 10 {
            lines.push(Line::from(Span::styled(
                format!("  ... and {} more", details.environment.len() - 10),
                Style::default().fg(theme.dim()),
            )));
        }
    }
}
