mod generator;
mod scanner;

use generator::generate_theme_loader_code;
use scanner::scan_themes;

/// Main entry point for theme configuration loading
pub fn load_theme_config() {
    // Embed all available themes for runtime selection
    embed_runtime_themes();
}

fn embed_runtime_themes() {
    const BLUE: &str = "\x1b[38;2;137;180;250m";
    const GREEN: &str = "\x1b[38;2;166;227;161m";
    const MAUVE: &str = "\x1b[38;2;203;166;247m";
    const NC: &str = "\x1b[0m";
    const INFO_ICON: &str = "\u{f05a}"; //
    const CHECK_ICON: &str = "\u{f00c}"; //

    // Scan all available themes (built-in + user custom)
    let (themes, default_count, user_count, user_dir) = scan_themes();

    eprintln!(
        "{}{}  {}[themes] Embedded {} theme(s) total ({} default + {} custom)",
        BLUE,
        INFO_ICON,
        NC,
        themes.len(),
        default_count,
        user_count
    );

    if user_count > 0 {
        eprintln!(
            "{}{}  {}[themes] Found {} custom theme(s) in {}{}",
            GREEN,
            CHECK_ICON,
            NC,
            user_count,
            MAUVE,
            user_dir.as_ref().map_or("", |p| p.as_str())
        );
    }

    // Set theme file paths as env vars (for custom themes if needed)
    for (name, path) in &themes {
        let env_name = format!("THEME_FILE_{}", name.to_uppercase().replace('-', "_"));
        println!("cargo:rustc-env={}={}", env_name, path.display());
    }

    // Generate theme names list (for runtime iteration)
    let mut theme_names: Vec<&str> = themes.iter().map(|(n, _)| n.as_str()).collect();
    theme_names.sort(); // Sort alphabetically for consistent ordering
    let theme_names_str = theme_names.join(",");
    eprintln!("[theme] THEME_NAMES = {:?}", theme_names_str);
    println!("cargo:rustc-env=THEME_NAMES={}", theme_names_str);

    // Generate match arms for load_theme_by_name()
    generate_theme_loader_code(&themes);
}
