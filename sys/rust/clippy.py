#!/usr/bin/env python3
"""
Rust linter using cargo clippy
Checks Rust code for common mistakes and improvements
"""

import sys
import subprocess
from pathlib import Path
from typing import List

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

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


def check_clippy() -> bool:
    """Check if clippy is installed"""
    try:
        subprocess.run(['cargo', 'clippy', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("clippy is not installed")
        print()
        print(f"{Colors.TEXT}Install clippy:{Colors.NC}")
        print(f"{Colors.TEXT}  rustup component add clippy{Colors.NC}")
        print()
        return False


def get_clippy_version() -> str:
    """Get clippy version"""
    try:
        result = subprocess.run(['cargo', 'clippy', '--version'], capture_output=True, text=True, check=True)
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


def lint_project(project_path: Path, deny_warnings: bool = True) -> int:
    """
    Lint a Rust project with clippy
    Returns: 0=no warnings, 1=warnings found, 2=failed

    NOTE: Always uses -D warnings to fail on any warnings
    """
    project_name = project_path.name

    # ALWAYS use -D warnings to catch all issues
    cmd = ['cargo', 'clippy', '--all-targets', '--all-features', '--', '-D', 'warnings']

    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            log_success(f"  {project_name} - No issues found")
            return 0
        else:
            log_warn(f"  {project_name} - Issues found")
            if result.stdout:
                print(f"{Colors.YELLOW}{result.stdout.strip()}{Colors.NC}")
            if result.stderr:
                print(f"{Colors.RED}{result.stderr.strip()}{Colors.NC}")
            return 1

    except Exception as e:
        log_error(f"  Error linting {project_name}: {e}")
        return 2


def main():
    """Main function"""
    import argparse

    config = load_env_config(REPO_ROOT)

    parser = argparse.ArgumentParser(
        description='Rust linter using cargo clippy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Lint current Rust project
  python3 clippy.py

  # Lint all Rust projects in directory
  python3 clippy.py --recursive

  # Treat warnings as errors
  python3 clippy.py --deny-warnings

  # Lint specific project
  python3 clippy.py --path /path/to/rust-project
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
        '-d', '--deny-warnings',
        action='store_true',
        help='Treat warnings as errors'
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.MAUVE}[clippy]{Colors.NC} {Icons.WARN}  Rust Linter")
    print()

    if not check_cargo():
        return 1

    if not check_clippy():
        return 1

    version = get_clippy_version()
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

    clean = 0
    warnings = 0
    failed = 0

    for project_path in projects:
        result = lint_project(project_path, deny_warnings=args.deny_warnings)
        if result == 0:
            clean += 1
        elif result == 1:
            warnings += 1
        elif result == 2:
            failed += 1

    print()
    print(f"{Colors.MAUVE}Summary{Colors.NC}")
    print()

    total = clean + warnings + failed
    print(f"{Colors.TEXT}Total projects:      {Colors.NC}{Colors.SAPPHIRE}{total}{Colors.NC}")

    if clean > 0:
        print(f"{Colors.GREEN}No issues:           {Colors.NC}{Colors.SAPPHIRE}{clean}{Colors.NC}")

    if warnings > 0:
        print(f"{Colors.YELLOW}Issues found:        {Colors.NC}{Colors.SAPPHIRE}{warnings}{Colors.NC}")

    if failed > 0:
        print(f"{Colors.RED}Failed:              {Colors.NC}{Colors.SAPPHIRE}{failed}{Colors.NC}")

    print()

    if failed > 0:
        log_error("Some projects failed to lint")
        return 1
    elif warnings > 0:
        log_warn("Some projects have linting issues")
        return 1
    else:
        log_success("All projects passed linting!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
