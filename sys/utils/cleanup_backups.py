#!/usr/bin/env python3
"""
Backup File Cleanup Tool - Find and optionally delete .backup files
"""

import sys
from pathlib import Path

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent  # Go up 2 levels: utils/ -> sys/ -> repo root
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

# Import central theme
from theme import Colors, Icons, log_success, log_info, log_warn, log_error


def find_backup_files(directory: Path) -> list:
    """Find all .backup and .backup-* files in directory recursively."""
    backup_files = []

    # Find .backup files
    backup_files.extend(directory.rglob('*.backup'))

    # Find .backup-* files (timestamped backups)
    backup_files.extend(directory.rglob('*.backup-*'))

    # Sort by modification time (newest first)
    backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return backup_files


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_age(mtime: float) -> str:
    """Format file age in human-readable format."""
    import time
    age_seconds = time.time() - mtime
    age_minutes = age_seconds / 60
    age_hours = age_minutes / 60
    age_days = age_hours / 24

    if age_days >= 1:
        return f"{int(age_days)}d ago"
    elif age_hours >= 1:
        return f"{int(age_hours)}h ago"
    elif age_minutes >= 1:
        return f"{int(age_minutes)}m ago"
    else:
        return f"{int(age_seconds)}s ago"


def main():
    """Main function."""
    print(f"{Colors.MAUVE}[cleanup-backups]{Colors.NC} {Icons.FILE}  Finding backup files...\n")

    # Find all backup files
    backup_files = find_backup_files(REPO_ROOT)

    if not backup_files:
        log_success("No backup files found!")
        return

    # Display found files
    total_size = 0
    log_info(f"Found {len(backup_files)} backup file(s):\n")

    for i, backup_file in enumerate(backup_files, 1):
        size = backup_file.stat().st_size
        mtime = backup_file.stat().st_mtime
        relative_path = backup_file.relative_to(REPO_ROOT)

        total_size += size

        # Color based on age (red = old, yellow = medium, green = recent)
        age_days = (time.time() - mtime) / 86400
        if age_days > 7:
            color = Colors.RED
        elif age_days > 1:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN

        print(f"  {color}{i:2d}.{Colors.NC} {relative_path}")
        print(f"      {Colors.SUBTEXT}Size: {format_size(size):>10}  |  Age: {format_age(mtime)}{Colors.NC}")

    print(f"\n{Colors.BLUE}Total:{Colors.NC} {len(backup_files)} files, {format_size(total_size)}\n")

    # Ask user what to do
    try:
        response = input(f"{Colors.YELLOW}{Icons.WARN}  {Colors.NC}Delete all backup files? [y/N]: ").strip().lower()

        if response in ['y', 'yes']:
            deleted_count = 0
            deleted_size = 0

            for backup_file in backup_files:
                try:
                    size = backup_file.stat().st_size
                    backup_file.unlink()
                    deleted_count += 1
                    deleted_size += size
                    print(f"{Colors.GREEN}{Icons.CHECK}  {Colors.NC}Deleted: {backup_file.relative_to(REPO_ROOT)}")
                except Exception as e:
                    log_error(f"Failed to delete {backup_file.name}: {e}")

            print()
            log_success(f"Deleted {deleted_count} file(s), freed {format_size(deleted_size)}")
        else:
            log_info("No files deleted")

    except KeyboardInterrupt:
        print()
        log_warn("Cancelled by user")
        sys.exit(0)


if __name__ == '__main__':
    import time
    main()
