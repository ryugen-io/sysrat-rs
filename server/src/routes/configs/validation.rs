use axum::http::StatusCode;

/// Allowed file extensions for config files
const ALLOWED_EXTENSIONS: &[&str] = &[
    "conf", "toml", "txt", "sh", "fish", "rs", "json", "yaml", "yml", "ini", "env",
];

/// Validates a filename for security
pub(super) fn validate_filename(filename: &str) -> Result<(), (StatusCode, String)> {
    // Security: No path traversal or Windows paths
    // Forward slashes (/) are allowed for directory-scanned files
    if filename.contains("..") || filename.contains('\\') {
        return Err((StatusCode::BAD_REQUEST, "Invalid filename".into()));
    }

    // Extract extension from filename (handle paths with slashes)
    let actual_filename = filename.rsplit('/').next().unwrap_or(filename);

    // Check if extension is whitelisted
    let has_valid_extension = ALLOWED_EXTENSIONS
        .iter()
        .any(|ext| actual_filename.ends_with(&format!(".{}", ext)));

    if !has_valid_extension {
        return Err((
            StatusCode::BAD_REQUEST,
            format!(
                "File extension not allowed. Allowed: {}",
                ALLOWED_EXTENSIONS.join(", ")
            ),
        ));
    }

    Ok(())
}
