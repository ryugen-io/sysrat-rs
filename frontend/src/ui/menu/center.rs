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

    // Calculate max item length for padding (centered but aligned)
    let max_len = state
        .menu
        .items
        .iter()
        .map(|item| {
            let prefix = MenuTheme::selected_prefix(); // Use longest prefix
            let icon = match item.as_str() {
                "Config Files" => format!("{} ", theme.icons.config_files),
                "Container" => format!("{} ", theme.icons.container),
                _ => String::new(),
            };
            prefix.len() + icon.len() + item.len()
        })
        .max()
        .unwrap_or(0);

    // Add menu items with padding to align them
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

        // Icons from theme configuration
        let icon = match item.as_str() {
            "Config Files" => format!("{} ", theme.icons.config_files),
            "Container" => format!("{} ", theme.icons.container),
            _ => String::new(),
        };

        let line_text = format!("{}{}{}", prefix, icon, item);
        let padding = " ".repeat(max_len.saturating_sub(line_text.len()));
        let padded_line = format!("{}{}", line_text, padding);

        lines.push(Line::from(Span::styled(padded_line, style)));
    }

    let menu = Paragraph::new(lines).alignment(Alignment::Center).block(
        Block::default()
            .borders(Borders::ALL)
            .border_style(MenuTheme::border_style(theme)),
    );

    f.render_widget(menu, area);
}
