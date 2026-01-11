use super::super::types::ContainerActionResponse;
use axum::{Json, http::StatusCode};

/// Execute a docker action (start/stop/restart) on a container
/// Timeout: 120 seconds for long-running operations
pub(super) async fn execute_container_action(
    container_id: &str,
    action: &str,
) -> Result<Json<ContainerActionResponse>, (StatusCode, String)> {
    match sysrat_core::containers::actions::execute_container_action(container_id, action).await {
        Ok(_) => {
            let past_tense = match action {
                "start" => "started",
                "stop" => "stopped",
                "restart" => "restarted",
                _ => action,
            };

            Ok(Json(ContainerActionResponse {
                success: true,
                message: format!("container {}", past_tense),
            }))
        }
        Err(e) => {
            let status: StatusCode = match e.kind() {
                std::io::ErrorKind::TimedOut => StatusCode::REQUEST_TIMEOUT,
                _ => StatusCode::INTERNAL_SERVER_ERROR,
            };
            Err((status, format!("docker {} failed: {}", action, e)))
        }
    }
}
