use super::super::types::{ContainerActionResponse, ContainerInfo, ContainerListResponse};
use super::actions::execute_container_action;
use axum::{Json, extract::Path, http::StatusCode};
use k_lib::config::Cookbook;
use k_lib::logger;
use tokio::process::Command;

const SCOPE: &str = "DOCKER";
const APP_NAME: &str = "sysrat";

fn log(cookbook: &Cookbook, level: &str, msg: &str) {
    logger::log_to_terminal(cookbook, level, SCOPE, msg);
    let _ = logger::log_to_file(cookbook, level, SCOPE, msg, Some(APP_NAME));
}

/// GET /api/containers - List all Docker containers
pub async fn list_containers() -> Result<Json<ContainerListResponse>, (StatusCode, String)> {
    let cookbook = Cookbook::load().ok();

    if let Some(ref cb) = cookbook {
        log(cb, "info", "GET /api/containers - listing");
    }

    let output = Command::new("docker")
        .args([
            "ps",
            "-a",
            "--format",
            "{{.ID}}\t{{.Names}}\t{{.State}}\t{{.Status}}",
        ])
        .output()
        .await
        .map_err(|e| {
            if let Some(ref cb) = cookbook {
                log(cb, "error", &format!("docker ps failed: {}", e));
            }
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Failed to execute docker command: {}", e),
            )
        })?;

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        if let Some(ref cb) = cookbook {
            log(cb, "error", &format!("docker ps failed: {}", error));
        }
        return Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Docker command failed: {}", error),
        ));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let mut containers = Vec::new();

    for line in stdout.lines() {
        let parts: Vec<&str> = line.split('\t').collect();
        if parts.len() >= 4 {
            containers.push(ContainerInfo {
                id: parts[0].to_string(),
                name: parts[1].to_string(),
                state: parts[2].to_string(),
                status: parts[3].to_string(),
            });
        }
    }

    if let Some(ref cb) = cookbook {
        log(
            cb,
            "success",
            &format!("Found {} containers", containers.len()),
        );
    }

    Ok(Json(ContainerListResponse { containers }))
}

/// POST /api/containers/:id/start - Start a container
pub async fn start_container(
    Path(id): Path<String>,
) -> Result<Json<ContainerActionResponse>, (StatusCode, String)> {
    execute_container_action(&id, "start").await
}

/// POST /api/containers/:id/stop - Stop a container
pub async fn stop_container(
    Path(id): Path<String>,
) -> Result<Json<ContainerActionResponse>, (StatusCode, String)> {
    execute_container_action(&id, "stop").await
}

/// POST /api/containers/:id/restart - Restart a container
pub async fn restart_container(
    Path(id): Path<String>,
) -> Result<Json<ContainerActionResponse>, (StatusCode, String)> {
    execute_container_action(&id, "restart").await
}
