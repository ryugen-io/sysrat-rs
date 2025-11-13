mod api;
mod events;
mod keybinds;
mod state;
mod storage;
mod theme;
mod ui;
mod utils;

use ratzilla::{DomBackend, WebRenderer};
use state::{AppState, Pane};
use std::{cell::RefCell, rc::Rc};
use wasm_bindgen::prelude::*;
use wasm_bindgen_futures::spawn_local;

#[wasm_bindgen(start)]
pub fn main() -> Result<(), JsValue> {
    // Set up panic hook for better error messages
    console_error_panic_hook::set_once();

    // Initialize app state
    let app_state = Rc::new(RefCell::new(AppState::new()));

    // Load cached lists from storage
    state::refresh::load_pane_cache(Pane::FileList, &mut app_state.borrow_mut());
    state::refresh::load_pane_cache(Pane::ContainerList, &mut app_state.borrow_mut());

    // Initialize Ratzilla backend and terminal
    let backend = DomBackend::new().map_err(|e| JsValue::from_str(&e.to_string()))?;
    let terminal =
        ratzilla::ratatui::Terminal::new(backend).map_err(|e| JsValue::from_str(&e.to_string()))?;

    // Show welcome message and load data based on restored pane
    {
        let state = app_state.borrow();
        let current_pane = state.focus;
        drop(state);

        match current_pane {
            Pane::FileList | Pane::Editor => {
                // Load file list if we restored to FileList or Editor
                let state_clone = Rc::clone(&app_state);
                spawn_local(async move {
                    match api::fetch_file_list().await {
                        Ok(files) => {
                            let mut st = state_clone.borrow_mut();
                            // Only save to cache if data changed
                            if st.file_list.files != files {
                                storage::generic::save("file-list", &files);
                            }
                            st.file_list.set_files(files);
                            st.set_status("Restored session");
                        }
                        Err(e) => {
                            storage::generic::clear("file-list");
                            state::status_helper::set_status_timed(
                                &state_clone,
                                format!("Error loading files: {}", utils::error::format_error(&e)),
                            );
                        }
                    }
                });
            }
            Pane::ContainerList => {
                // Load container list if we restored to ContainerList
                state::refresh::refresh_pane(Pane::ContainerList, &app_state);
                let mut state = app_state.borrow_mut();
                state.set_status("Restored session");
            }
            Pane::Menu => {
                let mut state = app_state.borrow_mut();
                state.set_status("Welcome to Config Manager");
            }
        }
    }

    // Start background refresh for container list (every 10 seconds)
    state::refresh::start_background_refresh(&app_state);

    // Set up key event handler
    terminal.on_key_event({
        let state_clone = Rc::clone(&app_state);
        move |key_event| {
            events::handle_key_event(Rc::clone(&state_clone), key_event);
        }
    });

    // Set up drawing loop
    terminal.draw_web(move |f| {
        let state = app_state.borrow();
        ui::render(f, &state);
    });

    Ok(())
}
