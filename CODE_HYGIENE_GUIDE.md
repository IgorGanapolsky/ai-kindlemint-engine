# 🧹 Code Hygiene Guide

> Maintaining a clean, organized, and efficient codebase for the AI-KindleMint-Engine project

## 📋 Table of Contents

1. [Overview](#overview)
2. [Current Issues](#current-issues)
3. [Quick Cleanup](#quick-cleanup)
4. [Code Hygiene Tools](#code-hygiene-tools)
5. [Best Practices](#best-practices)
6. [Automation](#automation)
7. [Maintenance Schedule](#maintenance-schedule)

## 🎯 Overview

Code hygiene is critical for maintaining a scalable, maintainable codebase. Our project has accumulated technical debt that needs systematic cleanup. This guide provides tools and processes to maintain code quality.

## 🚨 Current Issues

Based on our analysis, the project has:

| Issue Type | Count | Severity | Impact |
|------------|-------|----------|---------|
| CI Artifacts | 130 files | High | Clutters codebase, slows git operations |
| Duplicate Files | 247 files | High | Wastes space, causes confusion |
| Scattered Docs | 53 files | Medium | Hard to find documentation |
| Root Clutter | 13 files | Medium | Unprofessional, hard to navigate |
| Naming Issues | 5 files | Low | Inconsistent conventions |
| Missing .gitignore | 12 patterns | Low | Tracks unnecessary files |

## 🚀 Quick Cleanup

### Option 1: Interactive Cleanup (Recommended)

```bash
# Run the interactive cleanup script
python scripts/cleanup_project.py

# This will:
# 1. Create a backup
# 2. Show analysis results
# 3. Let you approve each cleanup action
# 4. Commit changes when done
```

### Option 2: Manual Steps

```bash
# 1. Run analysis
python agents/code_hygiene_orchestrator.py analyze

# 2. Generate detailed report
python agents/code_hygiene_orchestrator.py report -o hygiene_report.md

# 3. Run cleanup with confirmation
python agents/code_hygiene_orchestrator.py clean --interactive

# 4. Review and commit changes
git add -A
git commit -m "🧹 Code hygiene cleanup"
```

### Option 3: Automated Cleanup (Use with caution)

```bash
# Dry run first
python agents/code_hygiene_orchestrator.py clean --dry-run

# If satisfied, run actual cleanup
python agents/code_hygiene_orchestrator.py clean
```

## 🛠️ Code Hygiene Tools

### 1. Code Hygiene Orchestrator

**Location**: `agents/code_hygiene_orchestrator.py`

**Features**:
- Analyzes codebase for hygiene issues
- Provides detailed reports
- Automated fixes for common issues
- Safety checks and dry-run mode

**Commands**:
```bash
# Analyze codebase
python agents/code_hygiene_orchestrator.py analyze

# Generate report
python agents/code_hygiene_orchestrator.py report -o report.md

# Clean with dry-run
python agents/code_hygiene_orchestrator.py clean --dry-run

# Interactive cleanup
python agents/code_hygiene_orchestrator.py clean --interactive
```

### 2. Project Cleanup Script

**Location**: `scripts/cleanup_project.py`

**Features**:
- Interactive step-by-step cleanup
- Automatic backup creation
- Safe defaults
- Progress tracking

### 3. GitHub Action

**Location**: `.github/workflows/code-hygiene.yml`

**Features**:
- Weekly automated checks
- PR hygiene validation
- Automated issue creation
- Optional automated cleanup

## 📐 Best Practices

### File Organization

```
ai-kindlemint-engine/
├── src/                    # Source code
├── scripts/               # Utility scripts
├── tests/                 # Test files
├── docs/                  # Documentation
│   ├── reports/          # Analysis reports
│   ├── planning/         # Plans and strategies
│   └── guides/           # How-to guides
├── agents/               # AI agents
├── books/                # Book content
├── .ci_artifacts/        # CI/CD artifacts (gitignored)
├── .archive/             # Archived files (gitignored)
└── .misc/                # Miscellaneous files (gitignored)
```

### Naming Conventions

- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Test files**: `test_*.py` or `*_test.py`

### Git Hygiene

1. **Update .gitignore**:
```gitignore
# CI/CD artifacts
.ci_artifacts/
ci_orchestration_cycle_*.json

# Archives
.archive/

# Temporary files
*.tmp
*.temp
*.bak
*.swp
*~

# Misc
.misc/
full.txt
input.txt
output.txt
```

2. **Commit Messages**:
```bash
# Good examples
git commit -m "🧹 Remove duplicate puzzle metadata files"
git commit -m "📁 Organize CI artifacts into .ci_artifacts directory"
git commit -m "📚 Consolidate documentation into docs/ structure"
```

### Documentation Standards

1. **README files**: Only in directories that need explanation
2. **Markdown files**: Use descriptive names (not `full.txt`, `input.txt`)
3. **Reports**: Archive after 30 days
4. **Code comments**: Explain "why", not "what"

## 🤖 Automation

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: code-hygiene
        name: Code Hygiene Check
        entry: python agents/code_hygiene_orchestrator.py analyze
        language: system
        pass_filenames: false
```

### GitHub Actions

The code hygiene workflow runs:
- **Weekly**: Full analysis and issue creation
- **On PR**: Basic hygiene checks
- **Manual**: Full cleanup via workflow dispatch

### Local Git Hooks

```bash
# Create pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "🔍 Running code hygiene check..."
python agents/code_hygiene_orchestrator.py analyze
if [ $? -ne 0 ]; then
    echo "❌ Code hygiene issues detected. Run cleanup before pushing."
    exit 1
fi
EOF

chmod +x .git/hooks/pre-push
```

## 📅 Maintenance Schedule

### Daily
- Run tests before committing
- Use meaningful file names
- Keep root directory clean

### Weekly
- Run hygiene analysis
- Review and merge dependabot PRs
- Archive old reports

### Monthly
- Full cleanup sweep
- Review and update .gitignore
- Optimize CI/CD artifacts

### Quarterly
- Major reorganization if needed
- Update hygiene rules
- Review automation effectiveness

## 🚧 Preventing Future Issues

### 1. CI Artifacts
- Always write to `.ci_artifacts/` directory
- Use timestamps in filenames
- Implement automatic cleanup after 7 days

### 2. Documentation
- Create in appropriate `docs/` subdirectory
- Use clear, descriptive names
- Archive old reports automatically

### 3. Scripts
- New scripts go in `scripts/` directory
- Only `setup.py`, `manage.py` in root
- Use proper shebang lines

### 4. Temporary Files
- Never commit `.tmp`, `.bak` files
- Use proper cleanup in scripts
- Add to .gitignore immediately

## 🆘 Troubleshooting

### "Too many files to handle"
```bash
# Process in batches
python agents/code_hygiene_orchestrator.py clean --dry-run > cleanup_plan.txt
# Review and execute specific rules only
```

### "Accidentally deleted important file"
```bash
# Check the backup directory
ls -la .cleanup_backup_*/
# Or use git to restore
git checkout -- <filename>
```

### "Cleanup script fails"
```bash
# Run with debug logging
PYTHONPATH=. python -m pdb agents/code_hygiene_orchestrator.py analyze
```

## 📊 Success Metrics

Track hygiene improvements:

```bash
# Before cleanup
git count-objects -v

# After cleanup
git count-objects -v

# File count comparison
find . -type f | wc -l
```

Target metrics:
- ✅ No files in root except essential ones
- ✅ All CI artifacts in `.ci_artifacts/`
- ✅ Documentation organized in `docs/`
- ✅ No duplicate files
- ✅ Consistent naming conventions

## 🎯 Next Steps

1. **Immediate**: Run `python scripts/cleanup_project.py`
2. **Today**: Update .gitignore with hygiene patterns
3. **This Week**: Set up pre-commit hooks
4. **This Month**: Establish regular cleanup schedule

---

Remember: **A clean codebase is a productive codebase!** 🚀

For questions or improvements to this guide, please update this file directly.