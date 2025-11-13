use super::{AppState, Pane, status_helper};
use gloo_timers::callback::Interval;
use std::{cell::RefCell, rc::Rc};
use wasm_bindgen_futures::spawn_local;

/// Refresh data for a specific pane
pub fn refresh_pane(pane: Pane, state_rc: &Rc<RefCell<AppState>>) {
    match pane {
        Pane::FileList => refresh_file_list(state_rc),
        Pane::ContainerList => refresh_container_list(state_rc),
        _ => {}
    }
}

/// Save selection index for a pane
pub fn save_selection(pane: Pane, state: &AppState) {
    match pane {
        Pane::FileList => {
            crate::storage::generic::save("file-list-selection", &state.file_list.selected_index);
        }
        Pane::ContainerList => {
            crate::storage::generic::save(
                "container-list-selection",
                &state.container_list.selected_index,
            );
        }
        _ => {}
    }
}

/// Load cached data for a pane from storage
pub fn load_pane_cache(pane: Pane, state: &mut AppState) {
    match pane {
        Pane::FileList => {
            if let Some(files) = crate::storage::generic::load("file-list") {
                state.file_list.set_files(files);
            }
            // Restore selection index
            if let Some(index) = crate::storage::generic::load::<usize>("file-list-selection")
                && index < state.file_list.files.len()
            {
                state.file_list.selected_index = index;
            }
        }
        Pane::ContainerList => {
            if let Some(containers) = crate::storage::generic::load("container-list") {
                state.container_list.set_containers(containers);
            }
            // Restore selection index
            if let Some(index) = crate::storage::generic::load::<usize>("container-list-selection")
                && index < state.container_list.containers.len()
            {
                state.container_list.selected_index = index;
            }
        }
        _ => {}
    }
}

fn refresh_file_list(state_rc: &Rc<RefCell<AppState>>) {
    let state_clone = Rc::clone(state_rc);
    spawn_local(async move {
        match crate::api::fetch_file_list().await {
            Ok(files) => {
                let mut st = state_clone.borrow_mut();
                // Only save to cache if data changed
                if st.file_list.files != files {
                    crate::storage::generic::save("file-list", &files);
                }
                st.file_list.set_files(files);
                // Don't overwrite status on success - let action messages show
            }
            Err(e) => {
                crate::storage::generic::clear("file-list");
                status_helper::set_status_timed(
                    &state_clone,
                    format!("Error loading files: {:?}", e),
                );
            }
        }
    });
}

fn refresh_container_list(state_rc: &Rc<RefCell<AppState>>) {
    let state_clone = Rc::clone(state_rc);
    spawn_local(async move {
        match crate::api::fetch_container_list().await {
            Ok(containers) => {
                let mut st = state_clone.borrow_mut();
                // Only save to cache if data changed (important for background refresh!)
                if st.container_list.containers != containers {
                    crate::storage::generic::save("container-list", &containers);
                }
                st.container_list.set_containers(containers);
                // Don't overwrite status on success - let action messages show
            }
            Err(e) => {
                crate::storage::generic::clear("container-list");
                status_helper::set_status_timed(
                    &state_clone,
                    format!("Error loading containers: {:?}", e),
                );
            }
        }
    });
}

/// Start background refresh timer for container list
/// Refreshes every 10 seconds to keep container status up-to-date
pub fn start_background_refresh(state_rc: &Rc<RefCell<AppState>>) {
    let state_clone = Rc::clone(state_rc);

    // Create interval that fires every 10 seconds
    let interval = Interval::new(10_000, move || {
        refresh_container_list(&state_clone);
    });

    // Prevent interval from being dropped (it needs to keep running)
    interval.forget();
}
