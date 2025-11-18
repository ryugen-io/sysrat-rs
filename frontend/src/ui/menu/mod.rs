mod center;
mod keybinds;
mod rat_ascii;

use crate::state::AppState;
use ratzilla::ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout, Rect},
};

/// Main menu render function that orchestrates the layout
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
            Constraint::Percentage(28), // Rat ASCII
            Constraint::Percentage(45), // Menu center
            Constraint::Percentage(27), // Keybinds
        ])
        .split(vertical_chunks[1]);

    // Render each column
    rat_ascii::render(f, state, horizontal_chunks[0]);
    center::render(f, state, horizontal_chunks[1]);
    keybinds::render(f, state, horizontal_chunks[2]);
}
