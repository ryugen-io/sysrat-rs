use crate::{state::AppState, theme::menu::MenuTheme};
use ratzilla::ratatui::{
    Frame,
    layout::{Alignment, Rect},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
};

/// Renders the ASCII art rat logo in the left column
pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let sysrat_ascii = include_str!("../../../assets/sysrat.ascii");

    let lines: Vec<Line> = sysrat_ascii
        .lines()
        .map(|line| Line::from(Span::styled(line, MenuTheme::normal_item_style(theme))))
        .collect();

    let sysrat_widget = Paragraph::new(lines).alignment(Alignment::Center).block(
        Block::default()
            .borders(Borders::ALL)
            .border_style(MenuTheme::border_style(theme)),
    );

    f.render_widget(sysrat_widget, area);
}
