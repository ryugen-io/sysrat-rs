use crate::{
    state::{AppState, Pane},
    theme::editor::EditorTheme,
};
use ratzilla::ratatui::{
    Frame,
    layout::Rect,
    widgets::{Block, Borders},
};

pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let is_focused = state.focus == Pane::Editor;
    let border_style = EditorTheme::border_style(theme, state.vim_mode, is_focused);

    let title = if let Some(filename) = &state.editor.current_file {
        let dirty_marker = if state.dirty { " [+]" } else { "" };
        format!("{}{}", filename, dirty_marker)
    } else {
        "No file loaded".to_string()
    };

    let textarea_widget = &state.editor.textarea;
    let mut widget_with_block = textarea_widget.clone();
    widget_with_block.set_block(
        Block::default()
            .title(title)
            .borders(Borders::ALL)
            .border_style(border_style),
    );

    f.render_widget(&widget_with_block, area);
}
