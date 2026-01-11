use k_lib::config::Cookbook;
use k_lib::logger;
use std::io;
use std::time::Duration;
use tokio::process::Command;

const SCOPE: &str = "DOCKER";
const APP_NAME: &str = "sysrat";

fn log(cookbook: &Cookbook, level: &str, msg: &str) {
    logger::log_to_terminal(cookbook, level, SCOPE, msg);
    let _ = logger::log_to_file(cookbook, level, SCOPE, msg, Some(APP_NAME));
}

/// Execute a docker action (start/stop/restart) on a container
/// Timeout: 120 seconds for long-running operations
pub async fn execute_container_action(container_id: &str, action: &str) -> io::Result<()> {
    let cookbook = Cookbook::load().ok();

    if let Some(ref cb) = cookbook {
        log(cb, "info", &format!("docker {} {}", action, container_id));
    }

    let docker_cmd = Command::new("docker").args([action, container_id]).output();

    let output = tokio::time::timeout(Duration::from_secs(120), docker_cmd)
        .await
        .map_err(|e| {
            if let Some(ref cb) = cookbook {
                log(cb, "error", &format!("docker {} timed out", action));
            }
            io::Error::new(
                io::ErrorKind::TimedOut,
                format!("docker {} timed out: {}", action, e),
            )
        })?
        .map_err(|e| {
            if let Some(ref cb) = cookbook {
                log(cb, "error", &format!("docker {} failed: {}", action, e));
            }
            io::Error::other(format!("docker {} failed: {}", action, e))
        })?;

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        if let Some(ref cb) = cookbook {
            log(cb, "error", &format!("docker {} failed: {}", action, error));
        }
        return Err(io::Error::other(format!(
            "docker {} failed: {}",
            action, error
        )));
    }

    if let Some(ref cb) = cookbook {
        log(
            cb,
            "success",
            &format!("docker {} {} completed", action, container_id),
        );
    }

    Ok(())
}
