use super::models::{Config, ConfigFile};
use super::scanner::scan_directory;
use k_lib::config::Cookbook;
use k_lib::logger;
use std::collections::HashMap;

const SCOPE: &str = "CONFIG";
const APP_NAME: &str = "sysrat";

fn log(cookbook: &Cookbook, level: &str, msg: &str) {
    logger::log_to_terminal(cookbook, level, SCOPE, msg);
    let _ = logger::log_to_file(cookbook, level, SCOPE, msg, Some(APP_NAME));
}

/// Global application state holding the configuration
#[derive(Debug, Clone)]
pub struct AppConfig {
    files: Vec<ConfigFile>,
    file_index: HashMap<String, usize>,
    allowed_extensions: Vec<String>,
}

impl AppConfig {
    /// Load configuration from file
    pub fn load() -> Result<Self, String> {
        let cookbook = Cookbook::load().ok();
        let config_path = Self::config_path();

        if let Some(ref cb) = cookbook {
            log(cb, "info", &format!("Reading {}", config_path));
        }

        let content = std::fs::read_to_string(&config_path)
            .map_err(|e| format!("Failed to read config file {}: {}", config_path, e))?;

        let config: Config =
            toml::from_str(&content).map_err(|e| format!("Failed to parse config: {}", e))?;

        if let Some(ref cb) = cookbook {
            log(cb, "success", "Parsed sysrat.toml");
        }

        // Store allowed extensions
        let allowed_extensions = config.settings.allowed_extensions.clone();

        // Keep ordered list plus name-to-index lookup
        let mut files = Vec::new();
        let mut file_index = HashMap::new();

        // Add individual files (no extension validation - config is trusted)
        for file in config.files {
            if let Some(ref cb) = cookbook {
                log(cb, "success", &format!("  [file] {}", file.name));
            }
            Self::insert_file(file, &mut files, &mut file_index);
        }

        // Scan directories and add found files
        for dir_config in config.directories {
            if let Some(ref cb) = cookbook {
                log(cb, "info", &format!("  [scan] {}", dir_config.path));
            }
            match scan_directory(&dir_config) {
                Ok(scanned_files) => {
                    for file in scanned_files {
                        if let Some(ref cb) = cookbook {
                            log(cb, "success", &format!("    {}", file.name));
                        }
                        Self::insert_file(file, &mut files, &mut file_index);
                    }
                }
                Err(e) => {
                    if let Some(ref cb) = cookbook {
                        log(
                            cb,
                            "warn",
                            &format!("Failed to scan {}: {}", dir_config.name, e),
                        );
                    } else {
                        eprintln!(
                            "Warning: Failed to scan directory {}: {}",
                            dir_config.name, e
                        );
                    }
                }
            }
        }

        if let Some(ref cb) = cookbook {
            log(
                cb,
                "success",
                &format!("Loaded {} files total", files.len()),
            );
        }

        Ok(AppConfig {
            files,
            file_index,
            allowed_extensions,
        })
    }

    /// Get ordered list of files as configured by the user
    pub fn files(&self) -> &[ConfigFile] {
        &self.files
    }

    /// Get total file count
    pub fn file_count(&self) -> usize {
        self.files.len()
    }

    /// Get config for a specific file
    pub fn get_file(&self, name: &str) -> Option<&ConfigFile> {
        let idx = self.file_index.get(name)?;
        self.files.get(*idx)
    }

    /// Get allowed file extensions
    pub fn allowed_extensions(&self) -> &[String] {
        &self.allowed_extensions
    }

    /// Get the config file path (XDG-compliant)
    ///
    /// Search order:
    /// 1. SYSRAT_CONFIG env var
    /// 2. XDG_CONFIG_HOME/sysrat/sysrat.toml
    /// 3. ~/.config/sysrat/sysrat.toml
    /// 4. ./sysrat.toml (fallback)
    fn config_path() -> String {
        use std::path::Path;

        // 1. Explicit override via env var
        if let Ok(path) = std::env::var("SYSRAT_CONFIG") {
            return path;
        }

        // 2. XDG_CONFIG_HOME (if set)
        if let Ok(xdg_config) = std::env::var("XDG_CONFIG_HOME") {
            let path = format!("{}/sysrat/sysrat.toml", xdg_config);
            if Path::new(&path).exists() {
                return path;
            }
        }

        // 3. ~/.config/ (XDG default)
        if let Ok(home) = std::env::var("HOME") {
            let path = format!("{}/.config/sysrat/sysrat.toml", home);
            if Path::new(&path).exists() {
                return path;
            }
        }

        // 4. Fallback: current directory
        "sysrat.toml".to_string()
    }

    /// Insert or replace a file while preserving user ordering
    fn insert_file(
        file: ConfigFile,
        files: &mut Vec<ConfigFile>,
        index: &mut HashMap<String, usize>,
    ) {
        if let Some(pos) = index.get(&file.name).cloned() {
            files[pos] = file;
        } else {
            let pos = files.len();
            index.insert(file.name.clone(), pos);
            files.push(file);
        }
    }

    /// Reloads the configuration from disk, updating the current instance
    pub fn refresh(&mut self) -> Result<(), String> {
        let new_config = Self::load()?;
        *self = new_config;
        Ok(())
    }
}
