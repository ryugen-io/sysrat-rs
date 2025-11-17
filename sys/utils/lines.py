#!/usr/bin/env python3
"""
Line counter with detailed statistics
Analyzes source files and counts code, comment, and blank lines
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

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


# Comment patterns for different languages
COMMENT_PATTERNS = {
    'rs': [r'^\s*///?'],  # Rust: // or ///
    'sh': [r'^\s*#'],  # Shell: #
    'py': [r'^\s*#'],  # Python: #
    'js': [r'^\s*///?'],  # JavaScript: // or ///
    'ts': [r'^\s*///?'],  # TypeScript: // or ///
    'c': [r'^\s*///?'],  # C: // or ///
    'cpp': [r'^\s*///?'],  # C++: // or ///
    'go': [r'^\s*///?'],  # Go: // or ///
    'java': [r'^\s*///?'],  # Java: // or ///
}


class FileStats:
    """Statistics for a single file"""
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.total = 0
        self.code = 0
        self.comments = 0
        self.blank = 0


def count_lines(filepath: Path) -> FileStats:
    """Count lines in a file"""
    stats = FileStats(filepath)

    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')

        # Get comment pattern for this file type
        ext = filepath.suffix.lstrip('.')
        comment_patterns = COMMENT_PATTERNS.get(ext, [r'^\s*#'])  # Default to # comments

        for line in lines:
            stats.total += 1

            # Check if blank
            if re.match(r'^\s*$', line):
                stats.blank += 1
                continue

            # Check if comment
            is_comment = False
            for pattern in comment_patterns:
                if re.match(pattern, line):
                    stats.comments += 1
                    is_comment = True
                    break

            # Otherwise it's code
            if not is_comment:
                stats.code += 1

    except Exception as e:
        log_error(f"Error reading {filepath.name}: {e}")

    return stats


def scan_files(base_path: Path, types: List[str], recursive: bool, exclude_dirs: List[str]) -> List[Path]:
    """Scan for files to analyze"""
    files = []

    if base_path.is_file():
        files.append(base_path)
    elif base_path.is_dir():
        for ext in types:
            ext = ext.lstrip('*.')
            pattern = f'**/*.{ext}' if recursive else f'*.{ext}'
            matched_files = base_path.glob(pattern)

            # Filter out excluded directories
            for filepath in matched_files:
                should_exclude = False
                for exclude_dir in exclude_dirs:
                    if exclude_dir in filepath.parts:
                        should_exclude = True
                        break
                if not should_exclude:
                    files.append(filepath)

    return sorted(files)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Line counter with detailed statistics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Count lines in entire repository (recursive by default, excludes target/)
  python3 lines.py

  # Count lines in all Python files recursively
  python3 lines.py --types py

  # Count lines only in current directory (no recursion)
  python3 lines.py --no-recursive

  # Count lines with custom exclusions
  python3 lines.py --exclude target dist build

  # Count lines in multiple file types with custom limit
  python3 lines.py --types rs py sh js --limit 300
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to file or directory to analyze (default: current directory)'
    )

    parser.add_argument(
        '-t', '--types',
        nargs='+',
        default=['rs', 'py', 'sh'],
        help='File extensions to analyze (default: rs py sh)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        default=True,
        help='Search recursively in subdirectories (default: True)'
    )

    parser.add_argument(
        '--no-recursive',
        action='store_false',
        dest='recursive',
        help='Disable recursive search (only scan top-level directory)'
    )

    parser.add_argument(
        '-e', '--exclude',
        nargs='+',
        default=['target', '.git', 'node_modules', 'dist', '__pycache__', '.venv', 'venv'],
        help='Directories to exclude from scanning (default: target .git node_modules dist __pycache__ .venv venv)'
    )

    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=200,
        help='Line limit for warnings (default: 200)'
    )

    args = parser.parse_args()

    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    # Scan files
    files = scan_files(base_path, args.types, args.recursive, args.exclude)

    if not files:
        log_error(f"No files found matching types: {', '.join(args.types)}")
        return 1

    print()
    print(f"{Colors.MAUVE}[lines]{Colors.NC} {Colors.BLUE}{Icons.CHART}{Colors.NC} Analyzing lines of code...")
    print()
    log_info(f"Processing {len(files)} file(s) with limit: {args.limit} lines")
    print()

    # Analyze files
    file_stats = []
    for filepath in files:
        stats = count_lines(filepath)
        file_stats.append(stats)

    # Sort by code lines (descending)
    file_stats.sort(key=lambda s: s.code, reverse=True)

    # Calculate thresholds
    yellow_threshold = int(args.limit * 0.8)  # 80% of limit

    # Print file analysis
    print(f"{Colors.BLUE}{Icons.FILE}  File Analysis {Colors.SUBTEXT}(limit: {args.limit} lines, sorted by LOC):{Colors.NC}")
    print()

    over_limit = 0
    for stats in file_stats:
        # Color code by size
        if stats.code > args.limit:
            color = Colors.RED
            icon = Icons.WARN
            over_limit += 1
        elif stats.code > yellow_threshold:
            color = Colors.YELLOW
            icon = Icons.WARN
        else:
            color = Colors.GREEN
            icon = " "

        # Display relative path
        try:
            rel_path = stats.filepath.relative_to(base_path)
        except ValueError:
            rel_path = stats.filepath

        print(f"{color}{icon}  {stats.code:4d} lines{Colors.NC}  {Colors.SUBTEXT}{rel_path}{Colors.NC}")

    # Calculate totals
    total_files = len(file_stats)
    total_code = sum(s.code for s in file_stats)
    total_comments = sum(s.comments for s in file_stats)
    total_blank = sum(s.blank for s in file_stats)
    total_lines = sum(s.total for s in file_stats)

    max_code = max(s.code for s in file_stats) if file_stats else 0
    min_code = min(s.code for s in file_stats) if file_stats else 0
    max_file = max(file_stats, key=lambda s: s.code).filepath.name if file_stats else ""
    min_file = min(file_stats, key=lambda s: s.code).filepath.name if file_stats else ""

    avg_code = total_code // total_files if total_files > 0 else 0

    # Calculate percentages
    code_pct = (total_code / total_lines * 100) if total_lines > 0 else 0
    comment_pct = (total_comments / total_lines * 100) if total_lines > 0 else 0
    blank_pct = (total_blank / total_lines * 100) if total_lines > 0 else 0

    # Print summary
    print()
    print(f"{Colors.GREEN}{Icons.CHART}  Summary:{Colors.NC}")
    print()
    print(f"{Colors.TEXT}  Total files:     {Colors.NC}{total_files:6d}")
    print(f"{Colors.TEXT}  Code lines:      {Colors.NC}{total_code:6d} {Colors.SUBTEXT}({code_pct:.1f}%){Colors.NC}")
    print(f"{Colors.TEXT}  Comment lines:   {Colors.NC}{total_comments:6d} {Colors.SUBTEXT}({comment_pct:.1f}%){Colors.NC}")
    print(f"{Colors.TEXT}  Blank lines:     {Colors.NC}{total_blank:6d} {Colors.SUBTEXT}({blank_pct:.1f}%){Colors.NC}")
    print(f"{Colors.YELLOW}  Total lines:     {Colors.NC}{total_lines:6d}")
    print()
    print(f"{Colors.TEXT}  Average/file:    {Colors.NC}{avg_code:6d} {Colors.SUBTEXT}lines{Colors.NC}")
    print(f"{Colors.SAPPHIRE}  Largest file:    {Colors.NC}{max_code:6d} {Colors.SUBTEXT}lines{Colors.NC} {Colors.YELLOW}({max_file}){Colors.NC}")
    print(f"{Colors.GREEN}  Smallest file:   {Colors.NC}{min_code:6d} {Colors.SUBTEXT}lines{Colors.NC} {Colors.TEXT}({min_file}){Colors.NC}")
    print()

    # Check if we have files over the limit
    if over_limit > 0:
        log_warn(f"{over_limit} file(s) exceed {args.limit} lines")
    else:
        log_success(f"All files under {args.limit} lines!")

    print()
    log_success("Line count analysis complete!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
