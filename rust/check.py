#!/usr/bin/env python3
"""
Rust build checker using cargo check
Checks if Rust code compiles without producing binaries
"""

import sys
import subprocess
from pathlib import Path
from typing import List

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


def get_cargo_version() -> str:
    """Get cargo version"""
    try:
        result = subprocess.run(['cargo', '--version'], capture_output=True, text=True, check=True)
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


def check_project(project_path: Path, all_targets: bool = False) -> int:
    """
    Check a Rust project with cargo check
    Returns: 0=success, 1=errors, 2=failed
    """
    project_name = project_path.name

    cmd = ['cargo', 'check']
    if all_targets:
        cmd.append('--all-targets')

    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            log_success(f"  {project_name} - Check passed")
            return 0
        else:
            log_error(f"  {project_name} - Check failed")
            if result.stdout:
                print(f"{Colors.YELLOW}{result.stdout.strip()}{Colors.NC}")
            if result.stderr:
                print(f"{Colors.RED}{result.stderr.strip()}{Colors.NC}")
            return 1

    except Exception as e:
        log_error(f"  Error checking {project_name}: {e}")
        return 2


def main():
    """Main function"""
    import argparse

    config = load_env_config(REPO_ROOT)

    parser = argparse.ArgumentParser(
        description='Rust build checker using cargo check',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Check current Rust project
  python3 check.py

  # Check all Rust projects in directory
  python3 check.py --recursive

  # Check all targets (tests, benches, examples)
  python3 check.py --all-targets

  # Check specific project
  python3 check.py --path /path/to/rust-project
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
        '-a', '--all-targets',
        action='store_true',
        help='Check all targets (tests, benches, examples)'
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.MAUVE}[check]{Colors.NC} {Icons.CHECK}  Rust Build Checker")
    print()

    if not check_cargo():
        return 1

    version = get_cargo_version()
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

    passed = 0
    errors = 0
    failed = 0

    for project_path in projects:
        result = check_project(project_path, all_targets=args.all_targets)
        if result == 0:
            passed += 1
        elif result == 1:
            errors += 1
        elif result == 2:
            failed += 1

    print()
    print(f"{Colors.MAUVE}Summary{Colors.NC}")
    print()

    total = passed + errors + failed
    print(f"{Colors.TEXT}Total projects:      {Colors.NC}{Colors.SAPPHIRE}{total}{Colors.NC}")

    if passed > 0:
        print(f"{Colors.GREEN}Passed:              {Colors.NC}{Colors.SAPPHIRE}{passed}{Colors.NC}")

    if errors > 0:
        print(f"{Colors.YELLOW}Errors:              {Colors.NC}{Colors.SAPPHIRE}{errors}{Colors.NC}")

    if failed > 0:
        print(f"{Colors.RED}Failed:              {Colors.NC}{Colors.SAPPHIRE}{failed}{Colors.NC}")

    print()

    if failed > 0 or errors > 0:
        log_error("Some projects failed checks")
        return 1
    else:
        log_success("All projects passed checks!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
