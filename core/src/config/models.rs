use serde::Deserialize;

#[derive(Debug, Clone, Deserialize, Default)]
pub struct Settings {
    #[serde(default = "default_allowed_extensions")]
    pub allowed_extensions: Vec<String>,
}

fn default_allowed_extensions() -> Vec<String> {
    // Fallback if not specified in config (basic config file types)
    ["conf", "toml", "txt", "ini", "env"]
        .iter()
        .map(|s| s.to_string())
        .collect()
}

#[derive(Debug, Clone, Deserialize)]
pub struct ConfigFile {
    pub path: String,
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub readonly: bool,
    /// Optional category label used for grouping/sorting in the UI
    #[serde(default)]
    pub category: Option<String>,
    /// Optional theme variant name for this file (e.g., "mocha", "latte", "frappe")
    /// If not specified, the default theme is used
    #[serde(default)]
    pub theme: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ConfigDirectory {
    pub path: String,
    pub name: String,
    #[serde(default = "default_depth")]
    pub depth: usize,
    #[serde(default)]
    pub types: Vec<String>,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub readonly: bool,
    /// Optional category label applied to all files found in this directory
    #[serde(default)]
    pub category: Option<String>,
}

fn default_depth() -> usize {
    3
}

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    #[serde(default)]
    pub settings: Settings,
    #[serde(default)]
    pub files: Vec<ConfigFile>,
    #[serde(default)]
    pub directories: Vec<ConfigDirectory>,
}
