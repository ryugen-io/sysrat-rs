use crate::api;
use crate::state::{AppState, Pane, refresh, status_helper};
use crate::utils;
use ratzilla::event::{KeyCode, KeyEvent};
use std::{cell::RefCell, rc::Rc};
use wasm_bindgen_futures::spawn_local;

pub fn handle_keys(state: &mut AppState, state_rc: &Rc<RefCell<AppState>>, key_event: KeyEvent) {
    match key_event.code {
        KeyCode::Esc => {
            state.focus = Pane::Menu;
            state.status_message = None;
        }
        KeyCode::Char('j') | KeyCode::Down => {
            state.file_list.next();
            refresh::save_selection(Pane::FileList, state);
        }
        KeyCode::Char('k') | KeyCode::Up => {
            state.file_list.previous();
            refresh::save_selection(Pane::FileList, state);
        }
        KeyCode::Enter => {
            if let Some(fileinfo) = state.file_list.selected().cloned() {
                let state_clone = Rc::clone(state_rc);
                spawn_local(async move {
                    match api::fetch_file_content(&fileinfo.name).await {
                        Ok(content) => {
                            let mut st = state_clone.borrow_mut();
                            st.editor.load_content(fileinfo.name.clone(), content);
                            st.dirty = false;
                            st.focus = Pane::Editor;
                            st.set_status("[OK]".to_string());
                        }
                        Err(e) => {
                            status_helper::set_status_timed(
                                &state_clone,
                                format!("[ERROR loading: {}]", utils::error::format_error(&e)),
                            );
                        }
                    }
                });
            }
        }
        _ => {}
    }
}
