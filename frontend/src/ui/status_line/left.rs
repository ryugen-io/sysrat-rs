use crate::{
    state::{AppState, Pane, VimMode},
    theme::status_line::StatusLineTheme,
};
use ratzilla::ratatui::{
    Frame,
    layout::{Alignment, Rect},
    text::{Line, Span},
    widgets::Paragraph,
};

pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;

    let mut spans = vec![];

    // Only show vim mode in Editor and FileList (where NORMAL/INSERT is relevant)
    if matches!(state.focus, Pane::Editor | Pane::FileList) {
        let mode_text = StatusLineTheme::mode_text(state.vim_mode);
        let mode_style = StatusLineTheme::mode_style(theme, state.vim_mode);
        spans.push(Span::styled(format!(" {} ", mode_text), mode_style));
    }

    // Only show file info in Editor and FileList
    if matches!(state.focus, Pane::Editor | Pane::FileList) {
        if !spans.is_empty() {
            spans.push(Span::raw(" | "));
        }
        if let Some(filename) = &state.editor.current_file {
            spans.push(Span::styled(
                filename,
                StatusLineTheme::filename_style(theme),
            ));
            if state.dirty {
                spans.push(Span::styled(
                    " [modified]",
                    StatusLineTheme::modified_style(theme),
                ));
            }
        } else {
            spans.push(Span::styled(
                "No file",
                StatusLineTheme::no_file_style(theme),
            ));
        }
    }

    // Only show status message when not in Menu
    if state.focus != Pane::Menu
        && let Some(ref msg) = state.status_message
    {
        if !spans.is_empty() {
            spans.push(Span::raw(" | "));
        }
        let style = if msg.starts_with("[ERROR") {
            StatusLineTheme::error_message_style(theme)
        } else {
            StatusLineTheme::status_message_style(theme)
        };
        spans.push(Span::styled(msg, style));
    }

    // Help text - add separator only if spans is not empty
    let help_text = match (state.focus, state.vim_mode) {
        (Pane::Menu, _) => state.keybinds.menu.help_text(&state.keybinds.global),
        (Pane::FileList, _) => state.keybinds.file_list.help_text(&state.keybinds.global),
        (Pane::Editor, VimMode::Normal) => state.keybinds.global.editor_normal_help_text(),
        (Pane::Editor, VimMode::Insert) => state.keybinds.global.editor_insert_help_text(),
        (Pane::ContainerList, _) => state
            .keybinds
            .container_list
            .help_text(&state.keybinds.global),
    };

    if !spans.is_empty() {
        spans.push(Span::raw(" | "));
    }
    spans.push(Span::styled(
        help_text,
        StatusLineTheme::help_text_style(theme),
    ));

    let status_line = Paragraph::new(Line::from(spans))
        .style(StatusLineTheme::background(theme))
        .alignment(Alignment::Left);

    f.render_widget(status_line, area);
}
