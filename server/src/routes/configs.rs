use super::types::{
    FileContentResponse, FileListResponse, WriteConfigRequest, WriteConfigResponse,
};
use axum::{Json, extract::Path, http::StatusCode};

// Config file directory - could be made configurable
const CONFIG_DIR: &str = "/tmp/config-manager-configs";

// GET /api/configs - List all config files
pub async fn list_configs() -> Result<Json<FileListResponse>, (StatusCode, String)> {
    // Ensure config directory exists
    tokio::fs::create_dir_all(CONFIG_DIR).await.map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to create config dir: {}", e),
        )
    })?;

    let mut files = Vec::new();
    let mut dir = tokio::fs::read_dir(CONFIG_DIR).await.map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to read directory: {}", e),
        )
    })?;

    while let Some(entry) = dir.next_entry().await.map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to read entry: {}", e),
        )
    })? {
        if let Some(filename) = entry.file_name().to_str() {
            // Only include .conf and .toml files
            if filename.ends_with(".conf") || filename.ends_with(".toml") {
                files.push(filename.to_string());
            }
        }
    }

    files.sort();
    Ok(Json(FileListResponse { files }))
}

// GET /api/configs/:filename - Read a config file
pub async fn read_config(
    Path(filename): Path<String>,
) -> Result<Json<FileContentResponse>, (StatusCode, String)> {
    // Security: Validate filename (no path traversal)
    if filename.contains("..") || filename.contains('/') || filename.contains('\\') {
        return Err((StatusCode::BAD_REQUEST, "Invalid filename".into()));
    }

    // Only allow .conf and .toml files
    if !filename.ends_with(".conf") && !filename.ends_with(".toml") {
        return Err((
            StatusCode::BAD_REQUEST,
            "Only .conf and .toml files allowed".into(),
        ));
    }

    let path = format!("{}/{}", CONFIG_DIR, filename);

    match tokio::fs::read_to_string(&path).await {
        Ok(content) => Ok(Json(FileContentResponse { content })),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Err((
            StatusCode::NOT_FOUND,
            format!("File not found: {}", filename),
        )),
        Err(e) => Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Read error: {}", e),
        )),
    }
}

// POST /api/configs/:filename - Write a config file
pub async fn write_config(
    Path(filename): Path<String>,
    Json(payload): Json<WriteConfigRequest>,
) -> Result<Json<WriteConfigResponse>, (StatusCode, String)> {
    // Security: Validate filename
    if filename.contains("..") || filename.contains('/') || filename.contains('\\') {
        return Err((StatusCode::BAD_REQUEST, "Invalid filename".into()));
    }

    // Only allow .conf and .toml files
    if !filename.ends_with(".conf") && !filename.ends_with(".toml") {
        return Err((
            StatusCode::BAD_REQUEST,
            "Only .conf and .toml files allowed".into(),
        ));
    }

    let path = format!("{}/{}", CONFIG_DIR, filename);

    // Create backup before writing (if file exists)
    let backup_path = format!("{}.backup", path);
    let _ = tokio::fs::copy(&path, &backup_path).await;

    match tokio::fs::write(&path, payload.content.as_bytes()).await {
        Ok(_) => Ok(Json(WriteConfigResponse { success: true })),
        Err(e) => Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Write error: {}", e),
        )),
    }
}
