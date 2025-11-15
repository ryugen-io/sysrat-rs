# CI/CD Workflows Documentation

This directory contains GitHub Actions workflows for continuous integration and continuous deployment.

## Workflows Overview

### 🔧 Main CI Workflow (`ci.yml`)

The primary continuous integration workflow for Rust projects.

**Triggers:**
- Push to `master`, `main`, `develop` branches
- Pull requests to `master`, `main`, `develop` branches

**Jobs:**
- **Format Check** (`fmt`): Runs `cargo fmt` with auto-fix and commit
- **Linting** (`clippy`): Runs `cargo clippy` on backend and frontend
- **Build** (`build`): Multi-architecture builds (x86_64, aarch64, GNU/musl)
  - Builds backend with `cargo-auditable` for security
  - Builds frontend WASM with Trunk (x86_64 only)
  - Optional UPX compression (controlled by `.github/upx/` flags)
- **Test** (`test`): Runs unit tests, integration tests, and doc tests
- **Benchmark** (`bench`): Compiles benchmarks to ensure they build
- **Security Audit** (`audit`): Uses `cargo-audit` to check for vulnerabilities
- **Dependency Policy** (`deny`): Uses `cargo-deny` to enforce dependency policies

**Features:**
- Granular skip control via `.github/skips/` flag files
- Rust file change detection (only runs when Rust files change)
- Multi-architecture build matrix
- Frontend/Backend support with separate checks
- Build artifacts uploaded for each architecture

---

### 📊 Coverage Workflow (`ci-coverage.yml`)

Generates code coverage reports and uploads to Codecov.

**Triggers:**
- Push to `master`, `main`, `develop` branches
- Pull requests to `master`, `main`, `develop` branches

**Jobs:**
- Format, Clippy, Test, Benchmark (same as main CI)
- **Coverage** (`coverage`): Generates coverage with `cargo-tarpaulin`
  - Uploads to Codecov (requires `CODECOV_TOKEN` secret)
  - Archives coverage report as artifact

**Requirements:**
- Set `CODECOV_TOKEN` in repository secrets for coverage upload

---

### 🔒 Security Scan Workflow (`security-scan.yml`)

Comprehensive security scanning across multiple layers.

**Triggers:**
- Push to `master`, `main`, `develop` branches
- Pull requests to `master`, `main`, `develop` branches
- Daily schedule at 2 AM UTC
- Manual trigger (`workflow_dispatch`)

**Jobs:**

#### Skippable Security Jobs
- **Dependency Review** (`dependency-review`): Reviews dependencies in PRs
- **Rust Security** (`rust-security`): `cargo-audit` + `cargo-deny`
- **NPM Security** (`npm-security`): NPM audit + Snyk (if `package.json` exists)
- **Python Security** (`python-security`): Safety + Bandit (if Python files exist)
- **CodeQL** (`codeql`): Static analysis with GitHub CodeQL
- **Container Scan** (`container-scan`): Trivy scan (if `Dockerfile` exists)
- **License Check** (`license-check`): Validates dependency licenses

#### CRITICAL: Always-Run Secret Scanning
These jobs **CANNOT be skipped** and protect against accidental credential commits:
- **git-secrets**: Detects AWS keys, API credentials, tokens, private keys
- **detect-secrets**: Creates baseline and identifies credential exposure
- **TruffleHog**: Scans repository history for verified secrets

**Important:**
- Secret scanning jobs run on **every push** regardless of skip flags
- Failures indicate potential credential leaks - investigate immediately

---

### 🤖 AI Bot Mentions Workflow (`ai-bot-mentions.yml`)

Template for AI-powered bot integration in issues and PRs.

**Triggers:**
- Issue comments created
- Issues opened/edited
- Pull requests opened/edited
- PR review comments created

**Features:**
- Detects `@ai-bot` mentions in comments and issue/PR bodies
- Extracts command after mention
- Posts acknowledgment comment
- Template for AI service integration (Claude, ChatGPT, custom APIs)
- Error handling with user feedback

**Configuration:**
- Edit `env.BOT_MENTION` to change trigger phrase
- Implement AI integration in `Call AI Service` step
- Add API keys as repository secrets

---

### 🚀 Release Workflow (`release.yml`)

Builds release binaries with optimizations.

**Triggers:**
- Git tags matching `v*` (e.g., `v1.0.0`)
- Manual trigger (`workflow_dispatch`)

**Jobs:**
- Builds optimized release binaries for multiple targets
- Builds frontend WASM bundle
- Compresses with UPX for smaller artifacts
- Creates GitHub release with attached binaries

---

## Skip Control System

Control CI execution with flag files in `.github/skips/`:

### Global Skip
- `.skip-ci` - Skips ALL CI jobs (except critical security scans)

### Individual Job Skips
- `.skip-fmt` / `.skip-format` - Skip formatting
- `.skip-clippy` / `.skip-lint` - Skip linting
- `.skip-build` - Skip builds
- `.skip-test` / `.skip-tests` - Skip tests
- `.skip-bench` / `.skip-benchmark` - Skip benchmarks
- `.skip-audit` / `.skip-security` - Skip security audits
- `.skip-deny` - Skip cargo-deny
- `.skip-ai-bot` / `.skip-bot` - Skip AI bot workflow

### Usage

**Local skip (not committed):**
```bash
touch .github/skips/.skip-test
# Run CI - tests will be skipped locally
# File is gitignored, won't affect others
```

**Repository skip (committed):**
```bash
touch .github/skips/.skip-test
git add .github/skips/.skip-test
git commit -m "ci: skip tests temporarily"
git push
# CI skips tests for everyone until removed
```

See `.github/skips/README.md` for detailed documentation.

---

## UPX Compression

Enable binary compression with flag files in `.github/upx/`:

- `.enable-upx` - Enable for ALL architectures
- `.enable-upx-x86_64` - Enable for x86_64 only
- `.enable-upx-arm` - Enable for ARM64/aarch64 only

**Example:**
```bash
touch .github/upx/.enable-upx-x86_64
git add .github/upx/.enable-upx-x86_64
git commit -m "build: enable UPX compression for x86_64"
git push
```

See `.github/upx/README.md` for more information.

---

## Architecture Overview

```
.github/
├── workflows/
│   ├── ci.yml                 # Main CI workflow
│   ├── ci-coverage.yml        # Coverage reporting
│   ├── security-scan.yml      # Security scanning
│   ├── ai-bot-mentions.yml    # AI bot integration
│   └── release.yml            # Release builds
├── skips/
│   ├── .gitkeep
│   ├── README.md              # Skip control documentation
│   └── .skip-* (gitignored)   # Skip flag files
├── upx/
│   ├── .gitkeep
│   ├── README.md              # UPX documentation
│   └── .enable-upx* (gitignored)  # UPX flag files
└── security/
    ├── .gitkeep
    ├── README.md              # Security configuration
    └── secrets-patterns.txt   # Custom secret patterns (optional)
```

---

## Multi-Architecture Support

The CI builds for the following targets:
- `x86_64-unknown-linux-gnu` - Standard Linux (glibc)
- `x86_64-unknown-linux-musl` - Static Linux (musl)
- `aarch64-unknown-linux-gnu` - ARM64 Linux (glibc)
- `aarch64-unknown-linux-musl` - ARM64 Linux (musl)

Frontend WASM builds only on `x86_64-unknown-linux-gnu` to save CI time.

---

## Frontend Integration

The CI has special handling for the frontend (Yew/WASM):

### Format Check
- Backend: `cargo fmt --all`
- Frontend: `cd frontend && cargo fmt --all`

### Linting
- Backend: `cargo clippy --all-targets --all-features`
- Frontend: `cd frontend && cargo clippy --all-targets --all-features`

### Build
- Backend: Multi-arch with `cargo-auditable` / `cross`
- Frontend: `trunk build --release` (x86_64 only)
  - Installs Trunk automatically
  - Adds `wasm32-unknown-unknown` target
  - Outputs to `frontend/dist/`

### Test
- Backend: `cargo test --all-features --all`
- Frontend: `cd frontend && cargo test --all-features`

---

## Required Secrets

Configure these in repository settings:

- `CODECOV_TOKEN` - For coverage upload (ci-coverage.yml)
- `SNYK_TOKEN` - For Snyk scanning (security-scan.yml, optional)

---

## Best Practices

1. **Use skip flags sparingly** - Only for emergencies or known failures
2. **Never skip security scans** - They protect against credential leaks
3. **Document skip reasons** - Always explain why in commit messages
4. **Remove skip flags ASAP** - Don't leave them committed longer than needed
5. **Test locally first** - Use `cargo test`, `cargo clippy` before pushing
6. **Enable UPX for releases** - Keep disabled during development
7. **Review security scan results** - Daily scans catch new vulnerabilities

---

## Troubleshooting

### CI is not running
- Check for `.github/skips/.skip-ci` file
- Verify branch name matches trigger branches
- Check if only non-code files changed (e.g., only `.md` files)

### Formatting job fails
- Run `cargo fmt --all` locally
- Run `cd frontend && cargo fmt --all` locally
- Commit the formatted code

### Clippy job fails
- Run `cargo clippy --all-targets --all-features` locally
- Fix warnings or add `#[allow(clippy::...)]` if intentional
- Frontend: `cd frontend && cargo clippy --all-targets --all-features`

### Build job fails
- Check if all dependencies are in `Cargo.toml`
- For cross-compilation issues, test with `cross` locally
- Verify frontend builds: `cd frontend && trunk build`

### Secret scanning fails
- Review the detected pattern
- If false positive, add to `.secrets.baseline` and audit
- If real secret, rotate immediately and update repository

### Coverage upload fails
- Verify `CODECOV_TOKEN` is set in repository secrets
- Check Codecov service status
- Review workflow logs for specific error

---

## Integration with ryugen-io/.ci-workflows

These workflows are based on the standard templates from [ryugen-io/.ci-workflows](https://github.com/ryugen-io/.ci-workflows):

- `rust/standard/ci.yml` → `ci.yml` (with frontend integration)
- `rust/coverage/ci-coverage.yml` → `ci-coverage.yml` (with frontend tests)
- `general/security/security-scan.yml` → `security-scan.yml`
- `general/bots/ai-bot-mentions.yml` → `ai-bot-mentions.yml`

**Customizations:**
- Added frontend/WASM build support (Trunk)
- Separate backend/frontend format and clippy checks
- Frontend tests integrated into test job
- Frontend artifacts uploaded alongside backend

---

## Maintenance

To update workflows from upstream:

```bash
# Fetch latest templates
curl -O https://raw.githubusercontent.com/ryugen-io/.ci-workflows/main/rust/standard/ci.yml

# Review changes
diff ci.yml .github/workflows/ci.yml

# Merge updates manually, preserving frontend customizations
```

**Important:** Always preserve frontend-specific steps when merging updates!

---

For questions or issues, please refer to the [.ci-workflows documentation](https://github.com/ryugen-io/.ci-workflows).
