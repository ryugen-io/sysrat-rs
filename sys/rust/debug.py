#!/usr/bin/env python3
"""
Debug Toggle Script - Dynamically enable/disable debug code in sysrat

This script searches for debug markers and toggles commented debug code.
Supports multiple debug marker patterns and automatically discovers all files.
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Add theme module to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'theme'))
from theme import Colors, Icons

# Debug marker patterns to search for
DEBUG_START_MARKER = r'//\s*\[DEBUG_START\]'
DEBUG_END_MARKER = r'//\s*\[DEBUG_END\]'

# File patterns to search (relative to repo root)
SEARCH_PATTERNS = [
    'frontend/src/**/*.rs',
    'server/src/**/*.rs',
]


class DebugToggler:
    """Manages debug code toggling in source files"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.stats = {
            'files_scanned': 0,
            'files_with_debug': 0,
            'debug_blocks_found': 0,
            'lines_toggled': 0,
        }

    def find_debug_files(self) -> List[Path]:
        """Find all files containing debug markers"""
        files_with_debug = []

        for pattern in SEARCH_PATTERNS:
            for file_path in self.repo_root.glob(pattern):
                if file_path.is_file():
                    self.stats['files_scanned'] += 1
                    if self.contains_debug_markers(file_path):
                        files_with_debug.append(file_path)
                        self.stats['files_with_debug'] += 1

        return files_with_debug

    def contains_debug_markers(self, file_path: Path) -> bool:
        """Check if file contains any debug markers"""
        try:
            content = file_path.read_text(encoding='utf-8')
            return bool(re.search(DEBUG_START_MARKER, content))
        except Exception as e:
            print(f"{Colors.RED}{Icons.CROSS}  {Colors.NC}Error reading {file_path}: {e}")
        return False

    def find_debug_blocks(self, lines: List[str]) -> List[Tuple[int, int, bool]]:
        """
        Find debug code blocks in file content using [DEBUG_START] and [DEBUG_END] markers

        Returns: List of (start_line, end_line, is_commented) tuples
        """
        blocks = []
        in_debug_block = False
        block_start = -1

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Check for DEBUG_START marker
            if re.search(DEBUG_START_MARKER, line):
                in_debug_block = True
                block_start = i + 1  # Debug code starts on next line
                continue

            # Check for DEBUG_END marker
            if re.search(DEBUG_END_MARKER, line):
                if in_debug_block and block_start >= 0:
                    # Determine if block is commented by checking first code line
                    is_commented = True
                    for j in range(block_start, i):
                        if j < len(lines):
                            check_line = lines[j].strip()
                            if check_line and not check_line.startswith('//'):
                                is_commented = False
                                break
                            elif check_line.startswith('//'):
                                # Found a commented line, block is commented
                                break

                    blocks.append((block_start, i - 1, is_commented))
                in_debug_block = False
                block_start = -1
                continue

        return blocks

    def toggle_debug_block(self, lines: List[str], start: int, end: int, is_commented: bool) -> int:
        """
        Toggle debug code block between commented and uncommented

        Returns: Number of lines toggled
        """
        toggled = 0

        for i in range(start, end + 1):
            if i >= len(lines):
                break

            line = lines[i]
            # Strip only the trailing newline for processing, but preserve it
            has_newline = line.endswith('\n')
            line_content = line.rstrip('\n')

            # Skip empty lines
            if not line_content.strip():
                continue

            if is_commented:
                # Uncomment: Remove "// " while preserving ALL whitespace
                # Match: (leading whitespace)(// )(rest of line)
                match = re.match(r'^(\s*)//\s?(.*)$', line_content)
                if match:
                    indent, code = match.groups()
                    new_line = f"{indent}{code}"
                    if has_newline:
                        new_line += '\n'
                    lines[i] = new_line
                    toggled += 1
            else:
                # Comment: Add "// " after leading whitespace, preserving ALL indentation
                # Match: (leading whitespace)(rest of line)
                match = re.match(r'^(\s*)(.*)$', line_content)
                if match:
                    indent, code = match.groups()
                    new_line = f"{indent}// {code}"
                    if has_newline:
                        new_line += '\n'
                    lines[i] = new_line
                    toggled += 1

        return toggled

    def process_file(self, file_path: Path, enable: bool) -> Dict[str, int]:
        """
        Process a single file and toggle debug code

        Args:
            file_path: Path to file
            enable: True to enable debug, False to disable

        Returns: Statistics dict with blocks_found and lines_toggled
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines(keepends=True)

            # Find all debug blocks
            blocks = self.find_debug_blocks(lines)

            if not blocks:
                return {'blocks_found': 0, 'lines_toggled': 0}

            # Toggle each block
            total_toggled = 0
            for start, end, is_commented in blocks:
                # Only toggle if state doesn't match desired state
                if (enable and is_commented) or (not enable and not is_commented):
                    toggled = self.toggle_debug_block(lines, start, end, is_commented)
                    total_toggled += toggled

            # Write back to file if changes were made
            if total_toggled > 0:
                new_content = ''.join(lines)
                file_path.write_text(new_content, encoding='utf-8')

            return {
                'blocks_found': len(blocks),
                'lines_toggled': total_toggled,
            }

        except Exception as e:
            print(f"{Colors.RED}{Icons.CROSS}  {Colors.NC}Error processing {file_path}: {e}")
            return {'blocks_found': 0, 'lines_toggled': 0}

    def toggle_all(self, enable: bool):
        """Toggle debug code in all files"""
        action = "enabling" if enable else "disabling"
        print(f"{Colors.MAUVE}[debug]{Colors.NC} {action} debug code")
        print()

        # Find all files with debug markers
        debug_files = self.find_debug_files()

        if not debug_files:
            print(f"{Colors.YELLOW}{Icons.WARN}  {Colors.NC}no debug markers found in project")
            return

        print(f"{Colors.BLUE}{Icons.INFO}  {Colors.NC}Found {len(debug_files)} files with debug markers")
        print()

        # Process each file
        for file_path in debug_files:
            rel_path = file_path.relative_to(self.repo_root)
            result = self.process_file(file_path, enable)

            if result['lines_toggled'] > 0:
                self.stats['debug_blocks_found'] += result['blocks_found']
                self.stats['lines_toggled'] += result['lines_toggled']

                status = "enabled" if enable else "disabled"
                print(f"{Colors.GREEN}{Icons.CHECK}  {Colors.NC}{rel_path}")
                print(f"    {Colors.SUBTEXT}→{Colors.NC} {result['blocks_found']} blocks, "
                      f"{result['lines_toggled']} lines {status}")
            elif result['blocks_found'] > 0:
                print(f"{Colors.SUBTEXT}  {rel_path} (already {action.lower()}){Colors.NC}")

        # Print summary
        print()
        print(f"{Colors.MAUVE}[summary]{Colors.NC}")
        print(f"  Files scanned:      {self.stats['files_scanned']}")
        print(f"  Files with debug:   {self.stats['files_with_debug']}")
        print(f"  Debug blocks found: {self.stats['debug_blocks_found']}")
        print(f"  Lines toggled:      {self.stats['lines_toggled']}")
        print()

        if self.stats['lines_toggled'] > 0:
            print(f"{Colors.GREEN}{Icons.CHECK}  {Colors.NC}debug code {action.lower()}")
            if enable:
                print(f"{Colors.YELLOW}{Icons.WARN}  {Colors.NC}rebuild required: {Colors.BLUE}./rebuild.py{Colors.NC}")
        else:
            print(f"{Colors.BLUE}{Icons.INFO}  {Colors.NC}no changes needed")


def show_status(repo_root: Path):
    """Show current debug status"""
    print(f"{Colors.MAUVE}[debug]{Colors.NC} checking status")
    print()

    toggler = DebugToggler(repo_root)
    debug_files = toggler.find_debug_files()

    if not debug_files:
        print(f"{Colors.YELLOW}{Icons.WARN}  {Colors.NC}no debug markers found in project")
        return

    print(f"{Colors.BLUE}{Icons.INFO}  {Colors.NC}Found {len(debug_files)} files with debug markers:")
    print()

    for file_path in debug_files:
        rel_path = file_path.relative_to(repo_root)
        content = file_path.read_text(encoding='utf-8')
        lines = content.splitlines()

        blocks = toggler.find_debug_blocks(lines)
        if blocks:
            enabled_blocks = sum(1 for _, _, commented in blocks if not commented)
            disabled_blocks = sum(1 for _, _, commented in blocks if commented)

            if enabled_blocks > 0:
                status_icon = f"{Colors.GREEN}{Icons.CHECK}"
                status_text = f"{Colors.GREEN}ENABLED"
            else:
                status_icon = f"{Colors.SUBTEXT}○"
                status_text = f"{Colors.SUBTEXT}disabled"

            print(f"{status_icon}  {Colors.NC}{rel_path}")
            print(f"    {Colors.SUBTEXT}→{Colors.NC} {len(blocks)} blocks "
                  f"({enabled_blocks} enabled, {disabled_blocks} disabled)")


def print_usage():
    """Print usage information"""
    print(f"{Colors.MAUVE}[debug]{Colors.NC} debug code toggle")
    print()
    print("Usage:")
    print(f"  {Colors.BLUE}python3 sys/rust/debug.py enable{Colors.NC}   - Enable debug code")
    print(f"  {Colors.BLUE}python3 sys/rust/debug.py disable{Colors.NC}  - Disable debug code")
    print(f"  {Colors.BLUE}python3 sys/rust/debug.py status{Colors.NC}   - Show current status")
    print()
    print("Or using just:")
    print(f"  {Colors.BLUE}just debug-enable{Colors.NC}")
    print(f"  {Colors.BLUE}just debug-disable{Colors.NC}")
    print(f"  {Colors.BLUE}just debug-status{Colors.NC}")
    print()


def main():
    """Main entry point"""

    # Find repository root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent

    # Parse command
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command in ['enable', 'on', 'activate']:
        toggler = DebugToggler(repo_root)
        toggler.toggle_all(enable=True)
    elif command in ['disable', 'off', 'deactivate']:
        toggler = DebugToggler(repo_root)
        toggler.toggle_all(enable=False)
    elif command in ['status', 'check', 'info']:
        show_status(repo_root)
    else:
        print(f"{Colors.RED}{Icons.CROSS}  {Colors.NC}Unknown command: {command}")
        print()
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
