use crate::{state::AppState, theme::menu::MenuTheme};
use ratzilla::ratatui::{
    Frame,
    layout::{Alignment, Rect},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
};

/// Renders the keybinds help panel in the right column
pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let keybinds = &state.keybinds;

    let lines = vec![
        Line::from(Span::styled("", MenuTheme::ascii_art_style(theme))),
        Line::from(Span::styled("KEYBINDS", MenuTheme::title_style(theme))),
        Line::from(Span::styled("", MenuTheme::ascii_art_style(theme))),
        Line::from(Span::styled("NAVIGATION", MenuTheme::title_style(theme))),
        Line::from(Span::styled(
            format!(
                "{}/{} - Navigate",
                keybinds.menu.navigate_up, keybinds.menu.navigate_down
            ),
            MenuTheme::normal_item_style(theme),
        )),
        Line::from(Span::styled(
            format!(
                "{}/{} - Navigate",
                keybinds.menu.navigate_up_alt, keybinds.menu.navigate_down_alt
            ),
            MenuTheme::normal_item_style(theme),
        )),
        Line::from(Span::styled("", MenuTheme::ascii_art_style(theme))),
        Line::from(Span::styled("SELECTION", MenuTheme::title_style(theme))),
        Line::from(Span::styled(
            format!("{} - Select", keybinds.menu.select),
            MenuTheme::normal_item_style(theme),
        )),
        Line::from(Span::styled("", MenuTheme::ascii_art_style(theme))),
        Line::from(Span::styled("GLOBAL", MenuTheme::title_style(theme))),
        Line::from(Span::styled(
            format!("{} - Cycle Theme", keybinds.global.cycle_theme),
            MenuTheme::normal_item_style(theme),
        )),
    ];

    let keybinds_widget = Paragraph::new(lines).alignment(Alignment::Left).block(
        Block::default()
            .borders(Borders::ALL)
            .border_style(MenuTheme::border_style(theme)),
    );

    f.render_widget(keybinds_widget, area);
}
