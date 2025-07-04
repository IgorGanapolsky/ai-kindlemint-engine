# Bot Configuration Guide

> **Last Updated**: July 4, 2025
> **Purpose**: Reduce PR noise and improve developer experience

## 🤖 Bot Ecosystem Overview

### Active Bots (Optimized)
1. **CodeRabbit** - Code review (configured for minimal noise)
2. **GitHub Actions** - CI/CD pipeline (consolidated checks)
3. **Codecov** - Coverage reporting (single comment per PR)
4. **Orchestrator** - Auto-merge when checks pass

### Disabled Bots
1. **Sentry Seer** - Disabled due to redundancy with CodeRabbit
2. **Cursor Bugbot** - Manual trigger only (dashboard config required)

## 📝 Configuration Files

### `.coderabbit.yml`
Configures CodeRabbit for minimal verbosity:
- Only comments on significant issues
- Skips style/formatting (handled by linters)
- Groups related issues
- Max 3 file comments per PR
- Focuses on: security, performance, logic errors, bugs

### `.github/workflows/consolidated-ci.yml`
Single workflow combining all essential checks:
- Code quality (Ruff, MyPy)
- Tests (Python 3.11 only)
- Coverage upload
- Badge validation
- KDP metadata (conditional)

## 🎯 Optimization Results

### Before
- **64 checks** per PR
- **94+ bot comments** on simple PRs
- **Multiple Python versions** creating duplicates
- **12+ redundant workflows**

### After
- **~10-15 checks** per PR
- **<10 meaningful comments** per PR
- **Single Python version** (3.11)
- **21 active workflows** (from 33)

## 🔧 Disabled Workflows

The following workflows were disabled (`.yml.disabled`):
1. test-orchestration.yml
2. qa_validation.yml
3. quality-gate.yml
4. visual-qa-validation.yml
5. pr-validation.yml
6. agent-pr-validation.yml
7. autonomous-pr-handler.yml
8. ai-suggestions-processor.yml
9. autonomous-coderabbit-handler.yml
10. intelligent-pr-fixer.yml
11. intelligent-conflict-resolver.yml
12. requirements-health-check.yml

## 🚀 Quick Commands

### Re-enable a Bot
```bash
# Example: Re-enable Sentry
mv .github/workflows/sentry-ai-automation.yml.disabled .github/workflows/sentry-ai-automation.yml
```

### Trigger Manual Checks
```bash
# Run consolidated CI manually
gh workflow run consolidated-ci.yml

# Trigger specific bot review
# Add comment: @coderabbit review
```

### Monitor Bot Activity
```bash
# Check PR comments
gh pr view 130 --comments | grep -E "bot\]|Bot"

# Count workflow runs
gh run list --workflow=consolidated-ci.yml
```

## 📊 Best Practices

1. **Skip Bot Reviews**: Add `[skip-ci]` or `[skip-bots]` to PR title
2. **Focus Reviews**: Use draft PRs until ready for review
3. **Manual Triggers**: Use `@botname review` for specific bots
4. **Consolidate Changes**: Batch related changes to reduce PR count

## 🔍 Monitoring

Track bot efficiency:
- PR merge time (should decrease)
- Developer satisfaction (less noise)
- CI reliability (fewer flaky tests)
- Cost savings (fewer API calls)

## 🆘 Troubleshooting

### Too Few Checks
1. Review consolidated-ci.yml
2. Ensure critical checks aren't missing
3. Re-enable specific workflows if needed

### Bot Not Responding
1. Check bot configuration files
2. Verify GitHub tokens/permissions
3. Check workflow logs

### Need More Verbosity
1. Update .coderabbit.yml `comment_threshold`
2. Re-enable specific workflows
3. Use manual bot triggers

---

**Remember**: The goal is meaningful feedback, not maximum coverage. Quality over quantity!