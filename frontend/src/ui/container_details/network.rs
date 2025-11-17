use crate::{api::ContainerDetails, theme::ThemeConfig};
use ratzilla::ratatui::{
    style::Style,
    text::{Line, Span},
};

pub(super) fn add_network_info(
    lines: &mut Vec<Line<'static>>,
    details: &ContainerDetails,
    theme: &ThemeConfig,
) {
    if !details.ports.is_empty() {
        lines.push(Line::from(Span::styled(
            "Ports:",
            Style::default().fg(theme.selected()),
        )));
        for port in &details.ports {
            lines.push(Line::from(vec![
                Span::raw("  "),
                Span::styled(port.host_port.clone(), Style::default().fg(theme.text())),
                Span::raw(" → "),
                Span::styled(
                    port.container_port.clone(),
                    Style::default().fg(theme.text()),
                ),
                Span::styled(
                    format!("/{}", port.protocol),
                    Style::default().fg(theme.dim()),
                ),
            ]));
        }
        lines.push(Line::from(""));
    }

    if !details.networks.is_empty() {
        lines.push(Line::from(Span::styled(
            "Networks:",
            Style::default().fg(theme.selected()),
        )));
        for net in &details.networks {
            lines.push(Line::from(format!("  {}", net)));
        }
        lines.push(Line::from(""));
    }
}
