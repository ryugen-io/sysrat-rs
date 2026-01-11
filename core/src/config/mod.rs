mod app_config;
mod models;
mod scanner;

pub use app_config::AppConfig;
pub use models::{Config, ConfigDirectory, ConfigFile};

use std::sync::Arc;
use tokio::sync::RwLock;

/// Shared application state
pub type SharedConfig = Arc<RwLock<AppConfig>>;
