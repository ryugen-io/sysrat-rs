# Security Configuration

This directory contains security-related configuration files for CI workflows.

## Files

### `secrets-patterns.txt` (Optional)

Add custom secret patterns for git-secrets to detect:

```
# Example patterns
custom-api-key-[0-9a-zA-Z]{32}
MY_COMPANY_SECRET_[A-Z0-9]+
```

## Secret Scanning

The security workflow includes three layers of secret scanning:

1. **git-secrets**: Scans for AWS credentials and custom patterns
2. **detect-secrets**: Creates a baseline and detects new secrets
3. **TruffleHog**: Scans repository history for verified secrets

All three secret scanning jobs **ALWAYS run** and cannot be skipped.

## Adding Custom Patterns

Create a `secrets-patterns.txt` file in this directory:

```bash
cat > .github/security/secrets-patterns.txt << 'EOF'
# Custom API keys
custom-api-[0-9a-zA-Z]{40}

# Internal tokens
INTERNAL_TOKEN_[A-Z0-9]{32}
EOF
```

Then commit:

```bash
git add .github/security/secrets-patterns.txt
git commit -m "security: add custom secret patterns"
git push
```
