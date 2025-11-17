#!/usr/bin/env python3
"""
Rust test runner using cargo test
Runs all tests in Rust projects
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


def test_project(project_path: Path, verbose: bool = False, nocapture: bool = False) -> int:
    """
    Test a Rust project with cargo test
    Returns: 0=passed, 1=failed, 2=error
    """
    project_name = project_path.name

    cmd = ['cargo', 'test']
    if verbose:
        cmd.append('--verbose')
    if nocapture:
        cmd.append('--')
        cmd.append('--nocapture')

    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            log_success(f"  {project_name} - All tests passed")
            if verbose and result.stdout:
                print(f"{Colors.TEXT}{result.stdout.strip()}{Colors.NC}")
            return 0
        else:
            log_error(f"  {project_name} - Tests failed")
            if result.stdout:
                print(f"{Colors.YELLOW}{result.stdout.strip()}{Colors.NC}")
            if result.stderr:
                print(f"{Colors.RED}{result.stderr.strip()}{Colors.NC}")
            return 1

    except Exception as e:
        log_error(f"  Error testing {project_name}: {e}")
        return 2


def main():
    """Main function"""
    import argparse

    config = load_env_config(REPO_ROOT)

    parser = argparse.ArgumentParser(
        description='Rust test runner using cargo test',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run tests in current Rust project
  python3 test_rust.py

  # Run tests in all Rust projects
  python3 test_rust.py --recursive

  # Run tests with verbose output
  python3 test_rust.py --verbose

  # Run tests with output from test code
  python3 test_rust.py --nocapture

  # Test specific project
  python3 test_rust.py --path /path/to/rust-project
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
        '-v', '--verbose',
        action='store_true',
        help='Verbose test output'
    )

    parser.add_argument(
        '-n', '--nocapture',
        action='store_true',
        help='Show output from test code (--nocapture)'
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.MAUVE}[test]{Colors.NC} {Icons.ROCKET}  Rust Test Runner")
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
    failed_tests = 0
    failed_run = 0

    for project_path in projects:
        result = test_project(project_path, verbose=args.verbose, nocapture=args.nocapture)
        if result == 0:
            passed += 1
        elif result == 1:
            failed_tests += 1
        elif result == 2:
            failed_run += 1

    print()
    print(f"{Colors.MAUVE}Summary{Colors.NC}")
    print()

    total = passed + failed_tests + failed_run
    print(f"{Colors.TEXT}Total projects:      {Colors.NC}{Colors.SAPPHIRE}{total}{Colors.NC}")

    if passed > 0:
        print(f"{Colors.GREEN}Passed:              {Colors.NC}{Colors.SAPPHIRE}{passed}{Colors.NC}")

    if failed_tests > 0:
        print(f"{Colors.YELLOW}Failed tests:        {Colors.NC}{Colors.SAPPHIRE}{failed_tests}{Colors.NC}")

    if failed_run > 0:
        print(f"{Colors.RED}Failed to run:       {Colors.NC}{Colors.SAPPHIRE}{failed_run}{Colors.NC}")

    print()

    if failed_tests > 0 or failed_run > 0:
        log_error("Some tests failed")
        return 1
    else:
        log_success("All tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
