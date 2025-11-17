use super::types::SavedState;
use web_sys::window;

const STORAGE_KEY: &str = "config-manager-state";

pub fn save_state(pane: &str, filename: Option<&str>, content: Option<&str>) {
    if let Some(storage) = get_local_storage() {
        let state_json = serialize_state(pane, filename, content);
        let _ = storage.set_item(STORAGE_KEY, &state_json);
    }
}

pub fn load_state() -> Option<SavedState> {
    if let Some(storage) = get_local_storage()
        && let Ok(Some(state_str)) = storage.get_item(STORAGE_KEY)
    {
        return deserialize_state(&state_str);
    }
    None
}

fn get_local_storage() -> Option<web_sys::Storage> {
    window()?.local_storage().ok()?
}

fn serialize_state(pane: &str, filename: Option<&str>, content: Option<&str>) -> String {
    format!(
        "{{\"pane\":\"{}\",\"filename\":{},\"content\":{}}}",
        pane,
        serialize_option_string(filename),
        serialize_option_string(content)
    )
}

fn serialize_option_string(value: Option<&str>) -> String {
    value
        .map(|s| {
            format!(
                "\"{}\"",
                s.replace('\\', "\\\\")
                    .replace('\"', "\\\"")
                    .replace('\n', "\\n")
                    .replace('\r', "\\r")
            )
        })
        .unwrap_or_else(|| "null".to_string())
}

fn deserialize_state(json: &str) -> Option<SavedState> {
    let json = json.trim();
    if !json.starts_with('{') || !json.ends_with('}') {
        return None;
    }

    let mut pane = None;
    let mut filename = None;
    let mut content = None;

    for part in json[1..json.len() - 1].split(',') {
        if let Some((key, value)) = part.split_once(':') {
            let key = key.trim().trim_matches('"');
            let value = value.trim();

            match key {
                "pane" => pane = Some(value.trim_matches('"').to_string()),
                "filename" => filename = deserialize_option_string(value),
                "content" => content = deserialize_option_string(value),
                _ => {}
            }
        }
    }

    pane.map(|p| SavedState {
        pane: p,
        filename,
        content,
    })
}

fn deserialize_option_string(value: &str) -> Option<String> {
    if value == "null" {
        return None;
    }

    let content_str = value.trim_matches('"');
    Some(
        content_str
            .replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\\"", "\"")
            .replace("\\\\", "\\"),
    )
}

// Theme preference storage
const THEME_KEY: &str = "config-manager-theme";

pub fn save_theme_preference(theme_name: &str) {
    if let Some(storage) = get_local_storage() {
        let _ = storage.set_item(THEME_KEY, theme_name);
    }
}

pub fn load_theme_preference() -> Option<String> {
    if let Some(storage) = get_local_storage() {
        return storage.get_item(THEME_KEY).ok()?;
    }
    None
}
