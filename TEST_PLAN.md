# Shell Scripts Test Plan

This document describes the automated test suite for the Config Manager shell scripts (`rebuild.sh`, `start.sh`, `stop.sh`).

## Test Overview

The test suite validates that the shell scripts have been correctly updated with the Catppuccin Mocha color palette and follow consistent formatting standards.

## Running Tests

```bash
# Make the test script executable (if not already)
chmod +x test-scripts.sh

# Run all tests
./test-scripts.sh
```

## Test Cases

### 1. Executable Permissions
**Purpose**: Verify all scripts have executable permissions  
**Command**: `test -x <script>`  
**Expected**: All scripts should be executable

### 2. Shebang Validation
**Purpose**: Ensure scripts have correct bash shebang  
**Command**: `head -n 1 <script>`  
**Expected**: All scripts should start with `#!/bin/bash`

### 3. Catppuccin Mocha Color Palette
**Purpose**: Verify all required colors are defined with correct hex codes  
**Colors Tested**:
- RED (#f38ba8) - Error messages
- GREEN (#a6e3a1) - Success/Info messages
- YELLOW (#f9e2af) - Warning messages
- BLUE (#89b4fa) - Info highlights
- MAUVE (#cba6f7) - Headers
- SAPPHIRE (#74c7ec) - Success highlights

**Expected**: Each color definition must exist in all three scripts

### 4. True Color Support
**Purpose**: Verify scripts use 24-bit true color ANSI escape codes  
**Pattern**: `\033[38;2;R;G;Bm`  
**Expected**: All scripts should use 24-bit color codes instead of 8-bit or 16-bit

### 5. Consistent Tag Formatting
**Purpose**: Verify each script uses appropriate `[tag]` prefixes  
**Expected**:
- `rebuild.sh` uses `[rebuild]` tags
- `start.sh` uses `[start]` tags
- `stop.sh` uses `[stop]` tags

### 6. Logging Functions
**Purpose**: Verify all required logging functions are defined  
**Functions Tested**:
- `log_info()` - Info messages
- `log_warn()` - Warning messages
- `log_error()` - Error messages
- `log_success()` - Success messages

**Expected**: All four functions must exist in all three scripts

### 7. Syntax Validation
**Purpose**: Ensure scripts have valid bash syntax  
**Command**: `bash -n <script>`  
**Expected**: No syntax errors in any script

### 8. Help Output
**Purpose**: Test rebuild.sh help functionality  
**Command**: `./rebuild.sh --help`  
**Expected**: Help output should contain "Usage:" and "Options:" sections

### 9. Visual Color Preview
**Purpose**: Display color palette for manual verification  
**Expected**: Colors should render correctly in terminal with 24-bit color support

### 10. Security Best Practices
**Purpose**: Verify scripts follow security guidelines  
**Checks**:
- `set -e` is used (exit on error)
- Readonly variables are used for constants

**Expected**: All scripts should use `set -e` and readonly variables

## Test Results

After running `./test-scripts.sh`, you should see:

```
╔════════════════════════════════════════════════════════════╗
║   Test Summary                                             ║
╚════════════════════════════════════════════════════════════╝

Total Tests:  10
Passed:       10
Failed:       0

✓ All tests passed!
```

## Manual Verification

### Color Rendering Test

The test suite displays a visual preview of all colors. On a terminal with 24-bit color support, you should see:

- **RED** - Bright pink/red color for errors
- **GREEN** - Light green color for success
- **YELLOW** - Soft yellow color for warnings
- **BLUE** - Light blue color for info
- **MAUVE** - Purple/lavender color for headers
- **SAPPHIRE** - Cyan/aqua color for success highlights

### Sample Output Formats

```bash
[rebuild] Starting build process...
  Building backend...
[rebuild] Backend build successful
  Warning: Port may be in use
  Error: Build failed
  Server started successfully
```

### Testing Individual Scripts

```bash
# Test rebuild.sh color output
./rebuild.sh --help

# Test rebuild.sh full execution (requires dependencies)
./rebuild.sh --no-server

# Test start.sh output (shows colors when server is already running)
./start.sh

# Test stop.sh output
./stop.sh
```

## Terminal Requirements

For proper color rendering:
- Terminal must support 24-bit true color (most modern terminals do)
- Recommended terminals: iTerm2, Alacritty, Kitty, modern GNOME Terminal, Windows Terminal

## Continuous Integration

These tests are designed to run in CI/CD pipelines to ensure:
1. Scripts remain executable
2. Color definitions are not accidentally removed
3. Syntax remains valid
4. Formatting consistency is maintained

## Troubleshooting

### Colors don't render correctly
- Check if your terminal supports 24-bit color
- Try setting `COLORTERM=truecolor` environment variable
- Test with: `printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"`

### Tests fail on syntax check
- Run `bash -n <script>` to see specific syntax errors
- Check for unclosed quotes, missing semicolons, etc.

### Permission errors
- Ensure scripts have executable permissions: `chmod +x *.sh`
- Check file ownership if running in restricted environments

## Related Files

- `rebuild.sh` - Main build orchestration script
- `start.sh` - Server startup script  
- `stop.sh` - Server shutdown script
- `test-scripts.sh` - Automated test suite (this test runner)
- `CLAUDE.md` - Development guide with additional context

## Test Maintenance

When modifying shell scripts:
1. Run the test suite before committing changes
2. If adding new colors, update test case #3
3. If changing tag names, update test case #5
4. Keep this documentation synchronized with actual tests
