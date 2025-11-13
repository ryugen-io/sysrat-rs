use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize, Clone, PartialEq)]
pub struct FileInfo {
    pub name: String,
    pub description: String,
    pub readonly: bool,
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
