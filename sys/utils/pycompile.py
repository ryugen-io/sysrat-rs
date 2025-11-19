#!/usr/bin/env python3
"""
Python compilation checker - validates Python syntax by compiling to bytecode
Scans Python files and reports compilation errors
"""

import sys
from pathlib import Path
from typing import List, Tuple
import py_compile

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


class PyCompileChecker:
    def __init__(self):
        self.total_files = 0
        self.passed_files = 0
        self.failed_files = 0
        self.errors = []
        self.config = load_env_config(REPO_ROOT)

    def compile_file(self, filepath: Path) -> Tuple[bool, str]:
        """
        Compile a Python file to bytecode
        Returns: (success, error_message)
        """
        try:
            py_compile.compile(str(filepath), doraise=True)
            return True, ""
        except py_compile.PyCompileError as e:
            # Extract meaningful error message
            error_msg = str(e)
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def check_file(self, filepath: Path) -> bool:
        """Check a single Python file"""
        self.total_files += 1

        # Handle both absolute and relative paths
        try:
            rel_path = filepath.relative_to(REPO_ROOT)
        except ValueError:
            rel_path = filepath

        print(f"{Colors.TEXT}Compiling: {Colors.SAPPHIRE}{rel_path}{Colors.NC}")

        success, error_msg = self.compile_file(filepath)

        if success:
            log_success("  compilation successful")
            self.passed_files += 1
            return True
        else:
            log_error("  Compilation failed")
            print(f"{Colors.RED}    {error_msg}{Colors.NC}")
            self.failed_files += 1
            self.errors.append((filepath, error_msg))
            return False

    def scan_files(self, base_path: Path, recursive: bool) -> List[Path]:
        """Scan for Python files to check"""
        files = []

        if base_path.is_file():
            if base_path.suffix == '.py':
                files.append(base_path)
        elif base_path.is_dir():
            pattern = '**/*.py' if recursive else '*.py'
            files.extend(base_path.glob(pattern))

        # Filter out __pycache__ and .mypy_cache
        files = [f for f in files if '__pycache__' not in f.parts and '.mypy_cache' not in f.parts]

        return sorted(files)

    def run(self, base_path: Path, recursive: bool) -> int:
        """Run compilation checker"""
        print()
        print(f"{Colors.MAUVE}[pycompile]{Colors.NC} {Icons.FILE}  python compilation checker")
        print()
        log_info("Validating Python syntax by compiling to bytecode")
        print()

        files = self.scan_files(base_path, recursive)

        if not files:
            log_error("No Python files found")
            return 1

        log_info(f"checking {len(files)} Python file(s)")
        print()

        for filepath in files:
            self.check_file(filepath)
            print()

        # Print summary
        print(f"{Colors.MAUVE}summary{Colors.NC}")
        print()
        print(f"{Colors.TEXT}Total files checked:   {Colors.NC}{Colors.SAPPHIRE}{self.total_files}{Colors.NC}")
        print(f"{Colors.GREEN}Passed:                {Colors.NC}{Colors.SAPPHIRE}{self.passed_files}{Colors.NC}")

        if self.failed_files > 0:
            print(f"{Colors.RED}Failed:                {Colors.NC}{Colors.SAPPHIRE}{self.failed_files}{Colors.NC}")

        print()

        if self.failed_files > 0:
            log_error("Compilation check failed")
            return 1
        else:
            log_success("all files compiled")
            return 0


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Python compilation checker - validates Python syntax',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Check all Python files in current directory
  python3 pycompile.py

  # Check specific file
  python3 pycompile.py --path script.py

  # Check files in specific directory
  python3 pycompile.py --path /path/to/project

  # Check files recursively
  python3 pycompile.py --recursive --path /path/to/project
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to file or directory to check (default: current directory)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    args = parser.parse_args()

    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    checker = PyCompileChecker()
    return checker.run(base_path, args.recursive)


if __name__ == '__main__':
    sys.exit(main())
