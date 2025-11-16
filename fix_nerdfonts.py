#!/usr/bin/env python3
"""
Nerd Font Icon Fixer for Shell Scripts
Replaces empty icon strings with correct Nerd Font Unicode characters
"""

import sys
import re
from pathlib import Path

# Catppuccin Mocha color palette (24-bit true color)
class Colors:
    RED = '\033[38;2;243;139;168m'        # #f38ba8 - Errors
    GREEN = '\033[38;2;166;227;161m'      # #a6e3a1 - Success
    YELLOW = '\033[38;2;249;226;175m'     # #f9e2af - Warnings
    BLUE = '\033[38;2;137;180;250m'       # #89b4fa - Info
    MAUVE = '\033[38;2;203;166;247m'      # #cba6f7 - Headers
    SAPPHIRE = '\033[38;2;116;199;236m'   # #74c7ec - Success highlights
    TEXT = '\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
    SUBTEXT = '\033[38;2;186;194;222m'    # #bac2de - Subtext
    NC = '\033[0m'                         # No Color

# Nerd Font Icons
CHECK = '\uf00c'   #
CROSS = '\uf00d'   #
WARN = '\uf071'    #
INFO = '\uf05a'    #

# Nerd Font Icon mappings (Unicode codepoints)
NERD_FONTS = {
    'CHECK': '\uf00c',      #
    'CROSS': '\uf00d',      #
    'WARN': '\uf071',       #
    'INFO': '\uf05a',       #
    'SERVER': '\uf233',     # 󰒋
    'CHART': '\uf200',      # 󰈙
    'CLOCK': '\uf64f',      # 󰥔
    'MEM': '\uf538',        # 󰍛
    'CPU': '\uf2db',        # 󰻠
    'NET': '\uf6ff',        # 󰈀
    'LOG': '\uf15c',        #
    'FILE': '\uf15b',       #
}

def log_success(msg: str):
    """Log success message with icon"""
    print(f"{Colors.GREEN}{CHECK}  {Colors.NC}{msg}")

def log_error(msg: str):
    """Log error message with icon"""
    print(f"{Colors.RED}{CROSS}  {Colors.NC}{msg}", file=sys.stderr)

def log_warn(msg: str):
    """Log warning message with icon"""
    print(f"{Colors.YELLOW}{WARN}  {Colors.NC}{msg}")

def log_info(msg: str):
    """Log info message with icon"""
    print(f"{Colors.BLUE}{INFO}  {Colors.NC}{msg}")

def fix_icons_in_file(filepath: Path, dry_run: bool = False) -> bool:
    """
    Fix Nerd Font icons in a shell script file

    Args:
        filepath: Path to the shell script
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
            # Match patterns like: readonly CHECK=""
            pattern = rf'(readonly\s+{icon_name}=)""\s*$'
            replacement = rf'\1"{icon_char}"'

            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            if new_content != content:
                changes_made = True
                if not dry_run:
                    log_success(f"Fixed {icon_name} in {filepath.name}")
                else:
                    log_warn(f"Would fix {icon_name} in {filepath.name}")
                content = new_content

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

  # Dry run to see what would be changed
  python3 fix_nerdfonts.py --dry-run

  # Fix specific file
  python3 fix_nerdfonts.py status.sh
        '''
    )

    parser.add_argument(
        'files',
        nargs='*',
        help='Shell script files to fix (default: all *.sh in current directory)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )

    args = parser.parse_args()

    # Determine which files to process
    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = list(Path('.').glob('*.sh'))

    if not files:
        log_error("No shell script files found!")
        return 1

    # Header
    tag = f"{Colors.MAUVE}[fix-nerdfonts]{Colors.NC}"
    if args.dry_run:
        print(f"{tag} {Colors.YELLOW}DRY RUN:{Colors.NC} Checking Nerd Font icons...")
    else:
        print(f"{tag} Fixing Nerd Font icons...")
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
        print(f"{Colors.BLUE}Processing{Colors.NC} {filepath.name}...")

        if fix_icons_in_file(filepath, dry_run=args.dry_run):
            fixed_files += 1
        else:
            log_info(f"No changes needed for {filepath.name}")

        print()

    # Summary
    print(f"{Colors.GREEN}Summary:{Colors.NC}")
    print()
    print(f"{Colors.BLUE}  Total files:     {Colors.NC}{total_files}")
    print(f"{Colors.GREEN}  Files fixed:     {Colors.NC}{fixed_files}")

    if args.dry_run and fixed_files > 0:
        print()
        log_info(f"Run without {Colors.BLUE}--dry-run{Colors.NC} to apply changes")

    return 0


if __name__ == '__main__':
    sys.exit(main())
