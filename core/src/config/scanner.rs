use super::models::{ConfigDirectory, ConfigFile};
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

/// Scan a directory and return all matching files
pub fn scan_directory(dir_config: &ConfigDirectory) -> Result<Vec<ConfigFile>, String> {
    let mut found_files = Vec::new();
    let base_path = Path::new(&dir_config.path);

    // Normalize directory name (strip leading slash for consistent naming)
    let dir_name = dir_config.name.trim_start_matches('/');

    // Expand home directory
    let expanded_path = if dir_config.path.starts_with("~/") {
        let home =
            std::env::var("HOME").map_err(|_| "HOME environment variable not set".to_string())?;
        PathBuf::from(home).join(&dir_config.path[2..])
    } else {
        base_path.to_path_buf()
    };

    if !expanded_path.exists() {
        return Err(format!(
            "Directory does not exist: {}",
            expanded_path.display()
        ));
    }

    // Walk directory with depth limit
    for entry in WalkDir::new(&expanded_path)
        .max_depth(dir_config.depth)
        .follow_links(false)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        if !entry.file_type().is_file() {
            continue;
        }

        let path = entry.path();

        // Check file extension matches allowed types
        if !dir_config.types.is_empty() {
            if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                if !dir_config.types.iter().any(|t| t == ext) {
                    continue;
                }
            } else {
                continue; // No extension, skip
            }
        }

        // Create ConfigFile entry
        let relative_path = path
            .strip_prefix(&expanded_path)
            .unwrap_or(path)
            .to_string_lossy()
            .to_string();

        let file_name = path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("unknown")
            .to_string();

        // Use directory name as prefix for uniqueness
        let display_name = if relative_path.contains('/') || relative_path.contains('\\') {
            format!("{}/{}", dir_name, relative_path)
        } else {
            format!("{}/{}", dir_name, file_name)
        };

        found_files.push(ConfigFile {
            path: path.to_string_lossy().to_string(),
            name: display_name,
            description: format!("From directory: {}", dir_config.description),
            readonly: dir_config.readonly,
            category: dir_config.category.clone(),
            theme: None,
        });
    }

    // Sort by path for consistent ordering
    found_files.sort_by(|a, b| a.name.cmp(&b.name));

    Ok(found_files)
}
