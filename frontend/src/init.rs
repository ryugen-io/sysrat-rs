use crate::{
    api, dom,
    state::{AppState, Pane},
    storage, utils,
};
use std::{cell::RefCell, rc::Rc};
use wasm_bindgen::prelude::*;
use wasm_bindgen_futures::spawn_local;
use web_sys::window;

/// Initialize theme in DOM (background color + font)
pub fn setup_theme(app_state: &Rc<RefCell<AppState>>) {
    if let Some(win) = window()
        && let Some(doc) = win.document()
        && let Some(body) = doc.body()
    {
        let theme = &app_state.borrow().current_theme;

        // Set background color
        let mantle = theme.mantle();
        if let ratzilla::ratatui::style::Color::Rgb(r, g, b) = mantle {
            let bg_color = format!("rgb({}, {}, {})", r, g, b);
            let _ = body.set_attribute("style", &format!("background-color: {}", bg_color));
        }

        // Inject font configuration
        let font_config = &theme.font;
        if let Err(e) = dom::inject_font(&doc, font_config) {
            web_sys::console::error_1(&JsValue::from_str(&format!(
                "Failed to inject font: {:?}",
                e
            )));
        }
    }
}

/// Load cached data from browser storage
pub fn load_cache(app_state: &mut AppState) {
    crate::state::refresh::load_pane_cache(Pane::FileList, app_state);
    crate::state::refresh::load_pane_cache(Pane::ContainerList, app_state);
}

/// Load data based on current pane
pub fn load_pane_data(app_state: &Rc<RefCell<AppState>>) {
    let state = app_state.borrow();
    let current_pane = state.focus;
    drop(state);

    match current_pane {
        Pane::FileList | Pane::Editor => {
            // Load file list if we restored to FileList or Editor
            let state_clone = Rc::clone(app_state);
            spawn_local(async move {
                match api::fetch_file_list().await {
                    Ok(files) => {
                        {
                            let mut st = state_clone.borrow_mut();
                            // Only save to cache if data changed
                            if st.file_list.files != files {
                                storage::generic::save("file-list", &files);
                            }
                            st.file_list.set_files(files);
                        }
                        crate::state::status_helper::set_status_timed(
                            &state_clone,
                            "Restored session",
                        );
                    }
                    Err(e) => {
                        storage::generic::clear("file-list");
                        crate::state::status_helper::set_status_timed(
                            &state_clone,
                            format!("[ERROR loading files: {}]", utils::error::format_error(&e)),
                        );
                    }
                }
            });
        }
        Pane::ContainerList => {
            // Load container list if we restored to ContainerList
            crate::state::refresh::refresh_pane(Pane::ContainerList, app_state);
            crate::state::status_helper::set_status_timed(app_state, "Restored session");
        }
        Pane::Menu => {
            let mut state = app_state.borrow_mut();
            state.set_status("Welcome to Config Manager");
        }
        Pane::Splash => {
            // No data to load for splash
        }
    }
}
