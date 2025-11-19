#!/usr/bin/env python3
"""
Python cache cleaner - removes __pycache__ and .mypy_cache directories
Cleans up Python bytecode and type checking cache files
"""

import sys
import shutil
from pathlib import Path
from typing import List

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info
)


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


class PyCacheCleaner:
    def __init__(self):
        self.pycache_dirs = []
        self.mypy_cache_dirs = []
        self.total_size = 0
        self.config = load_env_config(REPO_ROOT)

    def get_dir_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except (PermissionError, OSError):
            pass
        return total

    def format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def scan_caches(self, base_path: Path) -> None:
        """Scan for cache directories"""
        # Find __pycache__ directories
        self.pycache_dirs = list(base_path.rglob('__pycache__'))

        # Find .mypy_cache directories
        self.mypy_cache_dirs = list(base_path.rglob('.mypy_cache'))

    def remove_caches(self, dry_run: bool) -> None:
        """Remove cache directories"""
        all_caches = self.pycache_dirs + self.mypy_cache_dirs

        if not all_caches:
            log_info("No cache directories found")
            return

        for cache_dir in all_caches:
            dir_size = self.get_dir_size(cache_dir)
            self.total_size += dir_size

            # Handle both absolute and relative paths
            try:
                rel_path = cache_dir.relative_to(REPO_ROOT)
            except (ValueError, TypeError):
                rel_path = cache_dir

            if dry_run:
                print(f"{Colors.YELLOW}{Icons.CLEAN}  {Colors.NC}{Colors.TEXT}Would remove: {Colors.NC}{Colors.SAPPHIRE}{rel_path}{Colors.NC} {Colors.SUBTEXT}({self.format_size(dir_size)}){Colors.NC}")
            else:
                try:
                    shutil.rmtree(cache_dir)
                    print(f"{Colors.GREEN}{Icons.CLEAN}  {Colors.NC}{Colors.TEXT}Removed: {Colors.NC}{Colors.SAPPHIRE}{rel_path}{Colors.NC} {Colors.SUBTEXT}({self.format_size(dir_size)}){Colors.NC}")
                except (PermissionError, OSError) as e:
                    log_error(f"Failed to remove {rel_path}: {e}")

    def run(self, base_path: Path, dry_run: bool) -> int:
        """Run cache cleaner"""
        print()
        print(f"{Colors.MAUVE}[pyclean]{Colors.NC} {Icons.CLEAN}  python cache cleaner")
        print()

        if dry_run:
            log_info("Dry run mode - no files will be deleted")
        else:
            log_info("Scanning for Python cache directories")

        print()

        self.scan_caches(base_path)

        total_dirs = len(self.pycache_dirs) + len(self.mypy_cache_dirs)

        if total_dirs == 0:
            log_success("No cache directories found - nothing to clean")
            return 0

        log_info(f"found {len(self.pycache_dirs)} __pycache__ director{'y' if len(self.pycache_dirs) == 1 else 'ies'}")
        log_info(f"found {len(self.mypy_cache_dirs)} .mypy_cache director{'y' if len(self.mypy_cache_dirs) == 1 else 'ies'}")
        print()

        self.remove_caches(dry_run)

        # Print summary
        print()
        print(f"{Colors.MAUVE}summary{Colors.NC}")
        print()
        print(f"{Colors.TEXT}Total directories:     {Colors.NC}{Colors.SAPPHIRE}{total_dirs}{Colors.NC}")
        print(f"{Colors.TEXT}Total size:            {Colors.NC}{Colors.SAPPHIRE}{self.format_size(self.total_size)}{Colors.NC}")
        print()

        if dry_run:
            log_warn("Dry run completed - run without --dry-run to actually remove files")
            return 0
        else:
            log_success(f"Cleaned {total_dirs} cache director{'y' if total_dirs == 1 else 'ies'}")
            return 0


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Python cache cleaner - removes __pycache__ and .mypy_cache directories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Clean cache directories in current directory (recursive)
  python3 pyclean.py

  # Dry run - show what would be removed
  python3 pyclean.py --dry-run

  # Clean specific directory
  python3 pyclean.py --path /path/to/project

  # Clean specific directory with dry run
  python3 pyclean.py --path /path/to/project --dry-run
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to directory to clean (default: current directory)'
    )

    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='Show what would be removed without actually removing files'
    )

    args = parser.parse_args()

    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    if not base_path.is_dir():
        log_error(f"Path is not a directory: {base_path}")
        return 1

    cleaner = PyCacheCleaner()
    return cleaner.run(base_path, args.dry_run)


if __name__ == '__main__':
    sys.exit(main())
