#!/usr/bin/env python3
"""
Pre-Commit Checks Wrapper
Runs all pre-commit checks with optional summary mode
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

# Import central theme
from theme import Colors, Icons, log_success, log_error, log_warn, log_info


class CheckResult:
    """Result of a single check"""
    def __init__(self, name: str, passed: bool, output: str = ""):
        self.name = name
        self.passed = passed
        self.output = output


def run_check(name: str, command: List[str], summary_mode: bool = False) -> CheckResult:
    """
    Run a single check command

    Args:
        name: Display name of the check
        command: Command to execute
        summary_mode: If True, capture output; if False, stream to stdout

    Returns:
        CheckResult with pass/fail status and captured output
    """
    try:
        if summary_mode:
            # Capture output for summary
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            passed = result.returncode == 0
            output = result.stdout + result.stderr
            return CheckResult(name, passed, output)
        else:
            # Stream output directly
            result = subprocess.run(command, check=False)
            passed = result.returncode == 0
            return CheckResult(name, passed, "")
    except Exception as e:
        return CheckResult(name, False, f"Error running check: {e}")


def extract_summary(output: str, check_name: str) -> str:
    """
    Extract relevant summary line from check output

    Looks for lines like:
    - "all projects formatted"
    - "1 project(s) clean"
    - "23 files passed"
    """
    lines = output.split('\n')

    # Look for summary indicators
    summary_keywords = [
        'all projects', 'all files', 'all checks', 'all tests',
        'project(s)', 'file(s)', 'passed', 'failed', 'clean',
        'formatted', 'compiled', 'valid', 'issues'
    ]

    for line in reversed(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in summary_keywords):
            # Strip ANSI codes and extra whitespace
            import re
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
            if clean_line and not clean_line.startswith('#'):
                return clean_line

    # Fallback: return last non-empty line
    for line in reversed(lines):
        import re
        clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
        if clean_line:
            return clean_line

    return "completed"


def extract_errors(output: str) -> List[str]:
    """Extract error messages from output"""
    lines = output.split('\n')
    error_lines = []

    # Look for error indicators
    error_keywords = ['error:', 'failed', 'warning:', 'issue']

    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in error_keywords):
            import re
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
            if clean_line:
                error_lines.append(clean_line)

    return error_lines[:10]  # Limit to first 10 error lines


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Run all pre-commit checks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Full output (verbose)
  python3 precommit.py --verbose
  just pc

  # Summary mode (compact)
  python3 precommit.py --summary
  just pc-summary
        '''
    )

    parser.add_argument(
        '-s', '--summary',
        action='store_true',
        help='Show summary only (compact output)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show full output (default)'
    )

    args = parser.parse_args()

    # Default to verbose if neither specified
    summary_mode = args.summary and not args.verbose

    # Define all checks
    checks = [
        ("rustfmt", ["python3", "sys/rust/rustfmt.py", "--recursive"]),
        ("clippy", ["python3", "sys/rust/clippy.py", "--recursive"]),
        ("check", ["python3", "sys/rust/check.py", "--recursive"]),
        ("test", ["python3", "sys/rust/test_rust.py", "--recursive"]),
        ("pylint", ["python3", "sys/utils/pylint.py", "--recursive"]),
        ("pycompile", ["python3", "sys/utils/pycompile.py", "--recursive"]),
        ("htmlformat", ["python3", "sys/html/htmlformat.py", "--recursive", "--check"]),
        ("htmllint", ["python3", "sys/html/htmllint.py", "--recursive"]),
        ("audit", ["python3", "sys/rust/audit.py", "--recursive"]),
    ]

    if summary_mode:
        print(f"\n{Colors.MAUVE}[precommit]{Colors.NC} running pre-commit checks...\n")

    # Run all checks
    results = []
    for name, command in checks:
        if summary_mode:
            print(f"{Colors.SUBTEXT}running {name}...{Colors.NC}", end='\r')

        result = run_check(name, command, summary_mode)
        results.append(result)

        if summary_mode:
            # Clear the "running..." line
            print(" " * 50, end='\r')

    # Display results
    if summary_mode:
        # Summary mode: compact output
        failed_checks = []

        for result in results:
            status_icon = Icons.CHECK if result.passed else Icons.CROSS
            status_color = Colors.GREEN if result.passed else Colors.RED

            # Extract summary from output
            summary = extract_summary(result.output, result.name)

            print(f"{status_color}{status_icon}{Colors.NC}  {Colors.MAUVE}[{result.name}]{Colors.NC} {summary}")

            if not result.passed:
                failed_checks.append(result)

        # Show errors section if any checks failed
        if failed_checks:
            print(f"\n{Colors.RED}errors{Colors.NC}\n")

            for result in failed_checks:
                print(f"{Colors.MAUVE}[{result.name}]{Colors.NC}")

                # Extract and show error lines
                errors = extract_errors(result.output)
                if errors:
                    for error in errors[:5]:  # Show first 5 errors
                        print(f"  {Colors.RED}{error}{Colors.NC}")
                    if len(errors) > 5:
                        print(f"  {Colors.SUBTEXT}... and {len(errors) - 5} more{Colors.NC}")
                else:
                    # Show last 10 lines if no specific errors found
                    lines = result.output.strip().split('\n')[-10:]
                    for line in lines:
                        print(f"  {Colors.SUBTEXT}{line}{Colors.NC}")
                print()

        # Final summary
        print(f"{Colors.GREEN}summary{Colors.NC}\n")
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)

        if passed_count == total_count:
            log_success(f"all {total_count} checks passed")
        else:
            failed_count = total_count - passed_count
            log_error(f"{failed_count} check(s) failed")
            print(f"  {Colors.SUBTEXT}run 'just pc' for full output{Colors.NC}")

        print()

        # Exit with error if any check failed
        return 1 if failed_checks else 0
    else:
        # Verbose mode: checks already printed their output
        # Just return exit code based on results
        failed = sum(1 for r in results if not r.passed)
        return 1 if failed > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
