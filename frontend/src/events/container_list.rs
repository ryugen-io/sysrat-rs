use crate::api;
use crate::state::{AppState, Pane, refresh, status_helper};
use ratzilla::event::{KeyCode, KeyEvent};
use std::{cell::RefCell, rc::Rc};
use wasm_bindgen_futures::spawn_local;

pub fn handle_keys(state: &mut AppState, state_rc: &Rc<RefCell<AppState>>, key_event: KeyEvent) {
    match key_event.code {
        KeyCode::Char('j') | KeyCode::Down => {
            state.container_list.next();
            refresh::save_selection(Pane::ContainerList, state);
        }
        KeyCode::Char('k') | KeyCode::Up => {
            state.container_list.previous();
            refresh::save_selection(Pane::ContainerList, state);
        }
        KeyCode::Char('s') => {
            if let Some(container) = state.container_list._selected() {
                let container_id = container.id.clone();
                let container_name = container.name.clone();
                let state_clone = Rc::clone(state_rc);
                spawn_local(async move {
                    match api::start_container(&container_id).await {
                        Ok(msg) => {
                            status_helper::set_status_timed(
                                &state_clone,
                                format!("Started {}: {}", container_name, msg),
                            );
                            refresh::refresh_pane(Pane::ContainerList, &state_clone);
                        }
                        Err(e) => {
                            status_helper::set_status_timed(
                                &state_clone,
                                format!("Failed to start {}: {:?}", container_name, e),
                            );
                            refresh::refresh_pane(Pane::ContainerList, &state_clone);
                        }
                    }
                });
            }
        }
        KeyCode::Char('x') => {
            if let Some(container) = state.container_list._selected() {
                let container_id = container.id.clone();
                let container_name = container.name.clone();
                let state_clone = Rc::clone(state_rc);
                spawn_local(async move {
                    match api::stop_container(&container_id).await {
                        Ok(msg) => {
                            status_helper::set_status_timed(
                                &state_clone,
                                format!("Stopped {}: {}", container_name, msg),
                            );
                            refresh::refresh_pane(Pane::ContainerList, &state_clone);
                        }
                        Err(e) => {
                            status_helper::set_status_timed(
                                &state_clone,
                                format!("Failed to stop {}: {:?}", container_name, e),
                            );
                            refresh::refresh_pane(Pane::ContainerList, &state_clone);
                        }
                    }
                });
            }
        }
        KeyCode::Char('r') => {
            if let Some(container) = state.container_list._selected() {
                let container_id = container.id.clone();
                let container_name = container.name.clone();
                let state_clone = Rc::clone(state_rc);
                spawn_local(async move {
                    match api::restart_container(&container_id).await {
                        Ok(msg) => {
                            status_helper::set_status_timed(
                                &state_clone,
                                format!("Restarted {}: {}", container_name, msg),
                            );
                            refresh::refresh_pane(Pane::ContainerList, &state_clone);
                        }
                        Err(e) => {
                            status_helper::set_status_timed(
                                &state_clone,
                                format!("Failed to restart {}: {:?}", container_name, e),
                            );
                            refresh::refresh_pane(Pane::ContainerList, &state_clone);
                        }
                    }
                });
            }
        }
        KeyCode::Esc => {
            state.focus = Pane::Menu;
        }
        KeyCode::Left if key_event.ctrl => {
            state.focus = Pane::Menu;
        }
        _ => {}
    }
}
