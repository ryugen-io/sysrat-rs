use serde::{Deserialize, Serialize};

#[derive(Serialize, Clone)]
pub struct FileInfo {
    pub name: String,
    pub description: String,
    pub readonly: bool,
    /// Optional theme variant for this file
    #[serde(skip_serializing_if = "Option::is_none")]
    pub theme: Option<String>,
    /// Optional category label used for grouping/sorting in the UI
    #[serde(skip_serializing_if = "Option::is_none")]
    pub category: Option<String>,
}

#[derive(Serialize)]
pub struct FileListResponse {
    pub files: Vec<FileInfo>,
}

#[derive(Serialize)]
pub struct FileContentResponse {
    pub content: String,
}

#[derive(Deserialize)]
pub struct WriteConfigRequest {
    pub content: String,
}

#[derive(Serialize)]
pub struct WriteConfigResponse {
    pub success: bool,
}

#[derive(Serialize, Clone)]
pub struct ContainerInfo {
    pub id: String,
    pub name: String,
    pub state: String,
    pub status: String,
}

#[derive(Serialize)]
pub struct ContainerListResponse {
    pub containers: Vec<ContainerInfo>,
}

#[derive(Serialize)]
pub struct ContainerActionResponse {
    pub success: bool,
    pub message: String,
}

#[derive(Serialize, Clone)]
pub struct PortMapping {
    pub container_port: String,
    pub host_port: String,
    pub protocol: String,
}

#[derive(Serialize, Clone)]
pub struct VolumeMount {
    pub source: String,
    pub destination: String,
    pub mode: String,
}

#[derive(Serialize, Clone)]
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

#[derive(Serialize)]
pub struct ContainerDetailsResponse {
    pub details: ContainerDetails,
}
