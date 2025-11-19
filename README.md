# sysrat - codebase

```
sysrat-rs/
├── .github/
│   ├── logs/
│   │   └── 20251119-091325-workflow.log
│   ├── skips/
│   │   └── .skip.update-readme.example
│   └── workflows/
│       ├── scripts/
│       │   ├── ci-lines.sh
│       │   ├── ci-logger.sh
│       │   └── update_readme.py
│       ├── check-skip.yml
│       └── update-readme.yml
├── frontend/
│   ├── assets/
│   │   ├── menu-text.ascii
│   │   └── sysrat.ascii
│   ├── build_helpers/
│   │   ├── theme/
│   │   │   ├── generator.rs
│   │   │   ├── mod.rs
│   │   │   └── scanner.rs
│   │   ├── ascii.rs
│   │   ├── date.rs
│   │   ├── hash.rs
│   │   ├── keybinds.rs
│   │   ├── mod.rs
│   │   ├── statusline.rs
│   │   └── version.rs
│   ├── src/
│   │   ├── api/
│   │   │   ├── configs.rs
│   │   │   ├── containers.rs
│   │   │   ├── mod.rs
│   │   │   └── types.rs
│   │   ├── events/
│   │   │   ├── container_list/
│   │   │   │   ├── actions.rs
│   │   │   │   ├── details.rs
│   │   │   │   ├── mod.rs
│   │   │   │   └── navigation.rs
│   │   │   ├── editor/
│   │   │   │   ├── normal_mode/
│   │   │   │   │   ├── editing.rs
│   │   │   │   │   ├── insert_commands.rs
│   │   │   │   │   ├── mod.rs
│   │   │   │   │   └── navigation.rs
│   │   │   │   ├── input.rs
│   │   │   │   ├── insert_mode.rs
│   │   │   │   └── mod.rs
│   │   │   ├── file_list.rs
│   │   │   ├── menu.rs
│   │   │   └── mod.rs
│   │   ├── keybinds/
│   │   │   ├── help_text.rs
│   │   │   ├── mod.rs
│   │   │   └── types.rs
│   │   ├── state/
│   │   │   ├── refresh/
│   │   │   │   ├── cache.rs
│   │   │   │   ├── container_list.rs
│   │   │   │   ├── file_list.rs
│   │   │   │   └── mod.rs
│   │   │   ├── app.rs
│   │   │   ├── container_list.rs
│   │   │   ├── editor.rs
│   │   │   ├── file_list.rs
│   │   │   ├── menu.rs
│   │   │   ├── mod.rs
│   │   │   ├── pane.rs
│   │   │   └── status_helper.rs
│   │   ├── storage/
│   │   │   ├── generic.rs
│   │   │   ├── local.rs
│   │   │   ├── mod.rs
│   │   │   └── types.rs
│   │   ├── theme/
│   │   │   ├── types/
│   │   │   │   ├── colors.rs
│   │   │   │   ├── config.rs
│   │   │   │   ├── font.rs
│   │   │   │   ├── icons.rs
│   │   │   │   └── mod.rs
│   │   │   ├── builder.rs
│   │   │   ├── container_list.rs
│   │   │   ├── editor.rs
│   │   │   ├── file_list.rs
│   │   │   ├── loader.rs
│   │   │   ├── menu.rs
│   │   │   ├── mod.rs
│   │   │   └── status_line.rs
│   │   ├── ui/
│   │   │   ├── container_details/
│   │   │   │   ├── basic.rs
│   │   │   │   ├── config.rs
│   │   │   │   ├── mod.rs
│   │   │   │   ├── network.rs
│   │   │   │   └── storage.rs
│   │   │   ├── menu/
│   │   │   │   ├── center.rs
│   │   │   │   ├── keybinds.rs
│   │   │   │   ├── mod.rs
│   │   │   │   └── rat_ascii.rs
│   │   │   ├── status_line/
│   │   │   │   ├── components/
│   │   │   │   │   ├── build.rs
│   │   │   │   │   ├── mod.rs
│   │   │   │   │   ├── state.rs
│   │   │   │   │   └── text.rs
│   │   │   │   ├── rendering/
│   │   │   │   │   ├── mod.rs
│   │   │   │   │   └── spacing.rs
│   │   │   │   ├── config.rs
│   │   │   │   └── mod.rs
│   │   │   ├── container_list.rs
│   │   │   ├── editor.rs
│   │   │   ├── file_list.rs
│   │   │   └── mod.rs
│   │   ├── utils/
│   │   │   ├── error.rs
│   │   │   └── mod.rs
│   │   ├── dom.rs
│   │   ├── init.rs
│   │   └── lib.rs
│   ├── themes/
│   │   ├── cyberpunk.toml
│   │   ├── dracula.toml
│   │   ├── frappe.toml
│   │   ├── gruvbox-dark.toml
│   │   ├── gruvbox-light.toml
│   │   ├── latte.toml
│   │   ├── macchiato.toml
│   │   ├── mocha.toml
│   │   └── synthwave.toml
│   ├── build.rs
│   ├── Cargo.toml
│   ├── index.html
│   └── keybinds.toml
├── server/
│   ├── src/
│   │   ├── config/
│   │   │   ├── app_config.rs
│   │   │   ├── mod.rs
│   │   │   ├── models.rs
│   │   │   └── scanner.rs
│   │   ├── routes/
│   │   │   ├── configs/
│   │   │   │   ├── handlers.rs
│   │   │   │   ├── mod.rs
│   │   │   │   └── validation.rs
│   │   │   ├── containers/
│   │   │   │   ├── parser/
│   │   │   │   │   ├── basic.rs
│   │   │   │   │   ├── config.rs
│   │   │   │   │   ├── mod.rs
│   │   │   │   │   ├── network.rs
│   │   │   │   │   └── storage.rs
│   │   │   │   ├── actions.rs
│   │   │   │   ├── details.rs
│   │   │   │   ├── handlers.rs
│   │   │   │   └── mod.rs
│   │   │   ├── mod.rs
│   │   │   └── types.rs
│   │   ├── main.rs
│   │   └── version.rs
│   └── Cargo.toml
├── sys/
│   ├── env/
│   │   └── .env.example
│   ├── html/
│   │   ├── htmlformat.py
│   │   └── htmllint.py
│   ├── layout/
│   │   └── statusline.toml
│   ├── rust/
│   │   ├── audit.py
│   │   ├── check.py
│   │   ├── clean.py
│   │   ├── clippy.py
│   │   ├── debug.py
│   │   ├── rustfmt.py
│   │   └── test_rust.py
│   ├── theme/
│   │   ├── theme.py
│   │   └── theme.toml
│   └── utils/
│       ├── cleanup_backups.py
│       ├── fix_nerdfonts.py
│       ├── lines.py
│       ├── pyclean.py
│       ├── pycompile.py
│       ├── pylint.py
│       ├── remove_emojis.py
│       ├── venv.py
│       └── xdg_paths.py
├── Cargo.lock
├── Cargo.toml
├── CLAUDE.md
├── DEBUG.md
├── deny.toml
├── justfile
├── README.md
├── rebuild.py
├── start.py
├── status.py
├── stop.py
└── sysrat.toml
```
