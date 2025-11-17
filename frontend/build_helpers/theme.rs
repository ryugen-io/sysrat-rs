use std::fs;
use std::path::PathBuf;

pub fn load_theme_config() {
    // Embed all available themes for runtime selection
    embed_runtime_themes();
}

fn embed_runtime_themes() {
    let mut themes = Vec::new();

    // Scan default themes from frontend/themes/
    if let Ok(entries) = fs::read_dir("themes") {
        for entry in entries.flatten() {
            if let Some(name) = get_theme_name(&entry.path()) {
                themes.push((name, entry.path()));
            }
        }
    }

    // Scan user custom themes from USER_THEME_DIR env var
    if let Ok(user_theme_dir) = std::env::var("USER_THEME_DIR") {
        // Expand tilde in path
        let expanded_path = if let Some(stripped) = user_theme_dir.strip_prefix("~/") {
            if let Ok(home) = std::env::var("HOME") {
                PathBuf::from(home).join(stripped)
            } else {
                PathBuf::from(&user_theme_dir)
            }
        } else {
            PathBuf::from(&user_theme_dir)
        };

        if let Ok(entries) = fs::read_dir(expanded_path) {
            for entry in entries.flatten() {
                if let Some(name) = get_theme_name(&entry.path()) {
                    // Don't duplicate if theme name already exists
                    if !themes.iter().any(|(n, _)| n == &name) {
                        themes.push((name, entry.path()));
                    }
                }
            }
        }
    }

    // Set theme file paths as env vars (for custom themes if needed)
    for (name, path) in &themes {
        let env_name = format!("THEME_FILE_{}", name.to_uppercase().replace('-', "_"));
        println!("cargo:rustc-env={}={}", env_name, path.display());
    }

    // Generate theme names list (for runtime iteration)
    let theme_names: Vec<&str> = themes.iter().map(|(n, _)| n.as_str()).collect();
    println!("cargo:rustc-env=THEME_NAMES={}", theme_names.join(","));
}

fn get_theme_name(path: &std::path::Path) -> Option<String> {
    if path.extension()? != "toml" {
        return None;
    }
    path.file_stem()?.to_str().map(String::from)
}
