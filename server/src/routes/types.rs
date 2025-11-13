use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct FileListResponse {
    pub files: Vec<String>,
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
