#!/usr/bin/env python3
"""
README Generator for sysrat - Generates a tree view of the codebase
"""

import sys
from pathlib import Path

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # Go up 3 levels: scripts/ -> workflows/ -> .github/ -> repo root
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

# Import central theme
from theme import log_success


# Directories and files to ignore
IGNORE_DIRS = {
    '.git', 'target', 'node_modules', 'dist', '__pycache__',
    '.mypy_cache', '.pytest_cache', '.ruff_cache', '.trunk',
    '.venv', 'venv', '.idea', '.vscode', '.cache'
}

IGNORE_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitkeep', '*.pyc', '*.pyo',
    '*.swp', '*.swo', '*~', '.server.pid', 'server.log',
    '.gitignore', '.env', '.env.dev'
}

# File extensions to show (empty = show all)
SHOW_EXTENSIONS = set()  # Empty means show all files


def should_ignore(path: Path) -> bool:
    """Check if a path should be ignored."""
    # Ignore directories
    if path.is_dir() and path.name in IGNORE_DIRS:
        return True

    # Ignore backup files
    if path.name.endswith('.backup') or '.backup-' in path.name:
        return True

    # Ignore specific files
    if path.name in IGNORE_FILES:
        return True

    # Ignore pattern matching (e.g., *.pyc)
    for pattern in IGNORE_FILES:
        if '*' in pattern:
            ext = pattern.replace('*', '')
            if path.name.endswith(ext):
                return True

    return False


def generate_tree(directory: Path, prefix: str = "", is_last: bool = True, max_depth: int = -1, current_depth: int = 0) -> list:
    """
    Generate a tree structure for a directory.

    Args:
        directory: Path to directory to scan
        prefix: Current line prefix for indentation
        is_last: Whether this is the last item in current level
        max_depth: Maximum depth to recurse (-1 for unlimited)
        current_depth: Current recursion depth

    Returns:
        List of formatted tree lines
    """
    lines = []

    # Check depth limit
    if max_depth != -1 and current_depth >= max_depth:
        return lines

    # Get all items in directory
    try:
        items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return lines

    # Filter out ignored items
    items = [item for item in items if not should_ignore(item)]

    for index, item in enumerate(items):
        is_last_item = index == len(items) - 1

        # Choose the right box-drawing characters
        if is_last_item:
            current_prefix = "└── "
            extension = "    "
        else:
            current_prefix = "├── "
            extension = "│   "

        # Format item name
        if item.is_dir():
            item_name = f"{item.name}/"
        else:
            item_name = item.name

        # Add line
        lines.append(f"{prefix}{current_prefix}{item_name}")

        # Recurse into directories
        if item.is_dir():
            lines.extend(generate_tree(
                item,
                prefix + extension,
                is_last_item,
                max_depth,
                current_depth + 1
            ))

    return lines


def generate_readme() -> str:
    """Generate README with tree view of codebase."""
    readme = "# sysrat - codebase\n\n"
    readme += "```\n"
    readme += "sysrat-rs/\n"

    # Generate tree (no depth limit)
    tree_lines = generate_tree(REPO_ROOT, max_depth=-1)
    readme += "\n".join(tree_lines)

    readme += "\n```\n"

    return readme


def main():
    """Main function."""
    readme_content = generate_readme()

    # Write README
    readme_path = REPO_ROOT / 'README.md'

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    # Count total lines
    total_lines = readme_content.count('\n')

    log_success(f"README.md updated with tree view ({total_lines} lines)")


if __name__ == '__main__':
    main()
