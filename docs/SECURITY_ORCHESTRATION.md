# Security Orchestration System

## Overview

The Security Orchestration System prevents critical security issues (like hardcoded secrets) from entering the codebase through comprehensive, automated security validation integrated into every stage of the development workflow.

## Architecture

```
🔒 Security Orchestration Flow:

Developer → Pre-commit Hook → Security Validation → Commit/Block
                               ↓
GitHub Actions → Security Scan → PR Status Check
                               ↓  
Alembic System → Continuous Monitoring → Auto-Response
                               ↓
Reports & Alerts → Human Review → Resolution
```

## Components

### 1. Security Orchestrator (`scripts/orchestration/security_orchestrator.py`)

**Core security scanning engine with multiple detection methods:**

- **Secret Detection**: 8 pattern types for hardcoded credentials
- **Dependency Scanning**: Vulnerability detection in requirements.txt
- **Code Quality**: Security anti-patterns (eval, exec, shell injection)
- **Configuration**: Insecure configuration detection

**Key Features:**
- Shannon entropy analysis for secret detection
- GDPR-compliant pattern whitelisting
- Confidence scoring for findings
- JSON report generation

### 2. Pre-commit Hook (`scripts/git-hooks/pre-commit-security`)

**Blocks commits with critical security issues:**

```python
# Automatically runs on: git commit
# Validates: All staged files
# Action: Block critical issues, warn on high severity
# Reports: Saves to reports/security/pre_commit_validation.json
```

**Installation:**
```bash
python scripts/setup_security_orchestration.py
```

### 3. GitHub Actions Workflow (`.github/workflows/security-orchestration.yml`)

**Comprehensive CI/CD security scanning:**

- **Triggers**: All PRs, daily at 2 AM UTC, manual dispatch
- **Tools**: Safety, Bandit, Semgrep, GitLeaks, TruffleHog
- **Actions**: Security reports, issue creation, Slack alerts
- **Artifacts**: 30-day report retention

**Scan Types:**
- `full`: Complete security analysis
- `secrets_only`: Focused secret detection
- `dependencies_only`: Vulnerability scanning
- `quick`: Fast pre-merge validation

### 4. Alembic Integration

**Real-time security monitoring during autonomous operation:**

```python
# Runs every hour during Alembic execution
# Pauses operations if critical issues found
# Generates detailed security reports
# Integrates with event-driven responses
```

## Security Detection Patterns

### Secret Detection Patterns

| Pattern Type | Regex | Severity | Example |
|--------------|--------|----------|---------|
| Generic Password | `(password\|pwd)\s*=\s*["\']?([a-zA-Z0-9]{8,})` | CRITICAL | `password="secret123"` |
| API Key | `(api[_-]?key)\s*=\s*["\']?([a-zA-Z0-9]{20,})` | CRITICAL | `api_key="sk-abc123"` |
| JWT Token | `eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+` | HIGH | JWT format |
| AWS Access Key | `AKIA[0-9A-Z]{16}` | CRITICAL | AWS key format |
| Private Key | `-----BEGIN.*PRIVATE KEY-----` | CRITICAL | PEM format |

### Code Quality Patterns

| Pattern | Description | Severity | Recommendation |
|---------|-------------|----------|----------------|
| `eval()` | Code injection risk | HIGH | Use `ast.literal_eval()` |
| `exec()` | Code injection risk | HIGH | Avoid dynamic execution |
| `shell=True` | Command injection | MEDIUM | Use `shell=False` |
| `pickle.loads` | Deserialization attack | MEDIUM | Use JSON instead |

## Configuration

### Security Config (`scripts/orchestration/security_config.json`)

```json
{
  "enabled_checks": ["secret_detection", "dependency_scan", "code_quality"],
  "severity_threshold": "medium",
  "fail_on_critical": true,
  "secret_detection": {
    "entropy_threshold": 4.5,
    "whitelist_files": [".env.example", "docs/*"],
    "whitelist_values": ["default-dev-key", "placeholder"]
  }
}
```

### Environment Variables

```bash
# Required for production
ENCRYPTION_PASSWORD=<32-character-password>
ENCRYPTION_SALT=<32-character-salt>

# Optional notifications
SLACK_WEBHOOK_URL=<webhook-url>
```

## Usage

### Setup (One-time)

```bash
# Install security orchestration
python scripts/setup_security_orchestration.py

# Verify installation
git commit -m "test" --dry-run  # Should show security validation
```

### Manual Security Scans

```bash
# Full security scan
python scripts/orchestration/security_orchestrator.py

# Quick validation of staged files
python scripts/git-hooks/pre-commit-security

# View latest reports
ls -la reports/security/
cat reports/security/security_report_*.json
```

### GitHub Actions

```bash
# Trigger manual security scan
gh workflow run security-orchestration.yml -f scan_type=full

# View security artifacts
gh run list --workflow=security-orchestration.yml
gh run download <run-id>
```

## Security Workflow

### 1. Development Phase

```
Developer writes code → Pre-commit hook validates → Commit allowed/blocked
```

**If blocked:**
1. Review security report in `reports/security/pre_commit_validation.json`
2. Fix critical issues (move secrets to environment variables)
3. Re-attempt commit

### 2. PR Phase

```
PR created → GitHub Actions security scan → Status check → Merge allowed/blocked
```

**If failed:**
1. Check workflow artifacts for detailed reports
2. Address all critical and high severity issues
3. Push fixes to trigger re-scan

### 3. Production Phase

```
Code deployed → Alembic continuous monitoring → Auto-pause if critical issues
```

**If critical issues found:**
1. Operations temporarily paused
2. Alert saved to `reports/security/CRITICAL_ALERT.txt`
3. Slack/email notifications sent (if configured)
4. Human intervention required

## Reports and Monitoring

### Report Types

1. **Pre-commit Validation**
   - File: `reports/security/pre_commit_validation.json`
   - Contains: Staged files, issues found, safety status

2. **GitHub Actions Security Report**
   - File: `reports/security/github_actions_security_report.json`
   - Contains: Combined tool outputs, workflow metadata

3. **Alembic Security Report**
   - File: `reports/security/alembic_security_report_*.json`
   - Contains: Runtime security status, continuous monitoring results

### Critical Alert Format

```
CRITICAL SECURITY ISSUES DETECTED:

• Potential Generic Password found: secret123...
  File: src/example.py
  Fix: Move generic password to environment variable

• Potential API Key found: sk-abc123...
  File: config/settings.py
  Fix: Move api key to environment variable
```

## Troubleshooting

### Common Issues

1. **"Security orchestrator not available"**
   - **Solution**: Run `python scripts/setup_security_orchestration.py`

2. **Pre-commit hook not running**
   - **Solution**: Check `.git/hooks/pre-commit` exists and is executable

3. **False positives in secret detection**
   - **Solution**: Add patterns to `whitelist_files` or `whitelist_values` in config

4. **GitHub Actions security scan failing**
   - **Solution**: Check workflow artifacts for detailed error reports

### Emergency Override

If you need to bypass security validation in an emergency:

```bash
# ONLY for emergencies - bypasses pre-commit hook
git commit -m "emergency fix" --no-verify

# Immediately run security scan after
python scripts/orchestration/security_orchestrator.py
```

## Best Practices

### For Developers

1. **Never commit secrets**: Use environment variables for all sensitive data
2. **Review security reports**: Address issues promptly, don't ignore warnings
3. **Use .env.example**: Template files for required environment variables
4. **Regular scans**: Run manual security scans before major releases

### For Operations

1. **Monitor security reports**: Review daily security scan results
2. **Keep tools updated**: Regularly update security scanning dependencies
3. **Configure notifications**: Set up Slack/email alerts for critical issues
4. **Incident response**: Have procedures for critical security alerts

## Integration with Existing Tools

### GitGuardian
- **Relationship**: Complementary - GitGuardian provides external monitoring
- **Our system**: Provides internal, pre-commit validation
- **Combined**: Complete coverage from development to production

### IDE Security Plugins
- **SonarLint**: Code quality analysis in IDE
- **Security extensions**: Real-time vulnerability detection
- **Our system**: Final validation layer before commit

## Metrics and KPIs

### Security Metrics Tracked

1. **Issues Prevented**: Critical issues blocked at pre-commit
2. **Response Time**: Time from detection to resolution
3. **False Positive Rate**: Accuracy of security pattern detection
4. **Coverage**: Percentage of codebase scanned

### Success Indicators

- **Zero critical issues** in production deployments
- **< 2% false positive rate** in secret detection
- **< 1 hour response time** for critical security alerts
- **100% pre-commit coverage** for all developers

The security orchestration system ensures that critical security issues like hardcoded passwords are caught and prevented automatically, maintaining the highest security standards throughout the development lifecycle! 🛡️