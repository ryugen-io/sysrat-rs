# sysrat-rs - Task Completion Checklist

## Before Committing Code

### 1. Code Formatting
- [ ] Run `just fmt` to format Rust code
- [ ] Run `just htmlformat` if HTML was modified

### 2. Linting & Type Checks
- [ ] Run `just clippy` - Fix all warnings
- [ ] Run `just check` - Ensure compilation succeeds
- [ ] Run `just pylint` if Python was modified

### 3. Testing
- [ ] Run `just test` - All tests must pass
- [ ] Manual testing: Start server with `just start`, verify functionality

### 4. Security
- [ ] Run `just audit` for dependency security check

### 5. Quick Full Check
```bash
just pc          # Runs all pre-commit checks (verbose)
# or
just pc-summary  # Runs all pre-commit checks (summary)
```

## After Adding New Features

### Frontend Changes
- [ ] Verify WASM builds: `just rebuild-frontend`
- [ ] Test in browser at http://localhost:3000
- [ ] Check all keybinds work correctly
- [ ] Verify theme renders correctly

### Backend Changes
- [ ] Verify server builds: `just rebuild-backend`
- [ ] Test API endpoints with curl or browser
- [ ] Check error handling for edge cases

### New Dependencies
- [ ] Update `deny.toml` if new licenses are introduced
- [ ] Run `just audit` to check for vulnerabilities

## Before Creating PR

- [ ] Run `just all-checks` - All checks must pass
- [ ] Verify no uncommitted changes to generated files
- [ ] Test full rebuild: `just rebuild`
- [ ] Ensure server starts and runs correctly

## Code Review Checklist

- [ ] Follows naming conventions (PascalCase types, snake_case functions)
- [ ] No unused imports or dead code (unless `#[allow(dead_code)]`)
- [ ] Error messages are helpful and clear
- [ ] No hardcoded paths (use env vars or config)
- [ ] API changes are backward compatible or documented
