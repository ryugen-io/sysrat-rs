use crate::state::{AppState, status_helper};
use crate::utils;
use std::{cell::RefCell, rc::Rc};
use wasm_bindgen_futures::spawn_local;

pub fn refresh_file_list(state_rc: &Rc<RefCell<AppState>>) {
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
                    format!("Error loading files: {}", utils::error::format_error(&e)),
                );
            }
        }
    });
}
