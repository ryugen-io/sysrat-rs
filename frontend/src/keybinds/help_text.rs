use super::types::*;

impl MenuKeybinds {
    pub fn help_text(&self, global: &GlobalKeybinds) -> String {
        format!(
            "{},{}/{},{}:navigate {}:select {}:theme",
            self.navigate_down,
            self.navigate_down_alt,
            self.navigate_up,
            self.navigate_up_alt,
            self.select,
            global.cycle_theme
        )
    }
}

impl FileListKeybinds {
    pub fn help_text(&self, _global: &GlobalKeybinds) -> String {
        format!(
            "{},{}/{},{}:navigate {}:load {}:menu {}:editor",
            self.navigate_down,
            self.navigate_down_alt,
            self.navigate_up,
            self.navigate_up_alt,
            self.select,
            self.back_to_menu,
            self.go_to_editor
        )
    }
}

impl ContainerListKeybinds {
    pub fn help_text(&self, _global: &GlobalKeybinds) -> String {
        format!(
            "{},{}/{},{}:navigate {}:start {}:stop {}:restart {}:menu",
            self.navigate_down,
            self.navigate_down_alt,
            self.navigate_up,
            self.navigate_up_alt,
            self.start_container,
            self.stop_container,
            self.restart_container,
            self.back_to_menu
        )
    }
}

impl GlobalKeybinds {
    pub fn editor_normal_help_text(&self) -> String {
        format!("i:insert {}:save {}:files", self.save, self.back_to_files)
    }

    pub fn editor_insert_help_text(&self) -> String {
        format!("ESC:normal {}:save", self.save)
    }
}
