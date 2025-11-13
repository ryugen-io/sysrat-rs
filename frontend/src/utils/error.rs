use wasm_bindgen::JsValue;

/// Convert JsValue error to a readable string
/// Extracts the inner string without the JsValue(...) wrapper
pub fn format_error(e: &JsValue) -> String {
    e.as_string().unwrap_or_else(|| format!("{:?}", e))
}
