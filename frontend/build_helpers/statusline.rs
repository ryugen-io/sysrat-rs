use std::env;
use std::fs;
use std::path::Path;

pub fn load_statusline_config() {
    // Theme colors (Catppuccin Mocha)
    const MAUVE: &str = "\x1b[38;2;203;166;247m";
    const BLUE: &str = "\x1b[38;2;137;180;250m";
    const NC: &str = "\x1b[0m";
    const INFO_ICON: &str = "\u{f05a}"; //

    let repo_root = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap();

    // 1. Load built-in config from sys/layout/statusline.toml
    let builtin_path = repo_root.join("sys").join("layout").join("statusline.toml");
    let builtin_config = fs::read_to_string(&builtin_path).unwrap_or_else(|e| {
        panic!(
            "{}[statusline]{} failed to read built-in config at {:?}: {}",
            MAUVE, NC, builtin_path, e
        )
    });

    // 2. Check for user custom config (XDG override)
    let user_layout_dir =
        env::var("USER_LAYOUT_DIR").unwrap_or_else(|_| "~/.config/sysrat/layout".to_string());

    // Expand tilde in path manually (avoid shellexpand dependency)
    let expanded_path = if let Some(stripped) = user_layout_dir.strip_prefix("~/") {
        if let Ok(home) = env::var("HOME") {
            Path::new(&home).join(stripped)
        } else {
            Path::new(&user_layout_dir).to_path_buf()
        }
    } else {
        Path::new(&user_layout_dir).to_path_buf()
    };

    let user_config_path = expanded_path.join("statusline.toml");

    let final_config = if user_config_path.exists() {
        println!(
            "cargo:warning={}[statusline]{} {}{}  {}using user custom config: {:?}",
            MAUVE, NC, BLUE, INFO_ICON, NC, user_config_path
        );
        fs::read_to_string(&user_config_path).unwrap_or_else(|e| {
            panic!(
                "{}[statusline]{} failed to read user config at {:?}: {}",
                MAUVE, NC, user_config_path, e
            )
        })
    } else {
        println!(
            "cargo:warning={}[statusline]{} {}{}  {}using built-in config: {:?}",
            MAUVE, NC, BLUE, INFO_ICON, NC, builtin_path
        );
        builtin_config
    };

    // 3. Validate TOML syntax
    toml::from_str::<toml::Value>(&final_config).unwrap_or_else(|e| {
        panic!("invalid status line TOML configuration: {}", e);
    });

    // 4. Determine which config file to use and set path for include_str!
    let config_path_to_use = if user_config_path.exists() {
        user_config_path.display().to_string()
    } else {
        builtin_path.display().to_string()
    };

    println!(
        "cargo:rustc-env=STATUSLINE_CONFIG_PATH={}",
        config_path_to_use
    );

    // 5. Rerun build script if config files change
    println!("cargo:rerun-if-changed={}", builtin_path.display());
    if user_config_path.exists() {
        println!("cargo:rerun-if-changed={}", user_config_path.display());
    }
}
