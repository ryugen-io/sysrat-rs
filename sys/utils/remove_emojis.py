#!/usr/bin/env python3
"""
Remove Unicode Emojis from Files
Removes Unicode emoji characters while preserving Nerd Font icons
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

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


# Use central theme icons
CLEAN = Icons.CLEAN


def remove_emojis(text: str) -> str:
    """
    Remove Unicode emojis while preserving Nerd Font icons

    Nerd Font icons are in Private Use Area (U+E000-U+F8FF, U+F0000-U+FFFFD)
    and are NOT removed.

    Args:
        text: Input text containing emojis

    Returns:
        Text with emojis removed and whitespace normalized
    """
    # Emoji ranges to remove (ONLY chat emojis from emojidb.org)
    # Preserves Nerd Font icons (U+E000-U+F8FF, U+F0000-U+FFFFD)
    # Preserves Box-Drawing characters (U+2500-U+257F)
    # Preserves standard punctuation and technical symbols
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001FAF8"  # Emoji & Pictographs (😀🎉🚀 etc.)
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA70-\U0001FAF8"  # Extended Pictographs
        "\U0001F1E6-\U0001F1FF"  # Regional Indicators (flags 🇩🇪🇺🇸)
        "\U0000FE00-\U0000FE0F"  # Variation Selectors
        "\U0000200D"             # Zero Width Joiner
        "]+",
        flags=re.UNICODE
    )

    # Remove emojis and normalize whitespace ONLY where emojis were removed
    # This preserves intentional spacing like in tree structures (├──)
    def replace_and_normalize(match):
        # Emoji was found and will be removed
        # Check if there are multiple spaces around it
        start_pos = match.start()
        end_pos = match.end()

        # Get surrounding context (if available)
        before = text[max(0, start_pos-1):start_pos] if start_pos > 0 else ''
        after = text[end_pos:min(len(text), end_pos+1)] if end_pos < len(text) else ''

        # If emoji is surrounded by spaces on both sides, leave one space
        if before == ' ' and after == ' ':
            return ' '
        # Otherwise just remove the emoji
        return ''

    return emoji_pattern.sub(replace_and_normalize, text)

def remove_emojis_from_file(filepath: Path, keep_backup: bool = True) -> Tuple[bool, int]:
    """
    Remove emojis from a file

    Args:
        filepath: Path to the file
        keep_backup: Whether to keep backup file

    Returns:
        Tuple of (changed, emoji_count)
    """
    try:
        # Read file
        original_content = filepath.read_text(encoding='utf-8')

        # Remove emojis
        new_content = remove_emojis(original_content)

        # Check if changed
        if original_content == new_content:
            return False, 0

        # Count removed emojis (approximate)
        emoji_count = len(original_content) - len(new_content)

        # Create backup if requested
        if keep_backup:
            backup_path = filepath.with_suffix(filepath.suffix + '.emoji-backup')
            backup_path.write_text(original_content, encoding='utf-8')

        # Write cleaned content
        filepath.write_text(new_content, encoding='utf-8')

        return True, emoji_count

    except Exception as e:
        log_error(f"Error processing {filepath.name}: {e}")
        return False, 0

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Remove Unicode emojis from files while preserving Nerd Font icons',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Remove emojis from all files in current directory
  python3 remove_emojis.py

  # Remove emojis from specific directory
  python3 remove_emojis.py --path /path/to/scripts

  # Process specific file types
  python3 remove_emojis.py --types sh py md

  # Remove emojis recursively
  python3 remove_emojis.py --recursive

  # Don't keep backups
  python3 remove_emojis.py --no-backup
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
        default=['sh', 'py', 'md', 'yml', 'yaml', 'txt'],
        help='File extensions to process (default: sh py md yml yaml txt)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )

    args = parser.parse_args()

    # Determine base path
    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    # Collect files
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

    # Exclude certain files from processing
    exclude_patterns = [
        'remove_emojis.py',      # Don't modify self
        'fix_nerdfonts.py',      # Don't modify nerd font fixer
    ]

    filtered_files = []
    for f in files:
        should_exclude = False
        for pattern in exclude_patterns:
            if pattern.startswith('*'):
                # Glob pattern
                if f.match(pattern):
                    should_exclude = True
                    break
            else:
                # Exact filename match
                if f.name == pattern:
                    should_exclude = True
                    break

        if not should_exclude:
            filtered_files.append(f)

    files = filtered_files

    if not files:
        log_error(f"No files remaining after exclusions")
        return 1

    # Header
    tag = f"{Colors.MAUVE}[remove-emojis]{Colors.NC}"
    print(f"\n{tag} {CLEAN}  Removing Unicode emojis from files...\n")

    log_info(f"Processing {len(files)} file(s)")
    if not args.no_backup:
        log_info("Backups will be created with .emoji-backup extension")
    print()

    # Process files
    cleaned_count = 0
    unchanged_count = 0
    total_emojis = 0
    cleaned_files = []  # Track cleaned files

    for filepath in sorted(files):
        changed, emoji_count = remove_emojis_from_file(
            filepath,
            keep_backup=not args.no_backup
        )

        if changed:
            cleaned_count += 1
            total_emojis += emoji_count
            cleaned_files.append(filepath.name)
            log_success(f"Cleaned {filepath.name} (removed ~{emoji_count} chars)")
            if not args.no_backup:
                print(f"  {Colors.SUBTEXT}Backup: {filepath.name}.emoji-backup{Colors.NC}")
        else:
            unchanged_count += 1
            print(f"  {Colors.TEXT}{filepath.name}{Colors.NC} {Colors.SUBTEXT}(no emojis){Colors.NC}")

    # Summary
    print(f"\n{Colors.GREEN}summary:{Colors.NC}\n")
    print(f"{Colors.BLUE}  Total files:     {Colors.NC}{len(files)}")
    print(f"{Colors.GREEN}  Cleaned:         {Colors.NC}{cleaned_count}")
    print(f"{Colors.TEXT}  No emojis:       {Colors.NC}{unchanged_count}")
    print(f"{Colors.SAPPHIRE}  Chars removed:   {Colors.NC}~{total_emojis}")
    print()

    if cleaned_count > 0:
        log_success("Emoji removal complete!")
        if not args.no_backup:
            log_warn("Review changes before deleting .emoji-backup files!")

        # Show list of cleaned files
        print(f"\n{Colors.YELLOW}Files cleaned:{Colors.NC}")
        for filename in cleaned_files:
            print(f"  {Colors.TEXT}- {filename}{Colors.NC}")
        print()
    else:
        log_success("No emojis found!")

    return 0

if __name__ == '__main__':
    sys.exit(main())
