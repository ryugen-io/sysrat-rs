# CI Skip Files

This directory contains flag files to control CI/CD workflow execution.

## How It Works

The presence of specific files in this directory will skip certain CI jobs:

### Global Skip

- `.skip-ci` - Skips **ALL** CI jobs (except critical security scans)

### Individual Job Skips

- `.skip-fmt` or `.skip-format` - Skip code formatting checks
- `.skip-clippy` or `.skip-lint` - Skip linting (clippy) checks
- `.skip-build` - Skip build jobs
- `.skip-test` or `.skip-tests` - Skip test execution
- `.skip-bench` or `.skip-benchmark` - Skip benchmark compilation checks
- `.skip-audit` or `.skip-security` - Skip security audit jobs
- `.skip-deny` - Skip cargo-deny dependency policy checks
- `.skip-ai-bot` or `.skip-bot` - Skip AI bot mention workflow

## Usage Examples

### Skip all CI temporarily

```bash
touch .github/skips/.skip-ci
git add .github/skips/.skip-ci
git commit -m "ci: temporarily disable CI"
git push
```

### Skip only tests during development

```bash
touch .github/skips/.skip-test
git add .github/skips/.skip-test
git commit -m "ci: skip tests temporarily"
git push
```

### Re-enable all CI

```bash
rm .github/skips/.skip-ci
git add .github/skips/.skip-ci
git commit -m "ci: re-enable CI"
git push
```

## Important Notes

1. **Secret Scanning ALWAYS Runs**: The following security jobs cannot be skipped:
   - `git-secrets`
   - `detect-secrets`
   - `trufflehog-scan`

2. **Skip Files Must Be Committed**: To skip CI on GitHub Actions, you MUST commit the skip files to the repository. They are NOT gitignored.

## Best Practices

- Use global `.skip-ci` sparingly - only for emergencies or major repository changes
- Prefer individual job skips when you know specific jobs will fail
- **Always commit skip files** - they must be in the repository to work on GitHub Actions
- Always document why you're skipping CI in your commit message
- Remove skip files as soon as the issue is resolved
- Never skip security scans unless absolutely necessary and you understand the risks

## Note

Skip files are **NOT gitignored** and will be tracked in the repository when committed. This is intentional - CI runs on GitHub Actions and needs to see these files.
