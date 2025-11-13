use crate::state::{AppState, status_helper};
use crate::utils;
use gloo_timers::callback::Interval;
use std::{cell::RefCell, rc::Rc};
use wasm_bindgen_futures::spawn_local;

pub fn refresh_container_list(state_rc: &Rc<RefCell<AppState>>) {
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
                    format!(
                        "Error loading containers: {}",
                        utils::error::format_error(&e)
                    ),
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
