#!/usr/bin/env python3
"""
Nerd Font Icon Fixer for Shell Scripts
Replaces empty icon strings with correct Nerd Font Unicode characters
"""

import sys
import re
from pathlib import Path

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

# Import central theme
from theme import Colors, Icons, log_success, log_error, log_warn, log_info


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from sys/env/.env.dev file"""
    env_file = repo_root / 'sys' / 'env' / '.env.dev'

    if not env_file.exists():
        raise FileNotFoundError(
            f"Development configuration file not found: {env_file}\n"
            f"Create sys/env/.env.dev for development tool configuration."
        )

    config = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip('"').strip("'")
                config[key] = value

    return config


# Nerd Font Icon mappings (Unicode codepoints)
NERD_FONTS = {
    'CHECK': Icons.CHECK,
    'CROSS': Icons.CROSS,
    'WARN': Icons.WARN,
    'INFO': Icons.INFO,
    'SERVER': Icons.SERVER,
    'DOCKER': Icons.DOCKER,
    'CONTAINER': Icons.CONTAINER,
    'CHART': Icons.CHART,
    'CLOCK': Icons.CLOCK,
    'MEM': Icons.MEM,
    'CPU': Icons.CPU,
    'NET': Icons.NET,
    'LOG': Icons.LOG,
    'FILE': Icons.FILE,
    'DATABASE': Icons.DATABASE,
    'PLAY': Icons.PLAY,
    'STOP': Icons.STOP,
    'RESTART': Icons.RESTART,
    'STATUS': Icons.STATUS,
}

def get_patterns_for_filetype(filepath: Path, icon_name: str) -> list:
    """
    Get appropriate regex patterns based on file extension

    Args:
        filepath: Path to the file
        icon_name: Name of the icon (e.g., 'CHECK', 'WARN')

    Returns:
        List of (pattern, description) tuples to try in order
    """
    suffix = filepath.suffix.lower()
    patterns = []

    if suffix == '.sh':
        # Shell scripts: readonly ICON=""
        patterns.append((
            rf'(readonly\s+{icon_name}=)""\s*$',
            'shell readonly'
        ))
    elif suffix in ['.yml', '.yaml']:
        # YAML files: ICON="" (no readonly, used in GitHub Actions)
        patterns.append((
            rf'(\s+{icon_name}=)""\s*$',
            'yaml assignment'
        ))
    elif suffix == '.py':
        # Python: ICON = "" (with spaces around =)
        patterns.append((
            rf'({icon_name}\s*=\s*)""\s*$',
            'python assignment'
        ))
    elif suffix == '.md':
        # Markdown: Could have various patterns
        # - Code blocks with readonly ICON=""
        # - Inline code `ICON=""`
        patterns.append((
            rf'(readonly\s+{icon_name}=)""\s*$',
            'markdown shell code'
        ))
        patterns.append((
            rf'(`{icon_name}=)""`',
            'markdown inline code'
        ))
    else:
        # Generic: try common patterns
        patterns.append((
            rf'(readonly\s+{icon_name}=)""\s*$',
            'generic readonly'
        ))
        patterns.append((
            rf'({icon_name}=)""\s*$',
            'generic assignment'
        ))

    return patterns

def fix_icons_in_file(filepath: Path, dry_run: bool = False) -> bool:
    """
    Fix Nerd Font icons in a file based on file type

    Args:
        filepath: Path to the file
        dry_run: If True, only show what would be changed

    Returns:
        True if changes were made, False otherwise
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        changes_made = False

        # Pattern to match: readonly ICON_NAME=""
        # We'll replace the empty string with the actual icon
        for icon_name, icon_char in NERD_FONTS.items():
            # Match patterns like: readonly CHECK=""
            # Updated patterns to handle variable whitespace around =
            # Pattern 1: With readonly (shell scripts)
            pattern1 = rf'(readonly\s+{icon_name})\s*=\s*""\s*$'
            # Pattern 2: Without readonly (YAML, other formats)
            pattern2 = rf'({icon_name})\s*=\s*""\s*$'
            # Replacement with normalized spacing (no spaces around =)
            replacement = rf'\1="{icon_char}"'

            # Try pattern 1 first (with readonly)
            new_content = re.sub(pattern1, replacement, content, flags=re.MULTILINE)

            # If no changes, try pattern 2 (without readonly)
            if new_content == content:
                new_content = re.sub(pattern2, replacement, content, flags=re.MULTILINE)

            if new_content != content:
                changes_made = True
                if not dry_run:
                    log_success(f"Fixed {icon_name} in {filepath.name}")
                else:
                    log_warn(f"Would fix {icon_name} in {filepath.name}")
                content = new_content

        # Normalize whitespace after icon fixes
        if changes_made:
            lines = content.split('\n')
            normalized_lines = []

            for line in lines:
                # Preserve leading whitespace (indentation)
                leading_ws = ''
                stripped = line.lstrip()
                if stripped != line:
                    leading_ws = line[:len(line) - len(stripped)]

                # Normalize multiple spaces to single space in content
                # But preserve spaces inside quoted strings
                if '"' not in stripped and "'" not in stripped:
                    # No quotes - safe to normalize
                    normalized = re.sub(r' {2,}', ' ', stripped)
                else:
                    # Has quotes - only normalize outside of quoted regions
                    # Simple approach: don't normalize to avoid breaking strings
                    normalized = stripped

                normalized_lines.append(leading_ws + normalized)

            content = '\n'.join(normalized_lines)

        if changes_made and not dry_run:
            filepath.write_text(content, encoding='utf-8')
            return True

        return changes_made

    except Exception as e:
        log_error(f"Error processing {filepath}: {e}")
        return False


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fix Nerd Font icons in shell scripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Fix all .sh files in current directory
  python3 fix_nerdfonts.py

  # Fix multiple file types
  python3 fix_nerdfonts.py --types sh md py

  # Fix files in a specific directory
  python3 fix_nerdfonts.py --path /path/to/scripts

  # Fix files recursively
  python3 fix_nerdfonts.py --recursive --path /path/to/scripts

  # Preview changes without modifying files
  python3 fix_nerdfonts.py --dry-run

  # Fix a specific file
  python3 fix_nerdfonts.py --path /path/to/script.sh
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to file or directory to process (default: current directory)'
    )

    parser.add_argument(
        '-t', '--types',
        nargs='+',
        default=['sh'],
        help='File extensions to process (default: sh)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    args = parser.parse_args()

    # Determine base path
    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    # Determine which files to process
    files = []

    if base_path.is_file():
        files.append(base_path)
    elif base_path.is_dir():
        for ext in args.types:
            ext = ext.lstrip('*.')
            pattern = f'**/*.{ext}' if args.recursive else f'*.{ext}'
            files.extend(base_path.glob(pattern))
    else:
        log_error(f"Invalid path: {base_path}")
        return 1

    if not files:
        log_error(f"No files found matching types: {', '.join(args.types)}")
        return 1

    # Header
    tag = f"{Colors.MAUVE}[fix-nerdfonts]{Colors.NC}"
    mode = "Preview mode" if args.dry_run else "Fixing Nerd Font icons"
    print(f"\n{tag} {mode}...\n")

    log_info(f"Processing {len(files)} file(s)")
    if args.dry_run:
        log_warn("DRY RUN - No files will be modified")
    print()

    total_files = 0
    fixed_files = 0

    for filepath in sorted(files):
        if not filepath.exists():
            log_error(f"File not found: {filepath}")
            continue

        if not filepath.is_file():
            log_error(f"Not a file: {filepath}")
            continue

        total_files += 1

        if fix_icons_in_file(filepath, dry_run=args.dry_run):
            fixed_files += 1
        else:
            print(f"  {Colors.TEXT}{filepath.name}{Colors.NC} {Colors.SUBTEXT}(no changes needed){Colors.NC}")

    # Summary
    print(f"\n{Colors.GREEN}summary:{Colors.NC}\n")
    print(f"{Colors.BLUE}  Total files:     {Colors.NC}{total_files}")
    print(f"{Colors.GREEN}  Files fixed:     {Colors.NC}{fixed_files}")
    print(f"{Colors.TEXT}  No changes:      {Colors.NC}{total_files - fixed_files}")
    print()

    if fixed_files > 0:
        if args.dry_run:
            log_warn("Run without --dry-run to apply changes")
        else:
            log_success("Nerd Font icon fix complete!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
