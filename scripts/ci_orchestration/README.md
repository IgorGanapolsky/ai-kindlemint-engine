# CI Orchestration System

An autonomous CI/CD orchestration system that monitors, analyzes, and automatically fixes CI failures in the ai-kindlemint-engine repository.

## 🎯 Overview

The CI Orchestration System provides:

- **Automated CI Monitoring**: Polls GitHub Actions API for failed workflows
- **Intelligent Failure Analysis**: Categorizes failures and determines root causes
- **Automatic Fix Application**: Implements fixes for common issues
- **Validation & Testing**: Ensures fixes don't break the build
- **Git Integration**: Creates commits and pull requests automatically
- **Notification System**: Alerts via Slack, email, or GitHub issues

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CI Monitor    │───▶│   CI Analyzer   │───▶│    CI Fixer     │
│                 │    │                 │    │                 │
│ • Poll GitHub   │    │ • Parse logs    │    │ • Apply fixes   │
│ • Detect fails  │    │ • Categorize    │    │ • Run commands  │
│ • Extract logs  │    │ • Suggest fix   │    │ • Modify files  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                  ┌─────────────────────────────┐
                  │      CI Orchestrator        │
                  │                             │
                  │ • Coordinate components     │
                  │ • Manage configuration      │
                  │ • Handle git operations     │
                  │ • Send notifications        │
                  └─────────────────────────────┘
```

## 📁 Components

### Core Scripts

- **`ci_monitor.py`** - Monitors GitHub Actions for failures
- **`ci_analyzer.py`** - Analyzes failures and suggests fixes
- **`ci_fixer.py`** - Implements automated fixes
- **`ci_orchestrator.py`** - Main orchestration logic
- **`config.json`** - Configuration settings

### GitHub Actions

- **`.github/workflows/ci_autofixer.yml`** - Automated workflow trigger

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies
pip install requests PyGithub autopep8 black isort flake8 mypy

# Set GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Navigate to orchestration directory
cd scripts/ci_orchestration
```

### 2. Run Single Analysis

```bash
# Analyze recent CI failures (dry run)
python ci_orchestrator.py --mode single --dry-run

# Apply fixes with high confidence threshold
python ci_orchestrator.py --mode single --confidence-threshold 0.9
```

### 3. Continuous Monitoring

```bash
# Start continuous monitoring
python ci_orchestrator.py --mode continuous --max-cycles 10

# Background monitoring with custom interval
nohup python ci_orchestrator.py --mode continuous &
```

## 🔧 Configuration

### Basic Configuration (`config.json`)

```json
{
  "monitoring": {
    "lookback_minutes": 60,
    "check_interval_seconds": 300,
    "max_failures_per_run": 20
  },
  "fixing": {
    "max_fixes_per_run": 10,
    "auto_fix_confidence_threshold": 0.8,
    "enable_auto_commit": false,
    "enable_auto_pr": false
  }
}
```

### Environment Variables

- `GITHUB_TOKEN` - GitHub API token with repo permissions
- `SLACK_WEBHOOK_URL` - Optional Slack webhook for notifications

## 🔍 Supported Fix Types

### Automatic Fixes (High Confidence)

- **Import Errors**: Add missing packages to requirements.txt
- **Syntax Errors**: Fix common Python syntax issues
- **Linting Issues**: Run Black, isort, autopep8
- **Missing Files**: Create missing directories and files
- **Type Errors**: Add basic type annotations

### Semi-Automatic Fixes (Medium Confidence)

- **Test Failures**: Update assertion values
- **Dependency Conflicts**: Update pinned versions
- **Path Issues**: Fix import paths

### Manual Review Required (Low Confidence)

- **Complex Logic Errors**: Require human intervention
- **Test Data Updates**: Context-specific changes
- **Architecture Changes**: Structural modifications

## 📊 Usage Examples

### Monitor Recent Failures

```bash
# Check last 2 hours for failures
python ci_monitor.py --lookback 120 --output recent_failures.json

# Monitor specific workflows
python ci_monitor.py --workflow-filter "Tests,QA Validation"
```

### Analyze Specific Failure

```bash
# Analyze failure report
python ci_analyzer.py --input ci_failures.json --output analysis.json

# Get detailed analysis
python ci_analyzer.py --input ci_failures.json --verbose
```

### Apply Targeted Fixes

```bash
# Apply only linting fixes
python ci_fixer.py --analysis ci_analysis.json --fix-types "run_black,run_isort"

# Apply fixes with validation
python ci_fixer.py --analysis ci_analysis.json --validate-after-fix
```

## 🔒 Safety Features

### Validation Steps

1. **Syntax Validation**: Ensure Python files are valid
2. **Import Testing**: Verify imports work correctly
3. **Unit Testing**: Run subset of tests
4. **Linting Checks**: Ensure code style compliance

### Rollback Mechanisms

- **Git Stash**: Automatic stashing before fixes
- **Backup Files**: Create `.bak` files for modified files
- **Validation Failure**: Automatic rollback on test failures

### Permission Controls

- **Confidence Thresholds**: Only apply high-confidence fixes
- **File Type Restrictions**: Limit modifications to safe file types
- **Command Whitelisting**: Only run approved commands

## 📈 Monitoring & Reporting

### Metrics Tracked

- **Failure Detection Rate**: % of failures caught
- **Fix Success Rate**: % of fixes that work
- **Time to Resolution**: Average fix application time
- **False Positive Rate**: % of incorrect fix attempts

### Reports Generated

- **Failure Analysis Report**: Detailed breakdown of issues
- **Fix Application Report**: What fixes were applied
- **Validation Report**: Test results after fixes
- **Trend Analysis**: Patterns in CI failures

## 🔔 Notifications

### Slack Integration

```json
{
  "notifications": {
    "slack_webhook": "https://hooks.slack.com/services/...",
    "notify_on_success": true,
    "notify_on_failure": true
  }
}
```

### GitHub Integration

- **Commit Comments**: Summary on relevant commits
- **Issue Creation**: For failures requiring manual review
- **PR Comments**: Status updates on pull requests

## 🐛 Troubleshooting

### Common Issues

**GitHub API Rate Limiting**
```bash
# Check rate limit status
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit
```

**Permission Errors**
```bash
# Verify token permissions
python -c "
import requests
headers = {'Authorization': 'token YOUR_TOKEN'}
r = requests.get('https://api.github.com/user', headers=headers)
print(r.json())
"
```

**Module Import Issues**
```bash
# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Debug Mode

```bash
# Enable debug logging
python ci_orchestrator.py --mode single --debug

# Verbose output
python ci_orchestrator.py --mode single --verbose --dry-run
```

## 🔧 Development

### Adding New Fix Types

1. **Add Pattern Recognition** in `ci_analyzer.py`:
```python
'new_error_type': {
    'patterns': [r'YourErrorPattern: (.+)'],
    'analyzer': self._analyze_new_error
}
```

2. **Implement Fix Method** in `ci_fixer.py`:
```python
def _fix_new_error(self, strategy: Dict) -> bool:
    # Implementation here
    return success
```

3. **Add Configuration** in `config.json`:
```json
{
  "fixing": {
    "safe_fix_types": ["new_error_type"]
  }
}
```

### Testing

```bash
# Run unit tests
python -m pytest tests/test_ci_orchestration.py

# Integration tests
python -m pytest tests/test_ci_integration.py

# Test with mock data
python ci_orchestrator.py --mode single --dry-run --test-data fixtures/
```

## 📚 API Reference

### CIMonitor

```python
monitor = CIMonitor('owner', 'repo', 'token')
failures = monitor.monitor_failures(lookback_minutes=60)
report = monitor.save_failure_report(failures)
```

### CIAnalyzer

```python
analyzer = CIAnalyzer(repo_path)
analysis = analyzer.analyze_failure_report('failures.json')
strategies = analyzer.prioritize_strategies(analysis)
```

### CIFixer

```python
fixer = CIFixer(repo_path, dry_run=True)
success = fixer.apply_fix_strategy(strategy)
report = fixer.generate_fix_report()
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-fix-type`
3. **Add tests**: Ensure new fixes are tested
4. **Update documentation**: Add examples and usage notes
5. **Submit pull request**: Include detailed description

## 📄 License

This CI orchestration system is part of the ai-kindlemint-engine project and follows the same licensing terms.

## 🆘 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review GitHub Issues for similar problems
3. Create a new issue with detailed information
4. Tag with `ci-orchestration` label