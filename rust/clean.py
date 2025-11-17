#!/usr/bin/env python3
"""
Rust cache cleaner using cargo clean
Removes build artifacts and caches from Rust projects
"""

import sys
import subprocess
from pathlib import Path
from typing import List
import shutil

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / '.sys' / 'theme'))

from theme import Colors, Icons, log_success, log_error, log_warn, log_info


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from .env file"""
    config = {
        'SYS_DIR': '.sys',
        'GITHUB_DIR': '.github',
        'SCRIPT_DIRS': 'docker,dev,utils,rust',
        'RUST_TOOLCHAIN': 'stable',
        'RUST_TARGET_DIR': 'target'
    }

    sys_env_dir = repo_root / config['SYS_DIR'] / 'env'
    for env_name in ['.env', '.env.example']:
        env_file = sys_env_dir / env_name
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
            break

    return config


def check_cargo() -> bool:
    """Check if cargo is installed"""
    try:
        subprocess.run(['cargo', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("cargo is not installed")
        print()
        print(f"{Colors.TEXT}Install Rust and cargo:{Colors.NC}")
        print(f"{Colors.BLUE}  # Using rustup (recommended){Colors.NC}")
        print(f"{Colors.TEXT}  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh{Colors.NC}")
        print()
        return False


def get_dir_size(path: Path) -> int:
    """Get total size of directory in bytes"""
    total = 0
    try:
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except (OSError, PermissionError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def find_cargo_projects(base_path: Path, recursive: bool) -> List[Path]:
    """Find all Cargo.toml files (Rust projects)"""
    projects = []

    if base_path.is_file() and base_path.name == 'Cargo.toml':
        projects.append(base_path.parent)
    elif base_path.is_dir():
        if (base_path / 'Cargo.toml').exists():
            projects.append(base_path)
        elif recursive:
            for cargo_toml in base_path.rglob('Cargo.toml'):
                projects.append(cargo_toml.parent)

    return sorted(set(projects))


def clean_project(project_path: Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Clean a Rust project with cargo clean
    Returns: (status, size_freed) where status is 0=success, 1=failed
    """
    project_name = project_path.name
    config = load_env_config(REPO_ROOT)
    target_dir = project_path / config['RUST_TARGET_DIR']

    if not target_dir.exists():
        print(f"  {Colors.TEXT}{project_name}{Colors.NC} {Colors.SUBTEXT}(no target dir){Colors.NC}")
        return (0, 0)

    size_before = get_dir_size(target_dir)

    if dry_run:
        log_info(f"  {project_name} - Would free {format_size(size_before)}")
        return (0, size_before)

    try:
        result = subprocess.run(
            ['cargo', 'clean'],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            log_success(f"  {project_name} - Freed {format_size(size_before)}")
            return (0, size_before)
        else:
            log_error(f"  {project_name} - Clean failed")
            if result.stderr:
                print(f"{Colors.RED}{result.stderr.strip()}{Colors.NC}")
            return (1, 0)

    except Exception as e:
        log_error(f"  Error cleaning {project_name}: {e}")
        return (1, 0)


def main():
    """Main function"""
    import argparse

    config = load_env_config(REPO_ROOT)

    parser = argparse.ArgumentParser(
        description='Rust cache cleaner using cargo clean',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Clean current Rust project
  python3 clean.py

  # Preview what would be cleaned (dry run)
  python3 clean.py --dry-run

  # Clean all Rust projects in directory
  python3 clean.py --recursive

  # Clean specific project
  python3 clean.py --path /path/to/rust-project
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to Rust project or directory (default: current directory)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively for Cargo.toml files'
    )

    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='Dry run - show what would be cleaned without actually cleaning'
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.MAUVE}[clean]{Colors.NC} {Icons.CLEAN}  Rust Cache Cleaner")
    print()

    if args.dry_run:
        log_info("Running in dry-run mode (no files will be removed)")
        print()

    if not check_cargo():
        return 1

    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    projects = find_cargo_projects(base_path, args.recursive)

    if not projects:
        log_error("No Rust projects found (no Cargo.toml)")
        return 1

    log_info(f"Found {len(projects)} Rust project(s)")
    print()

    cleaned = 0
    failed = 0
    total_freed = 0

    for project_path in projects:
        status, size_freed = clean_project(project_path, dry_run=args.dry_run)
        if status == 0:
            cleaned += 1
            total_freed += size_freed
        else:
            failed += 1

    print()
    print(f"{Colors.MAUVE}Summary{Colors.NC}")
    print()

    total = cleaned + failed
    print(f"{Colors.TEXT}Total projects:      {Colors.NC}{Colors.SAPPHIRE}{total}{Colors.NC}")

    if cleaned > 0:
        action = "Would clean" if args.dry_run else "Cleaned"
        print(f"{Colors.GREEN}{action}:           {Colors.NC}{Colors.SAPPHIRE}{cleaned}{Colors.NC}")

    if failed > 0:
        print(f"{Colors.RED}Failed:              {Colors.NC}{Colors.SAPPHIRE}{failed}{Colors.NC}")

    if total_freed > 0:
        action = "Would free" if args.dry_run else "Freed"
        print(f"{Colors.SAPPHIRE}Space {action.lower()}:      {Colors.NC}{Colors.SAPPHIRE}{format_size(total_freed)}{Colors.NC}")

    print()

    if failed > 0:
        log_error("Some projects failed to clean")
        return 1
    else:
        if args.dry_run:
            log_success("Dry run complete!")
        else:
            log_success("All projects cleaned successfully!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
