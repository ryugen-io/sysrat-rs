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
    let mode_text = StatusLineTheme::mode_text(state.vim_mode);
    let mode_style = StatusLineTheme::mode_style(state.vim_mode);

    let mut spans = vec![Span::styled(format!(" {} ", mode_text), mode_style)];

    // Only show file info when not in Menu
    if state.focus != Pane::Menu {
        spans.push(Span::raw(" | "));
        if let Some(filename) = &state.editor.current_file {
            spans.push(Span::styled(filename, StatusLineTheme::filename_style()));
            if state.dirty {
                spans.push(Span::styled(
                    " [modified]",
                    StatusLineTheme::modified_style(),
                ));
            }
        } else {
            spans.push(Span::styled("No file", StatusLineTheme::no_file_style()));
        }
    }

    // Only show status message when not in Menu
    if state.focus != Pane::Menu
        && let Some(ref msg) = state.status_message
    {
        spans.push(Span::raw(" | "));
        let style = if msg.starts_with("[ERROR") {
            StatusLineTheme::error_message_style()
        } else {
            StatusLineTheme::status_message_style()
        };
        spans.push(Span::styled(msg, style));
    }

    let help_text = match (state.focus, state.vim_mode) {
        (Pane::Menu, _) => format!(" | {}", state.keybinds.menu.help_text()),
        (Pane::FileList, _) => {
            format!(
                " | {}",
                state.keybinds.file_list.help_text(&state.keybinds.global)
            )
        }
        (Pane::Editor, VimMode::Normal) => {
            format!(" | {}", state.keybinds.global.editor_normal_help_text())
        }
        (Pane::Editor, VimMode::Insert) => {
            format!(" | {}", state.keybinds.global.editor_insert_help_text())
        }
        (Pane::ContainerList, _) => format!(" | {}", state.keybinds.container_list.help_text()),
    };
    spans.push(Span::styled(help_text, StatusLineTheme::help_text_style()));

    let status_line = Paragraph::new(Line::from(spans))
        .style(StatusLineTheme::background())
        .alignment(Alignment::Left);

    f.render_widget(status_line, area);
}
