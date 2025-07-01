# 🚀 PR Orchestrator Quick Start

## Enable the System (5 minutes)

### 1. Run Setup Script
```bash
./scripts/setup_branch_protection_with_orchestrator.sh
```

### 2. Add Secrets to GitHub
Go to Settings → Secrets → Actions and add:
- `OPENAI_API_KEY` (optional, for AI conflict resolution)
- `ANTHROPIC_API_KEY` (optional, for advanced analysis)

### 3. That's it! 🎉

## How It Works

The PR Orchestrator automatically:
- ✅ Analyzes every PR for type, size, and quality
- 🧹 Runs hygiene checks and applies fixes
- 🤖 Auto-merges safe PRs (docs, tests, dependencies)
- 🛡️ Blocks risky changes requiring review
- 📊 Tracks all metrics and decisions

## What Gets Auto-Merged?

| PR Type | Auto-Merge | Conditions |
|---------|------------|------------|
| Docs | ✅ Yes | Hygiene > 60% |
| Tests | ✅ Yes | Hygiene > 70% |
| Dependencies | ✅ Yes | From trusted bots |
| Bug Fixes | ✅ Yes* | With 1 approval, < 200 lines |
| Features | ❌ No | Requires manual review |

## Control Commands

Comment on any PR:
- `/merge` - Force merge
- `/hold` - Prevent auto-merge
- `/analyze` - Re-run analysis
- `/hygiene` - Apply fixes

## Monitor Activity

```bash
# Launch real-time dashboard
python scripts/pr_orchestrator/dashboard.py
```

## Safety First

The orchestrator NEVER auto-merges:
- 🔒 Security-related files
- 🚫 PRs with "do-not-merge" label
- ❌ Failed CI checks
- 📝 Changes requested by reviewers

---

Questions? Check [full documentation](docs/PR_ORCHESTRATOR.md)