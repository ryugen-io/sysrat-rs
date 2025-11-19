#!/usr/bin/env python3
"""
Python linter - checks Python code quality
Supports multiple linting tools: flake8, pylint, mypy, black
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

# Import central theme
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


def check_tool_installed(tool: str) -> bool:
    """Check if a linting tool is installed"""
    try:
        subprocess.run([tool, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_syntax(filepath: Path) -> Tuple[bool, str]:
    """Check Python syntax"""
    try:
        subprocess.run(['python3', '-m', 'py_compile', str(filepath)],
                      check=True, capture_output=True, text=True)
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def run_flake8(filepath: Path) -> Tuple[bool, List[str]]:
    """Run flake8 linter"""
    try:
        result = subprocess.run(
            ['flake8', '--max-line-length=100', '--extend-ignore=E501,W503', str(filepath)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, []
        return False, result.stdout.strip().split('\n') if result.stdout else []
    except FileNotFoundError:
        return True, []  # Tool not installed, skip


def run_pylint(filepath: Path) -> Tuple[bool, str]:
    """Run pylint"""
    try:
        result = subprocess.run(
            ['pylint', '--disable=C0111,C0103,R0913', str(filepath)],
            capture_output=True,
            text=True
        )
        # Pylint returns non-zero for warnings, we only care about score < 8
        if 'rated at' in result.stdout:
            score_line = [line for line in result.stdout.split('\n') if 'rated at' in line]
            if score_line:
                score = float(score_line[0].split('rated at ')[1].split('/')[0])
                if score < 8.0:
                    return False, result.stdout
        return True, ""
    except (FileNotFoundError, ValueError, IndexError):
        return True, ""  # Tool not installed or parsing error, skip


def run_mypy(filepath: Path) -> Tuple[bool, List[str]]:
    """Run mypy type checker"""
    try:
        result = subprocess.run(
            ['mypy', '--ignore-missing-imports', str(filepath)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, []
        return False, result.stdout.strip().split('\n') if result.stdout else []
    except FileNotFoundError:
        return True, []  # Tool not installed, skip


def lint_file(filepath: Path, tools: List[str]) -> Tuple[bool, int]:
    """
    Lint a single Python file
    Returns: (passed, issues)
    """
    issues = 0

    print(f"{Colors.BLUE}checking {Colors.NC}{filepath}")

    # 1. Syntax check (always run)
    passed, error = check_syntax(filepath)
    if not passed:
        log_error(f"  Syntax error: {error}")
        issues += 1
        return False, issues

    # 2. Run requested tools
    if 'flake8' in tools:
        passed, errors = run_flake8(filepath)
        if not passed:
            log_warn(f"  Flake8: {len(errors)} issue(s)")
            for error in errors[:3]:  # Show first 3 errors
                print(f"    {Colors.YELLOW}{error}{Colors.NC}")
            if len(errors) > 3:
                print(f"    {Colors.SUBTEXT}... and {len(errors) - 3} more{Colors.NC}")

    if 'pylint' in tools:
        passed, output = run_pylint(filepath)
        if not passed:
            log_warn("  Pylint: Score < 8.0")

    if 'mypy' in tools:
        passed, errors = run_mypy(filepath)
        if not passed:
            log_warn(f"  Mypy: {len(errors)} type issue(s)")
            for error in errors[:2]:  # Show first 2 errors
                print(f"    {Colors.YELLOW}{error}{Colors.NC}")
            if len(errors) > 2:
                print(f"    {Colors.SUBTEXT}... and {len(errors) - 2} more{Colors.NC}")

    if issues == 0:
        log_success("  passed syntax check")
        return True, 0
    else:
        log_error(f"  {issues} critical issue(s) found")
        return False, issues


def has_ignore_marker(filepath: Path) -> bool:
    """Check if file contains PYLINTCHECK_IGNORE marker"""
    try:
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                if 'PYLINTCHECK_IGNORE' in line:
                    return True
        return False
    except Exception:
        return False


def scan_files(base_path: Path, recursive: bool) -> List[Path]:
    """Scan for Python files"""
    files = []

    if base_path.is_file():
        if base_path.suffix == '.py':
            files.append(base_path)
    elif base_path.is_dir():
        pattern = '**/*.py' if recursive else '*.py'
        files.extend(base_path.glob(pattern))

    return sorted(files)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Python linter - checks Python code quality',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Lint all Python files in current directory (syntax only)
  python3 pylint.py

  # Lint with flake8
  python3 pylint.py --tools flake8

  # Lint with multiple tools
  python3 pylint.py --tools flake8 mypy

  # Lint files recursively
  python3 pylint.py --recursive --path /path/to/project

  # Lint a specific file
  python3 pylint.py --path script.py

Available tools: flake8, pylint, mypy
(Install with: pip install flake8 pylint mypy)
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to file or directory to lint (default: current directory)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    parser.add_argument(
        '-t', '--tools',
        nargs='+',
        choices=['flake8', 'pylint', 'mypy'],
        default=[],
        help='Additional linting tools to use (default: syntax check only)'
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.MAUVE}[pylint]{Colors.NC} python linter")
    print()

    # Check which tools are available
    available_tools = []
    for tool in args.tools:
        if check_tool_installed(tool):
            available_tools.append(tool)
            log_info(f"{tool} available")
        else:
            log_warn(f"{tool} not installed (skipping)")

    if not available_tools and args.tools:
        log_warn("No linting tools available, running syntax check only")

    print()

    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    # Scan files
    files = scan_files(base_path, args.recursive)

    if not files:
        log_error("No Python files found")
        return 1

    log_info(f"checking {len(files)} file(s)")
    print()

    # Lint files
    total_files = 0
    passed_files = 0
    total_issues = 0

    for filepath in files:
        if has_ignore_marker(filepath):
            print(f"{Colors.SUBTEXT}Skipping: {Colors.YELLOW}{filepath.name}{Colors.NC} {Colors.SUBTEXT}(PYLINTCHECK_IGNORE){Colors.NC}")
            print()
            continue

        passed, issues = lint_file(filepath, available_tools)
        total_files += 1
        if passed:
            passed_files += 1
        total_issues += issues
        print()

    # Summary
    print(f"{Colors.GREEN}summary:{Colors.NC}")
    print()
    print(f"{Colors.BLUE}  Total files:       {Colors.NC}{total_files}")
    print(f"{Colors.GREEN}  Passed:            {Colors.NC}{passed_files}")
    print(f"{Colors.RED}  Critical issues:   {Colors.NC}{total_issues}")
    print()

    if total_issues == 0:
        log_success("all python files passed")
        return 0
    else:
        log_error("linting failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
