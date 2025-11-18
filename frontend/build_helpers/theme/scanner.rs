use std::fs;
use std::path::PathBuf;

/// Scan all available themes (built-in + user custom)
///
/// Returns: (themes_list, default_count, user_count, user_theme_dir)
pub fn scan_themes() -> (Vec<(String, PathBuf)>, usize, usize, Option<String>) {
    let mut themes = Vec::new();

    // Scan default themes from frontend/themes/
    let default_count = scan_default_themes(&mut themes);

    // Scan user custom themes from USER_THEME_DIR env var
    let (user_count, user_dir) = scan_user_themes(&mut themes);

    (themes, default_count, user_count, user_dir)
}

/// Scan built-in themes from frontend/themes/ directory
fn scan_default_themes(themes: &mut Vec<(String, PathBuf)>) -> usize {
    let mut count = 0;

    if let Ok(entries) = fs::read_dir("themes") {
        for entry in entries.flatten() {
            if let Some(name) = get_theme_name(&entry.path()) {
                themes.push((name, entry.path()));
                count += 1;
            }
        }
    }

    count
}

/// Scan user custom themes from USER_THEME_DIR
///
/// Returns: (count, expanded_user_dir_path)
fn scan_user_themes(themes: &mut Vec<(String, PathBuf)>) -> (usize, Option<String>) {
    let mut count = 0;
    let mut user_dir_path = None;

    if let Ok(user_theme_dir) = std::env::var("USER_THEME_DIR") {
        let expanded_path = expand_tilde(&user_theme_dir);
        user_dir_path = Some(expanded_path.display().to_string());

        if let Ok(entries) = fs::read_dir(&expanded_path) {
            for entry in entries.flatten() {
                if let Some(name) = get_theme_name(&entry.path()) {
                    // Don't duplicate if theme name already exists
                    if !themes.iter().any(|(n, _)| n == &name) {
                        themes.push((name, entry.path()));
                        count += 1;
                    }
                }
            }
        }
    }

    (count, user_dir_path)
}

/// Extract theme name from file path (without .toml extension)
fn get_theme_name(path: &std::path::Path) -> Option<String> {
    if path.extension()? != "toml" {
        return None;
    }
    path.file_stem()?.to_str().map(String::from)
}

/// Expand tilde (~) in path to HOME directory
fn expand_tilde(path: &str) -> PathBuf {
    if let Some(stripped) = path.strip_prefix("~/")
        && let Ok(home) = std::env::var("HOME")
    {
        return PathBuf::from(home).join(stripped);
    }
    PathBuf::from(path)
}
