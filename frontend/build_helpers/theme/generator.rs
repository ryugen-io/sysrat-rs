use std::fs;
use std::path::{Path, PathBuf};

/// Generate Rust code for theme loading match statement
pub fn generate_theme_loader_code(themes: &[(String, PathBuf)]) {
    let out_dir = std::env::var("OUT_DIR").expect("OUT_DIR not set");
    let dest_path = PathBuf::from(out_dir).join("generated_theme_loader.rs");

    // Generate match arms for each theme
    let match_arms = generate_match_arms(themes);

    // Generate theme names array
    let theme_names: Vec<String> = themes
        .iter()
        .map(|(name, _)| format!(r#""{}""#, name))
        .collect();
    let theme_names_array = theme_names.join(", ");

    // Generate the full module code
    let code = format!(
        r#"// Auto-generated theme loader (DO NOT EDIT MANUALLY)
// Generated at build time by frontend/build_helpers/theme/generator.rs

/// Available theme names (hardcoded at build time)
pub const THEME_NAMES: &[&str] = &[{}];

/// Load theme content by name
pub fn load_theme_content(name: &str) -> Result<&'static str, String> {{
    let content = match name {{
{}
        _ => return Err(format!("Unknown theme: {{}}", name)),
    }};
    Ok(content)
}}
"#,
        theme_names_array,
        match_arms.join("\n")
    );

    fs::write(&dest_path, code).expect("Failed to write generated_theme_loader.rs");
    eprintln!(
        "[theme] Generated theme loader code at {}",
        dest_path.display()
    );
}

/// Generate match arms for all themes
fn generate_match_arms(themes: &[(String, PathBuf)]) -> Vec<String> {
    themes
        .iter()
        .map(|(name, path)| generate_single_match_arm(name, path))
        .collect()
}

/// Generate a single match arm for one theme
fn generate_single_match_arm(name: &str, path: &Path) -> String {
    // Get relative path from frontend/ directory
    let relative_path = get_relative_path(path);

    format!(
        r#"        "{}" => include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/{}")),"#,
        name, relative_path
    )
}

/// Get relative path from frontend/ directory
fn get_relative_path(path: &Path) -> String {
    if path.starts_with("themes/") {
        // Built-in theme: themes/mocha.toml
        path.to_string_lossy().to_string()
    } else {
        // User custom theme: use absolute path
        // Note: include_str! requires path relative to CARGO_MANIFEST_DIR
        // For user themes, we need to handle this differently
        path.to_string_lossy().to_string()
    }
}
