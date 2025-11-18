mod container_list;
mod editor;
mod file_list;
mod menu;

use crate::state::{AppState, Pane};
use ratzilla::event::{KeyCode, KeyEvent};
use std::{cell::RefCell, rc::Rc};

/// Check if a key event matches a keybind string from keybinds.toml.
/// Supports: single chars, special keys, and modifier combinations.
pub fn key_matches(event: &KeyEvent, binding: &str) -> bool {
    // Handle modifier + key combinations
    if let Some(stripped) = binding.strip_prefix("Ctrl-") {
        if !event.ctrl {
            return false;
        }
        return match_key_without_mods(event, stripped);
    }

    if let Some(stripped) = binding.strip_prefix("Alt-") {
        if !event.alt {
            return false;
        }
        return match_key_without_mods(event, stripped);
    }

    if let Some(stripped) = binding.strip_prefix("Shift-") {
        if !event.shift {
            return false;
        }
        return match_key_without_mods(event, stripped);
    }

    // No modifiers
    match_key_without_mods(event, binding)
}

/// Match key code without modifier check
pub fn match_key_without_mods(event: &KeyEvent, key_str: &str) -> bool {
    match key_str {
        "Enter" => event.code == KeyCode::Enter,
        "Esc" | "Escape" => event.code == KeyCode::Esc,
        "Tab" => event.code == KeyCode::Tab,
        "Backspace" => event.code == KeyCode::Backspace,
        "Delete" => event.code == KeyCode::Delete,
        "Left" => event.code == KeyCode::Left,
        "Right" => event.code == KeyCode::Right,
        "Up" => event.code == KeyCode::Up,
        "Down" => event.code == KeyCode::Down,
        s if s.starts_with('F') && s.len() > 1 => {
            // Function keys: F1, F2, etc.
            if let Ok(num) = s[1..].parse::<u8>() {
                event.code == KeyCode::F(num)
            } else {
                false
            }
        }
        s if s.len() == 1 => {
            // Single character (case-insensitive)
            let ch = s.chars().next().unwrap().to_ascii_lowercase();
            matches!(event.code, KeyCode::Char(c) if c.to_ascii_lowercase() == ch)
        }
        _ => false,
    }
}

pub fn handle_key_event(state: Rc<RefCell<AppState>>, key_event: KeyEvent) {
    let mut state_mut = state.borrow_mut();

    // Global keybindings (work in any pane/mode)
    let keybinds = &state_mut.keybinds.global;

    // Save file
    if key_matches(&key_event, &keybinds.save) {
        if let Some(filename) = state_mut.editor.current_file.clone() {
            let content = state_mut.editor.get_content();
            drop(state_mut); // Release borrow before async

            menu::save_file(state, filename, content);
        }
        return;
    }

    // Cycle theme
    if key_matches(&key_event, &keybinds.cycle_theme) {
        let current_name =
            crate::theme::load_theme_preference().unwrap_or_else(|| "mocha".to_string());
        let next_name = crate::theme::next_theme_name(&current_name);
        state_mut.set_theme(&next_name);
        return;
    }

    // Focus file list
    if key_matches(&key_event, &keybinds.back_to_files) {
        state_mut.focus = Pane::FileList;
        state_mut.save_to_storage();
        return;
    }

    // Ctrl+Right: Focus editor (hardcoded for now)
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
