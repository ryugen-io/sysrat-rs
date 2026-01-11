use std::fs;

pub fn extract_dependency_versions() {
    // Frontend Cargo.toml
    let cargo_toml = fs::read_to_string("Cargo.toml").expect("Failed to read Cargo.toml");

    // Extract ratzilla version
    if let Some(version) = find_dependency_version(&cargo_toml, "ratzilla") {
        println!("cargo:rustc-env=RATZILLA_VERSION={}", version);
    }

    // Extract tui-textarea version (which depends on ratatui)
    if find_dependency_version(&cargo_toml, "tui-textarea").is_some() {
        // tui-textarea 0.7 uses ratatui 0.29
        println!("cargo:rustc-env=RATATUI_VERSION=0.29");
    }

    // Extract tachyonfx version
    if let Some(version) = find_dependency_version(&cargo_toml, "tachyonfx") {
        println!("cargo:rustc-env=TACHYONFX_VERSION={}", version);
    }

    // Extract Rust edition from frontend Cargo.toml
    if let Some(edition) = extract_edition(&cargo_toml) {
        println!("cargo:rustc-env=RUST_EDITION={}", edition);
    }

    // Set Rust version (from rustc)
    if let Ok(output) = std::process::Command::new("rustc")
        .arg("--version")
        .output()
        && let Ok(version_str) = String::from_utf8(output.stdout)
    {
        // Extract version number from "rustc 1.82.0 (f6e511eec 2024-10-15)"
        if let Some(version) = version_str.split_whitespace().nth(1) {
            println!("cargo:rustc-env=RUST_VERSION={}", version);
        }
    }

    // Axum version from server Cargo.toml
    if let Ok(server_toml) = fs::read_to_string("../server/Cargo.toml")
        && let Some(version) = find_dependency_version(&server_toml, "axum")
    {
        println!("cargo:rustc-env=AXUM_VERSION={}", version);
    }
}

fn find_dependency_version(cargo_toml: &str, dependency_name: &str) -> Option<String> {
    cargo_toml
        .lines()
        .find(|line| line.contains(dependency_name))
        .and_then(parse_version_from_line)
}

fn parse_version_from_line(line: &str) -> Option<String> {
    // Try to extract version from lines like: ratzilla = "0.2"
    if let Some(start) = line.find('"')
        && let Some(end) = line[start + 1..].find('"')
    {
        return Some(line[start + 1..start + 1 + end].to_string());
    }
    // Try to extract from version = "x.y" format
    if let Some(start) = line.find("version") {
        let rest = &line[start..];
        if let Some(quote_start) = rest.find('"')
            && let Some(quote_end) = rest[quote_start + 1..].find('"')
        {
            return Some(rest[quote_start + 1..quote_start + 1 + quote_end].to_string());
        }
    }
    None
}

fn extract_edition(cargo_toml: &str) -> Option<String> {
    cargo_toml
        .lines()
        .find(|line| line.contains("edition"))
        .and_then(|line| {
            if let Some(start) = line.find('"')
                && let Some(end) = line[start + 1..].find('"')
            {
                Some(line[start + 1..start + 1 + end].to_string())
            } else {
                None
            }
        })
}
