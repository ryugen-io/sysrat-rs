#!/usr/bin/env python3
"""
HTML linter and validator
Validates HTML files for W3C compliance and best practices
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

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


def check_html5validator() -> bool:
    """Check if html5validator is installed"""
    try:
        subprocess.run(['html5validator', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_warn("html5validator is not installed")
        print()
        print(f"{Colors.TEXT}Install html5validator:{Colors.NC}")
        print(f"{Colors.BLUE}  # Using pip{Colors.NC}")
        print(f"{Colors.TEXT}  pip install html5validator{Colors.NC}")
        print()
        print(f"{Colors.SUBTEXT}Falling back to basic HTML syntax checking...{Colors.NC}")
        print()
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


def validate_html_basic(html_file: Path) -> Tuple[bool, str]:
    """Basic HTML syntax validation"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Basic checks
        errors = []

        if '<!DOCTYPE html>' not in content and '<!doctype html>' not in content:
            errors.append("Missing DOCTYPE declaration")

        if '<html' not in content:
            errors.append("Missing <html> tag")

        if '<head>' not in content:
            errors.append("Missing <head> tag")

        if '<body>' not in content:
            errors.append("Missing <body> tag")

        if '<meta charset=' not in content and '<meta charset=' not in content.lower():
            errors.append("Missing charset meta tag")

        if errors:
            return False, "\n".join(f"  - {err}" for err in errors)
        return True, "OK"

    except Exception as e:
        return False, str(e)


def filter_trunk_warnings(output: str) -> Tuple[str, bool]:
    """Filter out Trunk-specific warnings from html5validator output"""
    # Trunk-specific patterns to ignore
    ignore_patterns = [
        'Element "link" is missing one or more of the following attributes: "href", "resource"',
    ]

    lines = output.split('\n')
    filtered_lines = []
    has_real_errors = False

    for line in lines:
        # Check if line contains a Trunk-specific pattern
        is_trunk_warning = any(pattern in line for pattern in ignore_patterns)

        if is_trunk_warning:
            # Skip this line (Trunk-specific, not a real error)
            continue

        filtered_lines.append(line)

        # Check if this is a real error line
        if 'error:' in line.lower() or 'warning:' in line.lower():
            has_real_errors = True

    return '\n'.join(filtered_lines), has_real_errors


def validate_html_w3c(html_files: List[Path]) -> bool:
    """Validate HTML using html5validator (W3C validator)"""
    log_info(f"Running W3C HTML validation on {len(html_files)} file(s)...")

    # Build file list
    file_args = [str(f) for f in html_files]

    try:
        result = subprocess.run(
            ['html5validator'] + file_args,
            capture_output=True,
            text=True
        )

        # Filter Trunk-specific warnings
        filtered_output, has_real_errors = filter_trunk_warnings(result.stdout)

        if result.returncode == 0 or not has_real_errors:
            log_success("All HTML files are valid")
            return True
        else:
            log_error("HTML validation failed")
            if filtered_output.strip():
                print()
                print(f"{Colors.SUBTEXT}Validation output:{Colors.NC}")
                print(filtered_output)
            if result.stderr:
                print(f"{Colors.RED}{result.stderr}{Colors.NC}")
            return False

    except Exception as e:
        log_error(f"Failed to run html5validator: {e}")
        return False


def run_htmllint(base_path: Path, recursive: bool, use_validator: bool) -> int:
    """Run HTML linting"""
    print(f"{Colors.MAUVE}[htmllint]{Colors.NC} HTML Linting")
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

    # Use W3C validator if available
    if use_validator and check_html5validator():
        success = validate_html_w3c(html_files)
        return 0 if success else 1

    # Fall back to basic validation
    log_info("Running basic HTML syntax checks...")
    print()

    all_valid = True
    for html_file in html_files:
        rel_path = html_file.relative_to(base_path)
        valid, message = validate_html_basic(html_file)

        if valid:
            print(f"{Colors.GREEN}{Icons.CHECK}  {Colors.NC}{rel_path}: {Colors.SUBTEXT}{message}{Colors.NC}")
        else:
            all_valid = False
            print(f"{Colors.RED}{Icons.CROSS}  {Colors.NC}{rel_path}:")
            print(f"{Colors.RED}{message}{Colors.NC}")

    print()
    if all_valid:
        log_success("All HTML files passed basic validation")
        return 0
    else:
        log_error("Some HTML files have validation errors")
        return 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='HTML linter and validator',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search for HTML files recursively'
    )
    parser.add_argument(
        '--no-validator',
        action='store_true',
        help='Skip W3C validator, use basic checks only'
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

    # Run linting
    return run_htmllint(
        base_path=base_path,
        recursive=args.recursive,
        use_validator=not args.no_validator
    )


if __name__ == '__main__':
    sys.exit(main())
