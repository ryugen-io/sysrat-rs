mod routes;
mod version;

use axum::{
    Router,
    routing::{get, post},
};
use k_lib::config::Cookbook;
use k_lib::logger;
use std::sync::Arc;
use sysrat_core::config;
use tower_http::services::ServeDir;

use tokio::sync::RwLock;

const SCOPE: &str = "SYSRAT";
const APP_NAME: &str = "sysrat";

/// Log to terminal and file
fn log(cookbook: &Cookbook, level: &str, msg: &str) {
    logger::log_to_terminal(cookbook, level, SCOPE, msg);
    let _ = logger::log_to_file(cookbook, level, SCOPE, msg, Some(APP_NAME));
}

#[tokio::main]
async fn main() {
    // Load k-lib config for logging (fallback to eprintln if unavailable)
    let cookbook = Cookbook::load().ok();

    if let Some(ref cb) = cookbook {
        log(cb, "info", &version::version_string());
        log(cb, "info", "Initializing server...");
    } else {
        println!("{}", version::version_string());
    }

    // Load environment variables from sys/env/.env if it exists
    let env_file = std::env::var("SYSRAT_ENV_FILE").unwrap_or_else(|_| "sys/env/.env".to_string());
    match dotenvy::from_filename(&env_file) {
        Ok(_) => {
            if let Some(ref cb) = cookbook {
                log(cb, "success", &format!("Loaded env from {}", env_file));
            }
        }
        Err(e) => {
            if let Some(ref cb) = cookbook {
                log(cb, "warn", &format!("Could not load {}: {}", env_file, e));
                log(cb, "info", "Using default configuration values");
            } else {
                eprintln!("Warning: Could not load {}: {}", env_file, e);
            }
        }
    }

    // Load configuration (logging happens inside AppConfig::load)
    let app_config = match config::AppConfig::load() {
        Ok(cfg) => Arc::new(RwLock::new(cfg)),
        Err(e) => {
            if let Some(ref cb) = cookbook {
                log(cb, "error", &format!("Failed to load configuration: {}", e));
            } else {
                eprintln!("Failed to load configuration: {}", e);
            }
            std::process::exit(1);
        }
    };

    // Setup routes
    if let Some(ref cb) = cookbook {
        log(cb, "info", "Registering API routes...");
    }
    let app = Router::new()
        // API routes
        .route("/api/configs", get(routes::list_configs))
        .route("/api/configs/{*filename}", get(routes::read_config))
        .route("/api/configs/{*filename}", post(routes::write_config))
        .route("/api/containers", get(routes::list_containers))
        .route(
            "/api/containers/{id}/details",
            get(routes::get_container_details),
        )
        .route("/api/containers/{id}/start", post(routes::start_container))
        .route("/api/containers/{id}/stop", post(routes::stop_container))
        .route(
            "/api/containers/{id}/restart",
            post(routes::restart_container),
        )
        // Pass config as state
        .with_state(app_config)
        // Static files (frontend)
        .fallback_service(ServeDir::new("frontend/dist"));

    if let Some(ref cb) = cookbook {
        log(cb, "success", "Routes registered");
        log(cb, "info", "  GET  /api/configs");
        log(cb, "info", "  GET  /api/configs/{*filename}");
        log(cb, "info", "  POST /api/configs/{*filename}");
        log(cb, "info", "  GET  /api/containers");
        log(cb, "info", "  POST /api/containers/{id}/start");
        log(cb, "info", "  POST /api/containers/{id}/stop");
        log(cb, "info", "  POST /api/containers/{id}/restart");
    }

    // Read server configuration from environment or use defaults
    let server_port = std::env::var("SERVER_PORT").unwrap_or_else(|_| "3000".to_string());
    // Bind to 0.0.0.0 to ensure availability on all interfaces (needed for some setups/IPv6 dual stack)
    let bind_addr = format!("0.0.0.0:{}", server_port);
    let display_addr = format!("http://localhost:{}", server_port);

    if let Some(ref cb) = cookbook {
        log(cb, "info", &format!("Binding to {}", bind_addr));
    }

    let listener = tokio::net::TcpListener::bind(&bind_addr).await.unwrap();

    if let Some(ref cb) = cookbook {
        log(
            cb,
            "success",
            &format!("Server running on {}", display_addr),
        );
        log(cb, "info", "Ready to accept connections");
    } else {
        println!("Server running on {}", display_addr);
    }

    axum::serve(listener, app).await.unwrap();
}
