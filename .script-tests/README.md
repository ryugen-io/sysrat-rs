# Shell Script Testing Tools

This directory contains testing and linting tools for the shell scripts in the project.

## Files

### `shellcheck_test.py`
Python-based advanced shell script linter (alternative to shellcheck).

**Features:**
- Syntax checking
- Shebang validation
- `set -e` and `set -o pipefail` detection
- Readonly variable usage checking
- Function local variable checking
- Uses Catppuccin Mocha color scheme

**Usage:**
```bash
python3 .script-tests/shellcheck_test.py
```

### `test_runner.py`
BATS-style test runner for shell scripts (pure Python implementation).

**Features:**
- Syntax validation for all shell scripts
- Executable permission checks
- Functional tests (e.g., help flags, output validation)
- Clean output with color-coded results
- Uses Catppuccin Mocha color scheme

**Usage:**
```bash
python3 .script-tests/test_runner.py
```

### `test_scripts.bats`
BATS (Bash Automated Testing System) test suite.

**Features:**
- Comprehensive test coverage for all shell scripts
- Syntax validation
- Functional tests
- Integration tests

**Usage:**
```bash
# If bats is installed:
bats .script-tests/test_scripts.bats

# Otherwise use test_runner.py as an alternative
```

## Running Tests

### Quick Test (using lint.sh in root)
```bash
./lint.sh
```

### Full Python Linting
```bash
python3 .script-tests/shellcheck_test.py
```

### Full Test Suite
```bash
python3 .script-tests/test_runner.py
```

## Test Coverage

All shell scripts are tested for:
- ✅ Valid bash syntax
- ✅ Proper shebang (`#!/bin/bash`)
- ✅ Error handling (`set -e`)
- ✅ Pipe safety (`set -o pipefail`)
- ✅ Executable permissions
- ✅ Functional correctness

## Adding New Tests

When adding new shell scripts to the project:

1. Add syntax check to `test_runner.py`
2. Add functional tests if the script has command-line flags
3. Run the test suite to ensure all tests pass

## Dependencies

- **Python 3.6+** (for Python-based tools)
- **BATS** (optional, for running .bats files directly)

No external dependencies required for the Python tools - they use only the standard library.
