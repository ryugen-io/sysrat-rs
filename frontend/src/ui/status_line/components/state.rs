use crate::{
    state::{AppState, Pane, VimMode},
    theme::{ThemeConfig, status_line::StatusLineTheme},
};
use ratzilla::ratatui::text::Span;

pub fn render_vim_mode(state: &AppState, theme: &ThemeConfig) -> Option<Span<'static>> {
    // Only show vim mode in FileList/Editor panes
    if !matches!(state.focus, Pane::FileList | Pane::Editor) {
        return None;
    }

    let mode_text = StatusLineTheme::mode_text(state.vim_mode);
    let mode_style = StatusLineTheme::mode_style(theme, state.vim_mode);
    Some(Span::styled(format!(" {} ", mode_text), mode_style))
}

pub fn render_filename(state: &AppState, theme: &ThemeConfig) -> Option<Span<'static>> {
    if let Some(filename) = &state.editor.current_file {
        Some(Span::styled(
            filename.clone(),
            StatusLineTheme::filename_style(theme),
        ))
    } else {
        Some(Span::styled(
            "No file",
            StatusLineTheme::no_file_style(theme),
        ))
    }
}

pub fn render_modified_indicator(state: &AppState, theme: &ThemeConfig) -> Option<Span<'static>> {
    if state.dirty {
        Some(Span::styled(
            " [modified]",
            StatusLineTheme::modified_style(theme),
        ))
    } else {
        Some(Span::styled(" [OK]", StatusLineTheme::ok_style(theme)))
    }
}

pub fn render_status_message(state: &AppState, theme: &ThemeConfig) -> Option<Span<'static>> {
    if let Some(ref msg) = state.status_message {
        let style = if msg.starts_with(" [ERROR") {
            StatusLineTheme::error_message_style(theme)
        } else {
            StatusLineTheme::status_message_style(theme)
        };
        Some(Span::styled(msg.clone(), style))
    } else {
        None
    }
}

pub fn render_help_text(state: &AppState, theme: &ThemeConfig) -> Option<Span<'static>> {
    // No help text in Menu pane
    let help_text = match (state.focus, state.vim_mode) {
        (Pane::Menu, _) => String::new(),
        (Pane::FileList, _) => state.keybinds.file_list.help_text(&state.keybinds.global),
        (Pane::Editor, VimMode::Normal) => state.keybinds.global.editor_normal_help_text(),
        (Pane::Editor, VimMode::Insert) => state.keybinds.global.editor_insert_help_text(),
        (Pane::ContainerList, _) => state
            .keybinds
            .container_list
            .help_text(&state.keybinds.global),
    };

    if !help_text.is_empty() {
        Some(Span::styled(
            help_text,
            StatusLineTheme::help_text_style(theme),
        ))
    } else {
        None
    }
}
