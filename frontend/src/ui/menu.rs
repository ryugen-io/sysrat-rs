use crate::{state::AppState, theme::menu::MenuTheme};
use ratzilla::ratatui::{
    Frame,
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
};

pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    // Center the menu vertically
    let vertical_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Percentage(10),
            Constraint::Length(32),
            Constraint::Percentage(10),
        ])
        .split(area);

    // Split horizontally into 3 columns: Rat | Menu | Keybinds
    let horizontal_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(30), // Rat ASCII
            Constraint::Percentage(40), // Menu center
            Constraint::Percentage(30), // Keybinds
        ])
        .split(vertical_chunks[1]);

    // Render each column
    render_rat_ascii(f, state, horizontal_chunks[0]);
    render_menu_center(f, state, horizontal_chunks[1]);
    render_keybinds(f, state, horizontal_chunks[2]);
}

fn render_rat_ascii(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let sysrat_ascii = include_str!("../../assets/sysrat.ascii");

    let lines: Vec<Line> = sysrat_ascii
        .lines()
        .map(|line| Line::from(Span::styled(line, MenuTheme::ascii_art_style(theme))))
        .collect();

    let sysrat_widget = Paragraph::new(lines).alignment(Alignment::Center).block(
        Block::default()
            .borders(Borders::ALL)
            .border_style(MenuTheme::border_style(theme)),
    );

    f.render_widget(sysrat_widget, area);
}

fn render_menu_center(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let menu_text_ascii = include_str!("../../assets/menu-text.ascii");

    let mut lines = vec![];

    // Add menu text ASCII logo
    for line in menu_text_ascii.lines() {
        lines.push(Line::from(Span::styled(
            line,
            MenuTheme::title_style(theme),
        )));
    }

    // Add spacing
    lines.push(Line::from(""));

    // Add menu items with icons
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

        // Add icon based on item
        let icon = match item.as_str() {
            "Config Files" => "\u{f07c} ", // Nerd Font folder icon (U+F07C)
            "Container" => "\u{f308} ",    // Nerd Font docker icon (U+F308)
            _ => "",
        };

        lines.push(Line::from(Span::styled(
            format!("{}{}{}", prefix, icon, item),
            style,
        )));
    }

    let menu = Paragraph::new(lines).alignment(Alignment::Center).block(
        Block::default()
            .borders(Borders::ALL)
            .border_style(MenuTheme::border_style(theme)),
    );

    f.render_widget(menu, area);
}

fn render_keybinds(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let keybinds = &state.keybinds;

    let lines = vec![
        Line::from(""),
        Line::from(Span::styled("KEYBINDS", MenuTheme::title_style(theme))),
        Line::from(""),
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
        Line::from(""),
        Line::from(Span::styled("SELECTION", MenuTheme::title_style(theme))),
        Line::from(Span::styled(
            format!("{} - Select", keybinds.menu.select),
            MenuTheme::normal_item_style(theme),
        )),
        Line::from(""),
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
