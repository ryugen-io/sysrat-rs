use crate::{
    state::{AppState, Pane},
    theme::file_list::FileListTheme,
};
use ratzilla::ratatui::{
    Frame,
    layout::Rect,
    text::{Line, Span},
    widgets::{Block, Borders, List, ListItem, ListState},
};

pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    let theme = &state.current_theme;
    let is_focused = state.focus == Pane::FileList;

    let border_style = if is_focused {
        FileListTheme::border_focused(theme)
    } else {
        FileListTheme::border_unfocused(theme)
    };

    let items: Vec<ListItem> = state
        .file_list
        .files
        .iter()
        .map(|file| {
            ListItem::new(Line::from(vec![Span::styled(
                &file.name,
                FileListTheme::normal_item_style(theme),
            )]))
        })
        .collect();

    let list = List::new(items)
        .block(
            Block::default()
                .title("Config Files")
                .borders(Borders::ALL)
                .border_style(border_style),
        )
        .highlight_style(FileListTheme::selected_item_style(theme))
        .highlight_symbol(FileListTheme::selected_prefix());

    let mut list_state = ListState::default();
    list_state.select(Some(state.file_list.selected_index));

    f.render_stateful_widget(list, area, &mut list_state);
}
