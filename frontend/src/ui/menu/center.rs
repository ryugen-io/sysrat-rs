use crate::{state::AppState, theme::menu::MenuTheme};
use ratzilla::ratatui::{
    Frame,
    layout::{Alignment, Rect},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
};

/// Renders the center menu column with logo and menu items
pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let menu_text_ascii = include_str!("../../../assets/menu-text.ascii");

    let mut lines = vec![];

    // Add menu text ASCII logo
    for line in menu_text_ascii.lines() {
        lines.push(Line::from(Span::styled(
            line,
            MenuTheme::title_style(theme),
        )));
    }

    // Add spacing (styled to hide Braille characters)
    lines.push(Line::from(Span::styled(
        "",
        MenuTheme::ascii_art_style(theme),
    )));

    // Add menu items with Nerd Font icons
    for (i, item) in state.menu.items.iter().enumerate() {
        let is_selected = i == state.menu.selected_index;

        let style = if is_selected {
            MenuTheme::selected_item_style(theme)
        } else {
            MenuTheme::normal_item_style(theme)
        };

        let prefix = if is_selected {
            MenuTheme::selected_prefix()
        } else {
            MenuTheme::normal_prefix()
        };

        // Test: Einfachere Nerd Font Icons oder Unicode-Symbole
        let icon = match item.as_str() {
            "Config Files" => "□ ", // Simple box drawing character
            "Container" => "◆ ",    // Diamond symbol
            _ => "",
        };

        let line_text = format!("{}{}{}", prefix, icon, item);
        lines.push(Line::from(Span::styled(line_text, style)));
    }

    let menu = Paragraph::new(lines).alignment(Alignment::Center).block(
        Block::default()
            .borders(Borders::ALL)
            .border_style(MenuTheme::border_style(theme)),
    );

    f.render_widget(menu, area);
}
