use crate::{api::ContainerDetails, theme::ThemeConfig};
use ratzilla::ratatui::{
    style::Style,
    text::{Line, Span},
};

pub(super) fn add_storage_info(
    lines: &mut Vec<Line<'static>>,
    details: &ContainerDetails,
    theme: &ThemeConfig,
) {
    if !details.volumes.is_empty() {
        lines.push(Line::from(Span::styled(
            "Volumes:",
            Style::default().fg(theme.selected()),
        )));
        for vol in &details.volumes {
            lines.push(Line::from(vec![
                Span::raw("  "),
                Span::styled(vol.source.clone(), Style::default().fg(theme.text())),
                Span::raw(" → "),
                Span::styled(vol.destination.clone(), Style::default().fg(theme.text())),
                Span::styled(format!(" ({})", vol.mode), Style::default().fg(theme.dim())),
            ]));
        }
        lines.push(Line::from(""));
    }
}
