use super::validation::validate_filename;
use crate::config::SharedConfig;
use crate::routes::types::{
    FileContentResponse, FileInfo, FileListResponse, WriteConfigRequest, WriteConfigResponse,
};
use axum::{
    Json,
    extract::{Path, State},
    http::StatusCode,
};

/// GET /api/configs - List all config files
pub async fn list_configs(
    State(config): State<SharedConfig>,
) -> Result<Json<FileListResponse>, (StatusCode, String)> {
    // Build file info list with metadata
    let mut files = Vec::new();
    for name in config.list_files() {
        if let Some(file_cfg) = config.get_file(&name) {
            files.push(FileInfo {
                name: file_cfg.name.clone(),
                description: file_cfg.description.clone(),
                readonly: file_cfg.readonly,
            });
        }
    }
    Ok(Json(FileListResponse { files }))
}

/// GET /api/configs/*filename - Read a config file
pub async fn read_config(
    State(config): State<SharedConfig>,
    Path(filename): Path<String>,
) -> Result<Json<FileContentResponse>, (StatusCode, String)> {
    // Wildcard routes include leading slash, strip it
    let filename = filename.strip_prefix('/').unwrap_or(&filename);

    validate_filename(filename, &config)?;

    // Look up file in config
    let file_config = config.get_file(filename).ok_or((
        StatusCode::NOT_FOUND,
        format!("File not found in config: {}", filename),
    ))?;

    let path = &file_config.path;

    match tokio::fs::read_to_string(path).await {
        Ok(content) => Ok(Json(FileContentResponse { content })),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Err((
            StatusCode::NOT_FOUND,
            format!("File not found on disk: {}", path),
        )),
        Err(e) => Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Read error: {}", e),
        )),
    }
}

/// POST /api/configs/*filename - Write a config file
pub async fn write_config(
    State(config): State<SharedConfig>,
    Path(filename): Path<String>,
    Json(payload): Json<WriteConfigRequest>,
) -> Result<Json<WriteConfigResponse>, (StatusCode, String)> {
    // Wildcard routes include leading slash, strip it
    let filename = filename.strip_prefix('/').unwrap_or(&filename);

    validate_filename(filename, &config)?;

    // Look up file in config
    let file_config = config.get_file(filename).ok_or((
        StatusCode::NOT_FOUND,
        format!("File not found in config: {}", filename),
    ))?;

    // Check if file is readonly
    if file_config.readonly {
        return Err((
            StatusCode::FORBIDDEN,
            format!("File is read-only: {}", filename),
        ));
    }

    let path = &file_config.path;

    // Create backup before writing (if file exists)
    let backup_path = format!("{}.backup", path);
    let _ = tokio::fs::copy(path, &backup_path).await;

    match tokio::fs::write(path, payload.content.as_bytes()).await {
        Ok(_) => Ok(Json(WriteConfigResponse { success: true })),
        Err(e) => Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Write error: {}", e),
        )),
    }
}
