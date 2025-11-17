mod basic;
mod config;
mod network;
mod storage;

use crate::state::AppState;
use ratzilla::ratatui::{
    Frame,
    layout::Rect,
    style::Style,
    widgets::{Block, Borders, Paragraph, Wrap},
};

pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let block = Block::default()
        .borders(Borders::ALL)
        .title(" Container Details ")
        .border_style(Style::default().fg(theme.dim()));

    if let Some(details) = &state.container_details {
        let mut lines = Vec::new();
        basic::add_basic_info(&mut lines, details, theme);
        network::add_network_info(&mut lines, details, theme);
        storage::add_storage_info(&mut lines, details, theme);
        config::add_config_info(&mut lines, details, theme);

        let paragraph = Paragraph::new(lines).block(block).wrap(Wrap { trim: true });
        f.render_widget(paragraph, area);
    } else {
        let paragraph = Paragraph::new("No container selected")
            .block(block)
            .style(Style::default().fg(theme.dim()));
        f.render_widget(paragraph, area);
    }
}
