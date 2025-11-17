#!/usr/bin/env python3
"""
README Generator for SysRat - Lists user-facing files and directories
"""

import sys
from pathlib import Path

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # Go up 3 levels: scripts/ -> workflows/ -> .github/ -> repo root
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

# Import central theme
from theme import Colors, Icons, log_success


def get_project_files() -> dict:
    """Get relevant project files organized by category."""

    # User-facing management scripts
    management_scripts = []
    for script in ['start.py', 'stop.py', 'status.py', 'rebuild.py']:
        script_path = REPO_ROOT / script
        if script_path.exists():
            management_scripts.append(script)

    # Configuration files
    config_files = []
    for config in ['sysrat.toml', 'sys/env/.env.example', 'justfile', 'CLAUDE.md']:
        config_path = REPO_ROOT / config
        if config_path.exists():
            config_files.append(config)

    # Project directories (just mention them, don't scan contents)
    project_dirs = []
    for directory in ['server', 'frontend']:
        dir_path = REPO_ROOT / directory
        if dir_path.exists() and dir_path.is_dir():
            project_dirs.append(directory)

    return {
        'management_scripts': sorted(management_scripts),
        'config_files': sorted(config_files),
        'project_dirs': sorted(project_dirs)
    }


def get_description(filename: str) -> str:
    """Get description for a file."""
    descriptions = {
        # Management scripts
        'start.py': 'Start the SysRat server',
        'stop.py': 'Stop the SysRat server',
        'status.py': 'Check server status and stats',
        'rebuild.py': 'Build and deploy (backend + frontend)',

        # Config files
        'sysrat.toml': 'Application configuration',
        'sys/env/.env.example': 'Environment configuration template',
        'justfile': 'Task runner commands',
        'CLAUDE.md': 'Developer documentation and AI assistant guide',

        # Directories
        'server': 'Backend API server (Rust + Axum)',
        'frontend': 'WASM-based TUI frontend (Ratzilla)',
    }

    return descriptions.get(filename, '')


def generate_readme(files: dict) -> str:
    """Generate README with file links organized by category."""

    readme = "# SysRat\n\n"
    readme += "**SysRat** is a full-stack web-based configuration management system written in Rust.\n\n"
    readme += "- **Backend**: Rust + Axum (async web framework)\n"
    readme += "- **Frontend**: WASM + Ratzilla (terminal UI in the browser)\n"
    readme += "- **Features**: Configuration file management, Docker container management\n\n"

    # Management Scripts
    if files['management_scripts']:
        readme += "## Management Scripts\n\n"
        for script in files['management_scripts']:
            desc = get_description(script)
            readme += f"- [{script}]({script})"
            if desc:
                readme += f" - {desc}"
            readme += "\n"
        readme += "\n"

    # Configuration Files
    if files['config_files']:
        readme += "## Configuration\n\n"
        for config in files['config_files']:
            desc = get_description(config)
            readme += f"- [{config}]({config})"
            if desc:
                readme += f" - {desc}"
            readme += "\n"
        readme += "\n"

    # Project Structure
    if files['project_dirs']:
        readme += "## Project Structure\n\n"
        for directory in files['project_dirs']:
            desc = get_description(directory)
            readme += f"- `{directory}/`"
            if desc:
                readme += f" - {desc}"
            readme += "\n"
        readme += "\n"

    # Quick Start
    readme += "## Quick Start\n\n"
    readme += "```bash\n"
    readme += "# Build and start server\n"
    readme += "./rebuild.py\n\n"
    readme += "# Check status\n"
    readme += "./status.py\n\n"
    readme += "# Stop server\n"
    readme += "./stop.py\n"
    readme += "```\n\n"

    # Access
    readme += "## Access\n\n"
    readme += "Once started, access the web interface at: **http://localhost:3000**\n\n"

    # Documentation
    readme += "## Documentation\n\n"
    readme += "See [CLAUDE.md](CLAUDE.md) for comprehensive developer documentation.\n"

    return readme


def main():
    """Main function."""
    files = get_project_files()
    readme_content = generate_readme(files)

    # Write README
    readme_path = REPO_ROOT / 'README.md'

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    # Count total items
    total_items = (len(files['management_scripts']) +
                   len(files['config_files']) +
                   len(files['project_dirs']))

    log_success(f"README.md updated with {total_items} items")


if __name__ == '__main__':
    main()
