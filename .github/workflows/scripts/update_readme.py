#!/usr/bin/env python3
"""
README Generator for SysRat - Lists user-facing files and directories
"""

import sys
import tomllib
import subprocess
from datetime import datetime
from pathlib import Path

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # Go up 3 levels: scripts/ -> workflows/ -> .github/ -> repo root
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

# Import central theme
from theme import Colors, Icons, log_success


def get_git_info() -> dict:
    """Get git hash and build date."""
    info = {}

    # Get current git hash (short)
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        info['hash'] = result.stdout.strip()
    except Exception:
        info['hash'] = 'unknown'

    # Get current date
    info['date'] = datetime.now().strftime('%Y-%m-%d')

    return info


def extract_versions() -> dict:
    """Extract dependency versions from Cargo.toml files."""
    versions = {}

    # Read workspace Cargo.toml for edition
    workspace_toml = REPO_ROOT / 'Cargo.toml'
    if workspace_toml.exists():
        try:
            with open(workspace_toml, 'rb') as f:
                data = tomllib.load(f)
            if 'workspace' in data and 'package' in data['workspace']:
                edition = data['workspace']['package'].get('edition', 'unknown')
                versions['edition'] = edition
        except Exception:
            versions['edition'] = 'unknown'

    # Read server Cargo.toml for Axum version
    server_toml = REPO_ROOT / 'server' / 'Cargo.toml'
    if server_toml.exists():
        try:
            with open(server_toml, 'rb') as f:
                data = tomllib.load(f)
            if 'dependencies' in data:
                axum = data['dependencies'].get('axum', 'unknown')
                if isinstance(axum, dict):
                    axum = axum.get('version', 'unknown')
                versions['axum'] = axum
        except Exception:
            versions['axum'] = 'unknown'

    # Read frontend Cargo.toml for Ratzilla and Ratatui versions
    frontend_toml = REPO_ROOT / 'frontend' / 'Cargo.toml'
    if frontend_toml.exists():
        try:
            with open(frontend_toml, 'rb') as f:
                data = tomllib.load(f)
            if 'dependencies' in data:
                # Ratzilla
                ratzilla = data['dependencies'].get('ratzilla', 'unknown')
                if isinstance(ratzilla, dict):
                    ratzilla = ratzilla.get('version', 'unknown')
                versions['ratzilla'] = ratzilla

                # Ratatui (via tui-textarea dependency)
                # We get ratatui version indirectly, or hardcode known version
                # For simplicity, we'll note it's via ratzilla
                versions['ratatui'] = 'via ratzilla'
        except Exception:
            versions['ratzilla'] = 'unknown'
            versions['ratatui'] = 'unknown'

    return versions


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


def generate_readme(files: dict, versions: dict, git_info: dict) -> str:
    """Generate README with file links organized by category."""

    # Nerd Font Icons (matching theme.py)
    ROCKET = ''
    SERVER = '󰒋'
    HAMMER = ''
    FOLDER = ''
    FILE = ''
    CHART = '󰈙'
    INFO = ''

    readme = "# SysRat\n\n"
    readme += "**SysRat** is a full-stack web-based configuration management system written in Rust.\n\n"
    readme += f"- **Backend**: {SERVER} Rust + Axum (async web framework)\n"
    readme += f"- **Frontend**: {CHART} WASM + Ratzilla (terminal UI in the browser)\n"
    readme += f"- **Features**: Configuration file management, Docker container management\n\n"

    # Build info
    build_date = git_info.get('date', 'unknown')
    build_hash = git_info.get('hash', 'unknown')
    readme += f"[build] {INFO}  **Last Updated**: {build_date} (`{build_hash}`)\n\n"

    # Tech Stack with versions
    readme += f"## {HAMMER} Tech Stack\n\n"
    edition = versions.get('edition', 'unknown')
    axum = versions.get('axum', 'unknown')
    ratzilla = versions.get('ratzilla', 'unknown')

    readme += f"**Rust Edition {edition}**\n\n"
    readme += f"- **Backend**: {SERVER} Axum v{axum}\n"
    readme += f"- **Frontend**: {CHART} Ratzilla v{ratzilla} (Ratatui-based WASM TUI)\n"
    readme += f"- **Build**: {HAMMER} Trunk (WASM bundler), Cargo (Rust toolchain)\n\n"

    # Management Scripts
    if files['management_scripts']:
        readme += f"## {ROCKET} Management Scripts\n\n"
        for script in files['management_scripts']:
            desc = get_description(script)
            readme += f"- {FILE} [{script}]({script})"
            if desc:
                readme += f" - {desc}"
            readme += "\n"
        readme += "\n"

    # Configuration Files
    if files['config_files']:
        readme += f"## {FILE} Configuration\n\n"
        for config in files['config_files']:
            desc = get_description(config)
            readme += f"- {FILE} [{config}]({config})"
            if desc:
                readme += f" - {desc}"
            readme += "\n"
        readme += "\n"

    # Project Structure
    if files['project_dirs']:
        readme += f"## {FOLDER} Project Structure\n\n"
        for directory in files['project_dirs']:
            desc = get_description(directory)
            readme += f"- {FOLDER} `{directory}/`"
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
    git_info = get_git_info()
    versions = extract_versions()
    files = get_project_files()
    readme_content = generate_readme(files, versions, git_info)

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
