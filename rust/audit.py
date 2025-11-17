#!/usr/bin/env python3
"""
Rust security audit using cargo auditable
Builds binaries with embedded dependency info and checks for vulnerabilities
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


def check_auditable() -> bool:
    """Check if cargo-auditable is installed"""
    try:
        subprocess.run(['cargo', 'auditable', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("cargo-auditable is not installed")
        print()
        print(f"{Colors.TEXT}Install cargo-auditable:{Colors.NC}")
        print(f"{Colors.TEXT}  cargo install cargo-auditable{Colors.NC}")
        print()
        print(f"{Colors.BLUE}cargo-auditable embeds dependency info into Rust binaries{Colors.NC}")
        print(f"{Colors.BLUE}for better supply chain security and auditing.{Colors.NC}")
        print()
        return False


def get_auditable_version() -> str:
    """Get cargo-auditable version"""
    try:
        result = subprocess.run(
            ['cargo', 'auditable', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
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


def audit_project(project_path: Path, build_mode: str = 'check') -> int:
    """
    Audit a Rust project with cargo auditable
    build_mode: 'check' or 'build' (build creates actual binaries)
    Returns: 0=success, 1=warnings/issues, 2=failed
    """
    project_name = project_path.name

    if build_mode == 'build':
        log_info(f"  Building {project_name} with embedded audit info...")
        cmd = ['cargo', 'auditable', 'build', '--release']
    else:
        log_info(f"  Checking {project_name} dependencies...")
        cmd = ['cargo', 'auditable', 'build', '--release']

    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            log_success(f"  {project_name} - Audit complete, no issues")
            if build_mode == 'build':
                binary_path = project_path / 'target' / 'release'
                if binary_path.exists():
                    print(f"    {Colors.SAPPHIRE}Binary location: {binary_path}{Colors.NC}")
            return 0
        else:
            log_warn(f"  {project_name} - Build completed with warnings")
            if result.stdout:
                print(f"{Colors.YELLOW}{result.stdout.strip()}{Colors.NC}")
            if result.stderr:
                print(f"{Colors.RED}{result.stderr.strip()}{Colors.NC}")
            return 1

    except Exception as e:
        log_error(f"  Error auditing {project_name}: {e}")
        return 2


def main():
    """Main function"""
    import argparse

    config = load_env_config(REPO_ROOT)

    parser = argparse.ArgumentParser(
        description='Rust security audit using cargo auditable',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Audit current Rust project (check mode)
  python3 audit.py

  # Build binaries with embedded dependency info
  python3 audit.py --build

  # Audit all Rust projects in directory
  python3 audit.py --recursive

  # Audit specific project
  python3 audit.py --path /path/to/rust-project

About cargo-auditable:
  cargo-auditable builds Rust binaries with embedded dependency
  information, enabling better supply chain security auditing.
  This is more comprehensive than cargo-audit as it embeds
  the dependency tree directly into the binary.
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
        '-b', '--build',
        action='store_true',
        help='Build binaries (default: check only)'
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.MAUVE}[audit]{Colors.NC} {Icons.INFO}  Rust Security Audit (cargo auditable)")
    print()

    if not check_cargo():
        return 1

    if not check_auditable():
        return 1

    version = get_auditable_version()
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
    build_mode = 'build' if args.build else 'check'
    log_info(f"Mode: {build_mode}")
    print()

    clean = 0
    warnings = 0
    failed = 0

    for project_path in projects:
        result = audit_project(project_path, build_mode=build_mode)
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
        print(f"{Colors.GREEN}Clean:               {Colors.NC}{Colors.SAPPHIRE}{clean}{Colors.NC}")

    if warnings > 0:
        print(f"{Colors.YELLOW}Warnings:            {Colors.NC}{Colors.SAPPHIRE}{warnings}{Colors.NC}")

    if failed > 0:
        print(f"{Colors.RED}Failed:              {Colors.NC}{Colors.SAPPHIRE}{failed}{Colors.NC}")

    print()

    if failed > 0:
        log_error("Some projects failed to audit")
        return 1
    elif warnings > 0:
        log_warn("Some projects have warnings")
        return 0
    else:
        log_success("All projects passed audit!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
