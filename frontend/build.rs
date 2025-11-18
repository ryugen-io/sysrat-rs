mod build_helpers;

use build_helpers::{ascii, date, hash, keybinds, statusline, theme, version};

fn main() {
    // Load environment from sys/env/.env
    let env_file =
        std::env::var("SYSRAT_ENV_FILE").unwrap_or_else(|_| "../sys/env/.env".to_string());
    if let Err(e) = dotenvy::from_filename(&env_file) {
        eprintln!("Warning: Could not load {}: {}", env_file, e);
    }

    // Extract dependency versions from Cargo.toml
    version::extract_dependency_versions();

    // Set build metadata
    date::set_build_date();
    hash::set_build_hash();

    // Load theme configuration
    theme::load_theme_config();

    // Load keybinds configuration
    keybinds::load_keybinds_config();

    // Load ASCII art
    ascii::load_ascii_art();

    // Load status line configuration
    statusline::load_statusline_config();

    // Rerun if files change
    println!("cargo:rerun-if-changed=Cargo.toml");
    println!("cargo:rerun-if-changed=../sys/theme/theme.toml");

    // Dynamically track all theme files
    if let Ok(entries) = std::fs::read_dir("themes") {
        for entry in entries.flatten() {
            if let Some(path) = entry.path().to_str()
                && path.ends_with(".toml")
            {
                println!("cargo:rerun-if-changed={}", path);
            }
        }
    }

    println!("cargo:rerun-if-changed=assets/sysrat.ascii");
    println!("cargo:rerun-if-changed=assets/menu-text.ascii");
    println!("cargo:rerun-if-changed=../.git/HEAD");
    println!("cargo:rerun-if-changed=../.git/refs/heads");
}
