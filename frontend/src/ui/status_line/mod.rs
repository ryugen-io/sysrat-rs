mod left;
mod right;

use crate::state::AppState;
use ratzilla::ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout, Rect},
};

pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    // Split status line into 2 rows
    // Row 1: Status info (mode, file, messages, help)
    // Row 2: Build info (versions, dates)
    let rows = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Length(1), Constraint::Length(1)])
        .split(area);

    // Row 1: Status info (full width)
    left::render(f, state, rows[0]);

    // Row 2: Build info (full width, right aligned)
    right::render(f, state, rows[1]);
}
