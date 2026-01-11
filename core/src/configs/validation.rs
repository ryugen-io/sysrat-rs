use crate::config::AppConfig;
use std::io;

/// Validates a filename for security
/// Extension whitelist is loaded from sysrat.toml
pub fn validate_filename(filename: &str, config: &AppConfig) -> io::Result<()> {
    // Security: No path traversal or Windows paths
    // Forward slashes (/) are allowed for directory-scanned files
    if filename.contains("..") || filename.contains('\\') {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Invalid filename",
        ));
    }

    // Extract extension from filename (handle paths with slashes)
    let actual_filename = filename.rsplit('/').next().unwrap_or(filename);

    // Check if extension is whitelisted (from config)
    let allowed_extensions = config.allowed_extensions();
    let has_valid_extension = allowed_extensions
        .iter()
        .any(|ext| actual_filename.ends_with(&format!(".{}", ext)));

    if !has_valid_extension {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            format!(
                "File extension not allowed. Allowed: {}",
                allowed_extensions.join(", ")
            ),
        ));
    }

    Ok(())
}
