use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize, Clone, PartialEq)]
pub struct FileInfo {
    pub name: String,
    pub description: String,
    pub readonly: bool,
    /// Optional theme variant for this file
    #[serde(default)]
    pub theme: Option<String>,
    /// Optional category label used for grouping/sorting in the UI
    #[serde(default)]
    pub category: Option<String>,
}

#[derive(Deserialize)]
pub(super) struct FileListResponse {
    pub files: Vec<FileInfo>,
}

#[derive(Deserialize)]
pub(super) struct FileContentResponse {
    pub content: String,
}

#[derive(Serialize)]
pub(super) struct WriteConfigRequest {
    pub content: String,
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub struct ContainerInfo {
    pub id: String,
    pub name: String,
    pub state: String,
    pub status: String,
}

#[derive(Deserialize)]
pub(super) struct ContainerListResponse {
    pub containers: Vec<ContainerInfo>,
}

#[derive(Deserialize)]
pub(super) struct ContainerActionResponse {
    pub success: bool,
    pub message: String,
}

#[derive(Deserialize, Clone)]
pub struct PortMapping {
    pub container_port: String,
    pub host_port: String,
    pub protocol: String,
}

#[derive(Deserialize, Clone)]
pub struct VolumeMount {
    pub source: String,
    pub destination: String,
    pub mode: String,
}

#[derive(Deserialize, Clone)]
pub struct ContainerDetails {
    pub id: String,
    pub name: String,
    pub image: String,
    pub state: String,
    pub status: String,
    pub created: String,
    pub started: String,
    pub ports: Vec<PortMapping>,
    pub volumes: Vec<VolumeMount>,
    pub networks: Vec<String>,
    pub environment: Vec<String>,
    pub restart_policy: String,
    pub health: Option<String>,
}

#[derive(Deserialize)]
pub(super) struct ContainerDetailsResponse {
    pub details: ContainerDetails,
}
