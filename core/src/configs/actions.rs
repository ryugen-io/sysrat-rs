use super::validation::validate_filename;
use crate::config::SharedConfig;
use crate::types::FileInfo;
use k_lib::config::Cookbook;
use k_lib::logger;
use std::io;

const SCOPE: &str = "API";
const APP_NAME: &str = "sysrat";

fn log(cookbook: &Cookbook, level: &str, msg: &str) {
    logger::log_to_terminal(cookbook, level, SCOPE, msg);
    let _ = logger::log_to_file(cookbook, level, SCOPE, msg, Some(APP_NAME));
}

/// List all managed config files
/// Refreshes the configuration before listing
pub async fn list_files(config: &SharedConfig) -> Vec<FileInfo> {
    let cookbook = Cookbook::load().ok();

    if let Some(ref cb) = cookbook {
        log(cb, "info", "GET /api/configs - list files");
    }

    // Attempt to refresh configuration
    {
        let mut writer = config.write().await;
        if let Err(e) = writer.refresh() {
            if let Some(ref cb) = cookbook {
                log(cb, "warn", &format!("Failed to refresh config: {}", e));
            }
        } else if let Some(ref cb) = cookbook {
            log(cb, "success", "Config refreshed");
        }
    }

    let reader = config.read().await;
    let files: Vec<FileInfo> = reader
        .files()
        .iter()
        .map(|file_cfg| FileInfo {
            name: file_cfg.name.clone(),
            description: file_cfg.description.clone(),
            readonly: file_cfg.readonly,
            category: file_cfg.category.clone(),
            theme: file_cfg.theme.clone(),
        })
        .collect();

    if let Some(ref cb) = cookbook {
        log(cb, "success", &format!("Returning {} files", files.len()));
    }

    files
}

/// Read a managed config file
pub async fn read_file(filename: &str, config: &SharedConfig) -> io::Result<String> {
    let cookbook = Cookbook::load().ok();

    if let Some(ref cb) = cookbook {
        log(cb, "info", &format!("GET /api/configs/{}", filename));
    }

    let reader = config.read().await;
    validate_filename(filename, &reader)?;

    let path = reader
        .get_file(filename)
        .map(|f| f.path.clone())
        .ok_or_else(|| {
            if let Some(ref cb) = cookbook {
                log(cb, "error", &format!("File not found: {}", filename));
            }
            io::Error::new(
                io::ErrorKind::NotFound,
                format!("File not found in config: {}", filename),
            )
        })?;

    if let Some(ref cb) = cookbook {
        log(cb, "info", &format!("Reading {}", path));
    }

    // Drop lock before async IO
    drop(reader);

    let result = tokio::fs::read_to_string(&path).await;

    if let Some(ref cb) = cookbook {
        match &result {
            Ok(content) => log(cb, "success", &format!("Read {} bytes", content.len())),
            Err(e) => log(cb, "error", &format!("Read failed: {}", e)),
        }
    }

    result
}

/// Write a managed config file (with backup)
pub async fn write_file(filename: &str, content: &str, config: &SharedConfig) -> io::Result<()> {
    let cookbook = Cookbook::load().ok();

    if let Some(ref cb) = cookbook {
        log(cb, "info", &format!("POST /api/configs/{}", filename));
    }

    let reader = config.read().await;
    validate_filename(filename, &reader)?;

    let file_config = reader.get_file(filename).ok_or_else(|| {
        if let Some(ref cb) = cookbook {
            log(cb, "error", &format!("File not found: {}", filename));
        }
        io::Error::new(
            io::ErrorKind::NotFound,
            format!("File not found in config: {}", filename),
        )
    })?;

    if file_config.readonly {
        if let Some(ref cb) = cookbook {
            log(cb, "error", &format!("File is read-only: {}", filename));
        }
        return Err(io::Error::new(
            io::ErrorKind::PermissionDenied,
            format!("File is read-only: {}", filename),
        ));
    }

    let path = file_config.path.clone();
    drop(reader); // Release lock before IO operations

    // Create backup
    let backup_path = format!("{}.backup", path);
    if let Some(ref cb) = cookbook {
        log(cb, "info", &format!("Creating backup: {}", backup_path));
    }
    let _ = tokio::fs::copy(&path, &backup_path).await;

    if let Some(ref cb) = cookbook {
        log(
            cb,
            "info",
            &format!("Writing {} bytes to {}", content.len(), path),
        );
    }

    let result = tokio::fs::write(&path, content.as_bytes()).await;

    if let Some(ref cb) = cookbook {
        match &result {
            Ok(_) => log(cb, "success", &format!("Saved {}", filename)),
            Err(e) => log(cb, "error", &format!("Write failed: {}", e)),
        }
    }

    result
}
