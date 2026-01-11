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

    let mut items: Vec<ListItem> = Vec::new();
    let mut display_selected_index: Option<usize> = None;
    let mut last_category: Option<String> = None;

    for (file_idx, file) in state.file_list.files.iter().enumerate() {
        let category = file
            .category
            .as_deref()
            .unwrap_or("Uncategorized")
            .to_string();

        // Insert category header when it changes
        if last_category.as_deref() != Some(category.as_str()) {
            items.push(ListItem::new(Line::from(vec![Span::styled(
                category.clone(),
                FileListTheme::header_style(theme),
            )])));
            last_category = Some(category);
        }

        // Track where the selected file sits in the rendered list
        if file_idx == state.file_list.selected_index {
            display_selected_index = Some(items.len());
        }

        items.push(ListItem::new(Line::from(vec![Span::styled(
            format!("  - {}", file.name),
            FileListTheme::normal_item_style(theme),
        )])));
    }

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
    list_state.select(display_selected_index);

    f.render_stateful_widget(list, area, &mut list_state);
}
