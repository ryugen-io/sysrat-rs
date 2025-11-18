use super::{ContainerListState, EditorState, FileListState, MenuState, Pane, VimMode, refresh};
use crate::{
    api::ContainerDetails,
    keybinds::Keybinds,
    storage,
    theme::{ThemeConfig, load_current_theme},
};

pub struct AppState {
    pub focus: Pane,
    pub vim_mode: VimMode,
    pub menu: MenuState,
    pub file_list: FileListState,
    pub container_list: ContainerListState,
    pub container_details: Option<ContainerDetails>,
    pub editor: EditorState,
    pub dirty: bool,
    pub status_message: Option<String>,
    pub keybinds: Keybinds,
    pub current_theme: ThemeConfig,
}

impl AppState {
    pub fn new() -> Self {
        let mut state = Self {
            focus: Pane::Menu,
            vim_mode: VimMode::Normal,
            menu: MenuState::new(),
            file_list: FileListState::new(),
            container_list: ContainerListState::new(),
            container_details: None,
            editor: EditorState::new(),
            dirty: false,
            status_message: None,
            keybinds: Keybinds::load(),
            current_theme: load_current_theme(),
        };

        // Try to restore from localStorage
        if let Some(saved) = storage::load_state()
            && let Some(pane) = Pane::from_str(&saved.pane)
        {
            state.focus = pane;

            // If we were in the editor, restore the file
            if pane == Pane::Editor
                && let (Some(filename), Some(content)) = (saved.filename, saved.content)
            {
                state.editor.load_content(filename, content);
                state.dirty = false;
            }
        }

        state
    }

    pub fn save_to_storage(&self) {
        let filename = self.editor.current_file.as_deref();
        let content = if self.editor.current_file.is_some() {
            Some(self.editor.textarea.lines().join("\n"))
        } else {
            None
        };

        storage::save_state(self.focus.as_str(), filename, content.as_deref());

        // Also save current selection for lists
        refresh::save_selection(self.focus, self);
    }

    pub fn set_status(&mut self, message: impl Into<String>) {
        self.status_message = Some(message.into());
    }

    #[allow(dead_code)]
    pub fn clear_status(&mut self) {
        self.status_message = None;
    }

    pub fn check_dirty(&mut self) {
        let current_content = self.editor.textarea.lines().join("\n");
        self.dirty = current_content != self.editor.original_content;
    }

    pub fn set_theme(&mut self, theme_name: &str) {
        // DEBUG: Uncomment for set_theme diagnostics
        // web_sys::console::log_1(&wasm_bindgen::JsValue::from_str(&format!(
        //     "[DEBUG] set_theme called with: '{}'",
        //     theme_name
        // )));

        match crate::theme::load_theme_by_name(theme_name) {
            Ok(theme) => {
                // DEBUG: Uncomment for successful theme load diagnostics
                // web_sys::console::log_1(&wasm_bindgen::JsValue::from_str(&format!(
                //     "[DEBUG] Theme '{}' loaded successfully in set_theme",
                //     theme_name
                // )));

                self.current_theme = theme;
                crate::theme::save_theme_preference(theme_name);

                // Update DOM elements
                if let Err(e) = crate::update_dom_for_theme(&self.current_theme) {
                    web_sys::console::error_1(&wasm_bindgen::JsValue::from_str(&format!(
                        "Failed to update DOM for theme: {:?}",
                        e
                    )));
                }

                self.set_status(format!("Theme changed to: {}", theme_name));
            }
            Err(e) => {
                web_sys::console::error_1(&wasm_bindgen::JsValue::from_str(&format!(
                    "Failed to load theme '{}': {}",
                    theme_name, e
                )));
                self.set_status(format!("Theme '{}' not found", theme_name));
            }
        }
    }
}
