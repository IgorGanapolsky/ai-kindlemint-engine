# Git Workflow Guide - Solo Developer + AI Agents

## 🎯 Hybrid Git Flow Strategy

### For Human Changes (You)
✅ **Direct to main** - Fast iterations for solo development
```bash
# Quick method
./scripts/human_git_workflow.sh quick-push "feat: add new feature"

# Manual method  
git add . && git commit -m "feat: human change" && git push origin main
```

### For AI Agent Changes
🤖 **Pull Request workflow** - Safety and validation
```bash
# Agents use automated PR workflow
python scripts/agent_git_helper.py create-branch --agent-type content-generator --task "puzzle-generation"
python scripts/agent_git_helper.py commit --agent-type content-generator --message "Generate sudoku puzzles"
python scripts/agent_git_helper.py create-pr --agent-type content-generator --task "puzzle-generation" --summary "Added 100 new sudoku puzzles"
```

## 🛡️ Branch Protection Settings

**Configured for `main` branch:**
- ✅ **Require status checks**: CI Status must pass
- ✅ **Require branches up to date**: Prevents conflicts
- ❌ **Require pull request reviews**: OFF (solo developer)
- ✅ **Restrict force pushes**: Safety measure
- ✅ **Allow admin bypass**: You can push directly to main

## 🤖 Agent Workflow Configuration

**Located in:** `.github/agent-workflow.yml`

**Features:**
- Auto-merge when CI passes
- Standardized branch naming (`agent/type-task`)
- Automated PR templates
- Rollback capabilities

## 🚀 Quick Commands

### Human Workflow
```bash
# Quick push to main
./scripts/human_git_workflow.sh quick-push "docs: update README"

# Create feature branch for complex work
./scripts/human_git_workflow.sh feature-branch "payment-system" "Add Stripe integration"

# Finish and merge feature
./scripts/human_git_workflow.sh finish-feature "Payment system complete"

# Check repository status
./scripts/human_git_workflow.sh status

# Emergency rollback
./scripts/human_git_workflow.sh rollback 2  # Rollback 2 commits
```

### Agent Workflow
```bash
# Agents create PRs automatically
python scripts/agent_git_helper.py create-branch --agent-type puzzle-generator --task optimize-algorithms
python scripts/agent_git_helper.py commit --agent-type puzzle-generator --message "Optimize sudoku generation speed"
python scripts/agent_git_helper.py create-pr --agent-type puzzle-generator --task optimize-algorithms --summary "40% faster puzzle generation"

# Return to main safely
python scripts/agent_git_helper.py rollback --agent-type puzzle-generator
```

## 🔄 Workflow Examples

### Scenario 1: Quick Documentation Update (Human)
```bash
# Edit files
vim README.md

# Quick push
./scripts/human_git_workflow.sh qp "docs: update installation guide"
```

### Scenario 2: Major Feature Development (Human)
```bash
# Start feature
./scripts/human_git_workflow.sh fb "ai-voice-cloning" "Add voice synthesis capabilities"

# Work on feature...
git add . && git commit -m "feat: implement voice model training"
git push origin feature/ai-voice-cloning

# Finish feature
./scripts/human_git_workflow.sh ff "Voice cloning system ready for production"
```

### Scenario 3: Agent-Generated Content (AI)
```bash
# Agent creates new content automatically
./claude-code develop-feature marketplace_integration
# → Creates agent/claude-code-marketplace_integration branch
# → Implements feature with tests
# → Creates PR with auto-merge
# → Merges when CI passes
```

## 🚨 Emergency Procedures

### Rollback Bad Agent Changes
```bash
# Check recent PRs
gh pr list --state merged --limit 5

# Rollback specific commits
./scripts/human_git_workflow.sh rollback 3
```

### Fix Broken Main Branch
```bash
# Force reset to last known good commit
git checkout main
git reset --hard <good-commit-hash>
git push origin main --force-with-lease
```

### Disable Auto-Merge Temporarily
```bash
# Edit .github/agent-workflow.yml
# Set auto_merge.enabled: false
git add .github/agent-workflow.yml
./scripts/human_git_workflow.sh qp "config: disable agent auto-merge temporarily"
```

## 📊 Monitoring and Alerts

**GitHub Actions** automatically:
- ✅ Runs tests on every PR
- ✅ Validates code quality (black, flake8, mypy)
- ✅ Checks for security issues
- ✅ Updates badges and metrics

**Slack Integration** (if configured):
- 🔔 Notifications for failed CI
- 📈 Daily repository health reports
- 🤖 Agent activity summaries

## 🎛️ Configuration Files

| File | Purpose |
|------|---------|
| `.github/agent-workflow.yml` | Agent PR and merge configuration |
| `scripts/agent_git_helper.py` | Python helper for agent git operations |
| `scripts/human_git_workflow.sh` | Bash shortcuts for human workflows |
| `.github/workflows/` | CI/CD pipeline definitions |

## 💡 Best Practices

### For You (Human)
1. **Use quick-push for small changes** (docs, config, bug fixes)
2. **Use feature branches for major work** (new systems, breaking changes)
3. **Always check status before complex operations**
4. **Keep main branch clean and deployable**

### For Agents
1. **Always use PR workflow** - Never direct push to main
2. **Include comprehensive change summaries**
3. **Let CI validate before merge**
4. **Use descriptive branch and commit names**

This workflow gives you the **speed of solo development** with the **safety of team collaboration** for AI agents!
