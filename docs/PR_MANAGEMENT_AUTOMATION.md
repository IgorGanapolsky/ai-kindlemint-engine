# PR Management Automation

## Overview

The KindleMint Orchestration System now includes automated PR management capabilities. This eliminates the need for manual PR reviews for routine updates and security improvements.

## Features

### 🤖 Automated PR Review
- Reviews all open pull requests automatically
- Posts AI-generated review comments
- Categorizes PRs by type and author

### ✅ Auto-Approval & Merging
- Auto-approves PRs from trusted security bots:
  - Seer AI (Sentry)
  - Pixeebot
  - Dependabot
  - Snyk
  - DeepSource
  - CodeRabbit AI
- Automatically merges approved PRs when possible
- Falls back to squash merge if regular merge fails

### 🔒 Security-First Approach
- Prioritizes security improvements
- Validates changes are limited to security enhancements
- Ensures no functional code is altered in security PRs

### 📅 Scheduled Execution
- Runs automatically daily at 9 AM
- Can be triggered manually on-demand
- Integrated with the main orchestration system

## Usage

### Manual Execution

Run the standalone PR management script:
```bash
python scripts/auto_manage_prs.py
```

Process specific PRs:
```bash
python scripts/auto_manage_prs.py 76 75 74
```

### Through Orchestration System

Trigger via the orchestration coordinator:
```bash
python run_pr_management.py
```

### Automated Daily Runs

The PR management workflow is integrated into the daily orchestration schedule and runs automatically at 9 AM.

## Configuration

### Aggressive Mode
The system runs in aggressive mode by default, auto-approving PRs that match common patterns:
- test
- docs
- style
- refactor
- chore
- fix
- feat
- cleanup
- update
- remove
- add
- improve

### Custom Patterns
Modify `src/kindlemint/agents/github_issues_agent.py` to add custom auto-approve patterns:
```python
self.auto_approve_patterns = [
    "Add timeout to requests calls",
    "Secure Source of Randomness",
    "Bump .* from .* to .*",  # Dependency updates
]
```

## Integration

The PR management system is fully integrated with:
- **Automation Coordinator**: Schedules and coordinates PR management tasks
- **GitHub Issues Agent**: Handles the actual PR review and merge operations
- **Orchestration Runner**: Includes PR management in the daily workflow

## Monitoring

Check PR management results in:
- `books/coordination_data/pr_management_*.json` - Detailed results
- `orchestration_system.log` - System logs
- GitHub PR comments - AI review feedback

## Benefits

1. **Time Savings**: No more manual review of routine PRs
2. **Security**: Faster response to security updates
3. **Consistency**: Standardized review process
4. **24/7 Operation**: Works autonomously without human intervention
5. **Audit Trail**: All actions are logged and traceable

## Example Output

```
🤖 KindleMint PR Automation Starting...
📊 Processing 5 PRs: [75, 74, 73, 71, 70]

🔍 Processing PR #75...
✅ PR #75: Successfully reviewed
🚀 PR #75: Auto-merged!

🔍 Processing PR #74...
✅ PR #74: Successfully reviewed
📋 PR #74: manual_review_requested

==================================================
📈 PR Management Summary:
   Total Processed: 5
   ✅ Auto-merged: 2
   📋 Manual Review: 3
   ❌ Failed: 0
==================================================
```

## Troubleshooting

### PR Not Auto-Merging
- Check for merge conflicts
- Ensure PR is not a draft
- Verify branch protection rules allow automation

### Authentication Issues
- Run `gh auth status` to check GitHub CLI authentication
- Ensure proper permissions for the repository

### Rate Limiting
- The system includes delays between operations
- Adjust delays in `auto_manage_prs.py` if needed