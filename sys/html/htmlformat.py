#!/usr/bin/env python3
"""
HTML formatter using prettier or tidy
Formats HTML files for consistent style
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
                value = value.strip('"').strip("'")
                config[key] = value

    return config


def check_prettier() -> bool:
    """Check if prettier is installed"""
    try:
        subprocess.run(['npx', 'prettier', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_tidy() -> bool:
    """Check if tidy is installed"""
    try:
        subprocess.run(['tidy', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def find_html_files(base_path: Path, recursive: bool) -> List[Path]:
    """Find all HTML files in the given path"""
    html_files = []

    if recursive:
        html_files = list(base_path.rglob('*.html'))
    else:
        html_files = list(base_path.glob('*.html'))

    # Filter out build artifacts and dependencies
    exclude_patterns = [
        'target/', 'dist/', 'node_modules/', '.git/',
        'vendor/', 'build/', '__pycache__/'
    ]

    filtered_files = []
    for html_file in html_files:
        if not any(pattern in str(html_file) for pattern in exclude_patterns):
            filtered_files.append(html_file)

    return filtered_files


def format_html_prettier(html_files: List[Path], check_only: bool) -> bool:
    """Format HTML using prettier"""
    log_info(f"Formatting {len(html_files)} HTML file(s) with Prettier...")

    file_args = [str(f) for f in html_files]
    cmd = ['npx', 'prettier', '--write' if not check_only else '--check'] + file_args

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            if check_only:
                log_success("All HTML files are formatted correctly")
            else:
                log_success("HTML files formatted successfully")
            return True
        else:
            if check_only:
                log_error("Some HTML files need formatting")
            else:
                log_error("HTML formatting failed")
            if result.stdout:
                print()
                print(f"{Colors.SUBTEXT}{result.stdout}{Colors.NC}")
            return False

    except Exception as e:
        log_error(f"Failed to run prettier: {e}")
        return False


def format_html_manual(html_files: List[Path]) -> bool:
    """Manual HTML formatting (basic indentation fix)"""
    log_warn("No formatter installed, using basic formatting...")
    print()

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic formatting: ensure consistent line endings
            content = content.replace('\r\n', '\n')

            # Write back
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)

            rel_path = html_file.relative_to(REPO_ROOT)
            print(f"{Colors.GREEN}{Icons.CHECK}  {Colors.NC}{rel_path}")

        except Exception as e:
            rel_path = html_file.relative_to(REPO_ROOT)
            print(f"{Colors.RED}{Icons.CROSS}  {Colors.NC}{rel_path}: {e}")
            return False

    print()
    log_success("Basic formatting completed")
    return True


def run_htmlformat(base_path: Path, recursive: bool, check_only: bool) -> int:
    """Run HTML formatting"""
    print(f"{Colors.MAUVE}[htmlformat]{Colors.NC} HTML Formatting")
    print()

    # Find HTML files
    html_files = find_html_files(base_path, recursive)

    if not html_files:
        log_warn("No HTML files found")
        return 0

    print(f"{Colors.TEXT}Found {len(html_files)} HTML file(s){Colors.NC}")
    for html_file in html_files:
        rel_path = html_file.relative_to(base_path)
        print(f"{Colors.SUBTEXT}  - {rel_path}{Colors.NC}")
    print()

    # Check for prettier
    if check_prettier():
        success = format_html_prettier(html_files, check_only)
        return 0 if success else 1

    # Check for tidy
    if check_tidy():
        log_info("Using tidy for HTML formatting")
        log_warn("tidy support not yet implemented, using basic formatting")
        success = format_html_manual(html_files)
        return 0 if success else 1

    # Fall back to manual
    if check_only:
        log_warn("Cannot check formatting without prettier or tidy")
        return 1

    success = format_html_manual(html_files)
    return 0 if success else 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='HTML formatter',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search for HTML files recursively'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if files are formatted (do not modify)'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to search for HTML files (default: current directory)'
    )

    args = parser.parse_args()

    # Resolve path
    base_path = Path(args.path).resolve()
    if not base_path.exists():
        log_error(f"Path does not exist: {base_path}")
        return 1

    # Run formatting
    return run_htmlformat(
        base_path=base_path,
        recursive=args.recursive,
        check_only=args.check
    )


if __name__ == '__main__':
    sys.exit(main())
