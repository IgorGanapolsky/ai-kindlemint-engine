# Automated Code Hygiene System

## Overview

The Automated Code Hygiene System ensures code quality and repository cleanliness through continuous monitoring and enforcement. It prevents the accumulation of technical debt by catching issues early and automating cleanup tasks.

## Components

### 1. GitHub Action (`automated-hygiene-enforcement.yml`)

**Purpose**: Enforces hygiene standards on all pull requests

**Features**:
- Runs automatically on every PR
- Comments with detailed hygiene report
- Blocks merge if critical errors found
- Updates status checks

**Trigger Events**:
- Pull request opened
- Pull request synchronized (new commits)
- Pull request reopened
- Manual workflow dispatch

### 2. Pre-commit Hooks (`.pre-commit-config.yaml`)

**Purpose**: Catches hygiene issues before commits

**Checks**:
- Trailing whitespace removal
- File ending fixes
- Large file detection (>1MB)
- Private key detection
- Code formatting (Black)
- Import sorting (isort)
- Linting (flake8)
- Custom hygiene checks

### 3. Code Hygiene Orchestrator (`agents/code_hygiene_orchestrator.py`)

**Purpose**: Core engine for hygiene analysis and cleanup

**Capabilities**:
- Duplicate file detection
- Large file identification
- Unused file detection
- Naming convention enforcement
- Empty directory cleanup
- CI artifact organization
- One-off script detection

### 4. Hygiene Rules Configuration (`config/hygiene_rules.json`)

**Purpose**: Configurable rules and thresholds

**Rule Categories**:
- `duplicate_files`: No more than 3 identical files
- `large_files`: Files >10MB should use Git LFS
- `script_duplication`: Max 5 similar scripts per category
- `unused_files`: Archive files not modified in 90+ days
- `naming_conventions`: Enforce snake_case for Python
- `temporary_files`: Block .tmp, .debug, .log files
- `broken_symlinks`: Must be fixed or removed
- `one_off_scripts`: Limit emergency/fix scripts

## Installation

### Quick Setup

```bash
# Run the setup script
./scripts/setup_hygiene_automation.sh
```

### Manual Setup

1. **Install pre-commit**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Enable GitHub Action**:
   - The workflow is automatically active once merged to main
   - No additional configuration needed

3. **Configure Git Aliases**:
   ```bash
   git config alias.hygiene '!python agents/code_hygiene_orchestrator.py analyze'
   git config alias.clean-hygiene '!python agents/code_hygiene_orchestrator.py clean --interactive'
   ```

## Usage

### Local Development

1. **Automatic Checks**: Pre-commit hooks run automatically on `git commit`

2. **Manual Analysis**:
   ```bash
   git hygiene
   # or
   python agents/code_hygiene_orchestrator.py analyze
   ```

3. **Interactive Cleanup**:
   ```bash
   git clean-hygiene
   # or
   python agents/code_hygiene_orchestrator.py clean --interactive
   ```

4. **Skip Hooks** (use sparingly):
   ```bash
   git commit --no-verify
   ```

### Pull Requests

1. **Automatic Enforcement**: 
   - Hygiene check runs automatically
   - Results posted as PR comment
   - Status check blocks merge if errors found

2. **Manual Re-run**:
   - Go to Actions tab
   - Select "Automated Hygiene Enforcement"
   - Click "Run workflow"

### Scheduled Cleanup

- Weekly cleanup runs every Sunday at 2 AM UTC
- Automatically creates PR with hygiene fixes
- Review and merge to keep repository clean

## Rule Customization

Edit `config/hygiene_rules.json` to customize:

```json
{
  "rules": {
    "large_files": {
      "enabled": true,
      "severity": "error",
      "max_size_mb": 10,
      "exceptions": ["*.pdf", "*.png"]
    }
  }
}
```

### Severity Levels

- **error**: Blocks PR merge
- **warning**: Shows in report but doesn't block
- **info**: Informational only

## Troubleshooting

### Pre-commit Hooks Not Running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### GitHub Action Not Triggering

1. Check workflow is not disabled
2. Verify branch permissions
3. Check Actions tab for errors

### False Positives

1. Add exceptions to `hygiene_rules.json`
2. Update ignored paths for specific files
3. Use inline comments to suppress warnings

## Best Practices

1. **Fix Issues Early**: Address hygiene warnings before they become errors
2. **Regular Cleanup**: Run manual cleanup weekly
3. **Configure Rules**: Tailor rules to your project needs
4. **Document Exceptions**: Explain why certain files are exempt
5. **Monitor Trends**: Track hygiene metrics over time

## Metrics and Reporting

### PR Comment Format

```
## 🧹 Code Hygiene Report

❌ **3 error(s) found** - must be fixed before merging
⚠️ **5 warning(s) found** - should be addressed

### Issues Found:
- ❌ **duplicate_files**: Found 4 identical files (max: 3)
- ⚠️ **script_duplication**: 8 cleanup scripts found

### Statistics:
- Total files analyzed: 1,245
- Duplicate files found: 4
- Unused files detected: 23
```

### Weekly Report

The scheduled job creates detailed reports including:
- Files cleaned up
- Space recovered
- Issues fixed
- Remaining warnings

## Future Enhancements

1. **Auto-fix Mode**: Automatically fix simple issues
2. **Custom Rules**: Project-specific hygiene rules
3. **Metrics Dashboard**: Track hygiene over time
4. **Integration with Slack**: Real-time notifications
5. **AI-powered Suggestions**: Smart cleanup recommendations

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review hygiene logs in Actions tab
3. Create an issue with the `hygiene` label

---

*Remember: A clean codebase is a happy codebase! 🧹✨*