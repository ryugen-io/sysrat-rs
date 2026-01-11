use crate::routes::types::{
    FileContentResponse, FileInfo, FileListResponse, WriteConfigRequest, WriteConfigResponse,
};
use axum::{
    Json,
    extract::{Path, State},
    http::StatusCode,
};
use sysrat_core::config::SharedConfig;

/// GET /api/configs - List all config files
pub async fn list_configs(
    State(config): State<SharedConfig>,
) -> Result<Json<FileListResponse>, (StatusCode, String)> {
    let files = sysrat_core::configs::actions::list_files(&config).await;
    // Convert core::types::FileInfo to routes::types::FileInfo if they are different,
    // OR likely logic is: core types should replace routes types eventually.
    // For now, let's assume we map or use the same types if I replace imports.
    // But wait, I haven't replaced imports yet.
    // Let's rely on mapping for safety or better: REPLACE the usage of FileInfo in routes with core::types::FileInfo

    // Actually, let's map it clearly to avoid type errors if I haven't switched everything.
    let mapped_files = files
        .into_iter()
        .map(|f| FileInfo {
            name: f.name,
            description: f.description,
            readonly: f.readonly,
            category: f.category,
            theme: f.theme,
        })
        .collect();

    Ok(Json(FileListResponse {
        files: mapped_files,
    }))
}

/// GET /api/configs/*filename - Read a config file
pub async fn read_config(
    State(config): State<SharedConfig>,
    Path(filename): Path<String>,
) -> Result<Json<FileContentResponse>, (StatusCode, String)> {
    // Wildcard routes include leading slash, strip it
    let filename = filename.strip_prefix('/').unwrap_or(&filename);

    match sysrat_core::configs::actions::read_file(filename, &config).await {
        Ok(content) => Ok(Json(FileContentResponse { content })),
        Err(e) => {
            let status: StatusCode = match e.kind() {
                std::io::ErrorKind::NotFound => StatusCode::NOT_FOUND,
                _ => StatusCode::INTERNAL_SERVER_ERROR,
            };
            Err((status, format!("Read error: {}", e)))
        }
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

    match sysrat_core::configs::actions::write_file(filename, &payload.content, &config).await {
        Ok(_) => Ok(Json(WriteConfigResponse { success: true })),
        Err(e) => {
            let status: StatusCode = match e.kind() {
                std::io::ErrorKind::NotFound => StatusCode::NOT_FOUND,
                std::io::ErrorKind::PermissionDenied => StatusCode::FORBIDDEN,
                _ => StatusCode::INTERNAL_SERVER_ERROR,
            };
            Err((status, format!("Write error: {}", e)))
        }
    }
}
