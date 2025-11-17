#!/usr/bin/env python3
"""
Rust code formatter using cargo fmt
Automatically formats all Rust code in the workspace
"""

import sys
import subprocess
from pathlib import Path
from typing import List

# Add .sys/theme to path for central theming
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
        'RUST_TOOLCHAIN': 'stable'
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


def check_rustfmt() -> bool:
    """Check if rustfmt is installed"""
    try:
        subprocess.run(['rustfmt', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("rustfmt is not installed")
        print()
        print(f"{Colors.TEXT}Install rustfmt:{Colors.NC}")
        print(f"{Colors.TEXT}  rustup component add rustfmt{Colors.NC}")
        print()
        return False


def get_rustfmt_version() -> str:
    """Get rustfmt version"""
    try:
        result = subprocess.run(['rustfmt', '--version'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


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


def format_project(project_path: Path, check_mode: bool = False) -> int:
    """
    Format a Rust project
    Returns: 0=formatted, 1=unchanged, 2=failed
    """
    project_name = project_path.name

    cmd = ['cargo', 'fmt']
    if check_mode:
        cmd.append('--check')

    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            if check_mode:
                print(f"  {Colors.TEXT}{project_name}{Colors.NC} {Colors.SAPPHIRE}(already formatted){Colors.NC}")
                return 1
            else:
                log_success(f"  Formatted {project_name}")
                return 0
        else:
            if check_mode:
                log_warn(f"  {project_name} needs formatting")
                return 0
            else:
                log_error(f"  Failed to format {project_name}")
                if result.stderr:
                    print(f"{Colors.RED}{result.stderr.strip()}{Colors.NC}")
                return 2

    except Exception as e:
        log_error(f"  Error formatting {project_name}: {e}")
        return 2


def main():
    """Main function"""
    import argparse

    config = load_env_config(REPO_ROOT)

    parser = argparse.ArgumentParser(
        description='Rust code formatter using cargo fmt',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Format current Rust project
  python3 rustfmt.py

  # Check formatting without modifying files
  python3 rustfmt.py --check

  # Format all Rust projects in directory
  python3 rustfmt.py --recursive

  # Format specific project
  python3 rustfmt.py --path /path/to/rust-project
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
        '-c', '--check',
        action='store_true',
        help='Check mode - do not modify files, just report'
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.MAUVE}[rustfmt]{Colors.NC} {Icons.HAMMER}  Rust Code Formatter")
    print()

    if args.check:
        log_info("Running in check mode (no files will be modified)")
        print()

    if not check_cargo():
        return 1

    if not check_rustfmt():
        return 1

    version = get_rustfmt_version()
    log_info(f"Using {version}")
    print()

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

    formatted = 0
    unchanged = 0
    failed = 0

    for project_path in projects:
        result = format_project(project_path, check_mode=args.check)
        if result == 0:
            formatted += 1
        elif result == 1:
            unchanged += 1
        elif result == 2:
            failed += 1

    print()
    print(f"{Colors.MAUVE}Summary{Colors.NC}")
    print()

    total = formatted + unchanged + failed
    print(f"{Colors.TEXT}Total projects:      {Colors.NC}{Colors.SAPPHIRE}{total}{Colors.NC}")

    if formatted > 0:
        action = "Need formatting" if args.check else "Formatted"
        print(f"{Colors.GREEN}{action}:         {Colors.NC}{Colors.SAPPHIRE}{formatted}{Colors.NC}")

    if unchanged > 0:
        print(f"{Colors.TEXT}Already formatted:   {Colors.NC}{Colors.SAPPHIRE}{unchanged}{Colors.NC}")

    if failed > 0:
        print(f"{Colors.RED}Failed:              {Colors.NC}{Colors.SAPPHIRE}{failed}{Colors.NC}")

    print()

    if failed > 0:
        log_error("Some projects failed to format")
        return 1
    elif formatted > 0:
        if args.check:
            log_warn("Some projects need formatting")
            return 1
        else:
            log_success("All projects formatted successfully!")
            return 0
    else:
        log_success("All projects already formatted correctly!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
