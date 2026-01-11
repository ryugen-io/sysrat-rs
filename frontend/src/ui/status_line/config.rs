use crate::state::Pane;
use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct StatusLineConfig {
    pub menu: PaneConfig,
    pub file_list: PaneConfig,
    pub editor: PaneConfig,
    pub container_list: PaneConfig,
}

#[derive(Debug, Clone, Deserialize)]
pub struct PaneConfig {
    pub rows: Vec<RowConfig>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct RowConfig {
    pub components: Vec<ComponentConfig>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum ComponentConfig {
    Spacer,
    VimMode,
    Filename,
    ModifiedIndicator,
    StatusMessage,
    HelpText,
    BuildDate {
        #[serde(default)]
        style: Option<String>,
    },
    BuildHash {
        #[serde(default)]
        style: Option<String>,
    },
    RustVersion {
        #[serde(default)]
        style: Option<String>,
    },
    RustEdition {
        #[serde(default)]
        style: Option<String>,
    },
    Dependency {
        name: String,
        #[serde(default)]
        style: Option<String>,
    },
    Text {
        value: String,
        #[serde(default)]
        style: Option<String>,
    },
    Separator {
        value: String,
    },
}

impl StatusLineConfig {
    pub fn get_pane_config(&self, pane: &Pane) -> &PaneConfig {
        match pane {
            Pane::Menu => &self.menu,
            Pane::FileList => &self.file_list,
            Pane::Editor => &self.editor,
            Pane::ContainerList => &self.container_list,
            Pane::Splash => &self.menu, // Splash uses same status line as Menu
        }
    }
}
