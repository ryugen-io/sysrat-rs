mod container_details;
mod container_list;
mod editor;
mod file_list;
mod menu;
mod splash;
mod status_line;

use crate::state::{AppState, Pane};
use ratzilla::ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout},
    style::Style,
    widgets::{Block, Widget},
};

pub fn render(f: &mut Frame, state: &AppState) {
    // Set global background to MANTLE
    let background = Block::default().style(Style::default().bg(state.current_theme.mantle()));
    background.render(f.area(), f.buffer_mut());

    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Min(0),    // Main content
            Constraint::Length(4), // Status line (4 rows: spacing + status + spacing + build info)
        ])
        .split(f.area());

    // Main content depends on current pane
    match state.focus {
        Pane::Splash => splash::render(f, state, chunks[0]),
        Pane::Menu => menu::render(f, state, chunks[0]),
        Pane::ContainerList => render_container_view(f, state, chunks[0]),
        _ => render_main_content(f, state, chunks[0]),
    }

    // Status line
    status_line::render(f, state, chunks[1]);
}

fn render_main_content(f: &mut Frame, state: &AppState, area: ratzilla::ratatui::layout::Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(25), // File list
            Constraint::Percentage(1),  // Empty gap
            Constraint::Percentage(74), // Editor
        ])
        .split(area);

    file_list::render(f, state, chunks[0]);
    editor::render(f, state, chunks[2]);
}

fn render_container_view(f: &mut Frame, state: &AppState, area: ratzilla::ratatui::layout::Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(40), // Container list
            Constraint::Percentage(1),  // Empty gap
            Constraint::Percentage(59), // Container details
        ])
        .split(area);

    container_list::render(f, state, chunks[0]);
    container_details::render(f, state, chunks[2]);
}
