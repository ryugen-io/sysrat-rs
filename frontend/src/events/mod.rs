mod container_list;
mod editor;
mod file_list;
mod menu;

use crate::state::{AppState, Pane};
use ratzilla::event::{KeyCode, KeyEvent};
use std::{cell::RefCell, rc::Rc};

pub fn handle_key_event(state: Rc<RefCell<AppState>>, key_event: KeyEvent) {
    let mut state_mut = state.borrow_mut();

    // Global keybindings (work in any pane/mode)

    // F2: Save file
    if key_event.code == KeyCode::F(2) {
        if let Some(filename) = state_mut.editor.current_file.clone() {
            let content = state_mut.editor.get_content();
            drop(state_mut); // Release borrow before async

            menu::save_file(state, filename, content);
        }
        return;
    }

    // F3: Cycle theme
    if key_event.code == KeyCode::F(3) {
        let current_name =
            crate::theme::load_theme_preference().unwrap_or_else(|| "mocha".to_string());
        let next_name = crate::theme::next_theme_name(&current_name);
        state_mut.set_theme(next_name);
        return;
    }

    // Ctrl+Left: Focus file list
    if key_event.ctrl && key_event.code == KeyCode::Left {
        state_mut.focus = Pane::FileList;
        state_mut.save_to_storage();
        return;
    }

    // Ctrl+Right: Focus editor
    if key_event.ctrl && key_event.code == KeyCode::Right {
        state_mut.focus = Pane::Editor;
        state_mut.vim_mode = crate::state::VimMode::Normal;
        state_mut.save_to_storage();
        return;
    }

    match state_mut.focus {
        Pane::Menu => menu::handle_keys(&mut state_mut, &state, key_event),
        Pane::FileList => file_list::handle_keys(&mut state_mut, &state, key_event),
        Pane::Editor => editor::handle_keys(&mut state_mut, key_event),
        Pane::ContainerList => container_list::handle_keys(&mut state_mut, &state, key_event),
    }

    // Save state after any key event
    state_mut.save_to_storage();
}
