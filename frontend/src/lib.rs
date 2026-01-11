mod api;
mod dom;
mod events;
mod init;
mod keybinds;
mod state;
mod storage;
mod theme;
mod ui;
mod utils;

use ratzilla::{DomBackend, WebRenderer};
use state::AppState;
use std::{cell::RefCell, rc::Rc};
use wasm_bindgen::prelude::*;

// Re-export update_dom_for_theme for use in event handlers
pub use dom::update_dom_for_theme;

#[wasm_bindgen(start)]
pub fn main() -> Result<(), JsValue> {
    // Set up panic hook for better error messages
    console_error_panic_hook::set_once();

    // Initialize app state
    let app_state = Rc::new(RefCell::new(AppState::new()));

    // Set up theme in DOM
    init::setup_theme(&app_state);

    // Load cached lists from storage
    init::load_cache(&mut app_state.borrow_mut());

    // Initialize Ratzilla backend and terminal
    let backend = DomBackend::new().map_err(|e| JsValue::from_str(&e.to_string()))?;
    let terminal =
        ratzilla::ratatui::Terminal::new(backend).map_err(|e| JsValue::from_str(&e.to_string()))?;

    // Load data based on restored pane
    web_sys::console::log_1(&wasm_bindgen::JsValue::from_str(&format!(
        "[DEBUG] Initial focus: {:?}",
        app_state.borrow().focus
    )));
    init::load_pane_data(&app_state);

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
