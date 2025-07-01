# 🤖 PR Orchestrator - Intelligent Auto-Merge System

A world-class automated PR management system that handles pull requests intelligently, enforces code hygiene, resolves conflicts, and maintains high code quality standards.

## 🚀 Features

### Intelligent Auto-Merge
- **Smart Decision Engine**: Analyzes PR type, size, hygiene score, and test results
- **Confidence Scoring**: Makes merge decisions based on calculated confidence levels
- **Type-Specific Rules**: Different handling for docs, tests, features, bugfixes, etc.

### Code Hygiene Enforcement
- **Automated Analysis**: Runs the Code Hygiene Orchestrator on every PR
- **Auto-Fix Capability**: Applies hygiene fixes when confidence is high
- **Quality Gates**: Enforces minimum hygiene scores for different PR types

### Conflict Resolution
- **Smart Resolution**: Automatically resolves common conflicts (imports, versions, whitespace)
- **AI-Powered**: Uses Claude/GPT for complex semantic conflicts
- **Safety First**: Only applies resolutions with high confidence

### Real-Time Monitoring
- **Interactive Dashboard**: Live view of all PR activity
- **Performance Metrics**: Track auto-merge success rates, resolution times
- **Activity Logging**: Complete audit trail of all orchestrator actions

## 📋 Configuration

The orchestrator is configured via `config/pr-orchestrator.yaml`:

```yaml
orchestrator:
  enabled: true
  
  pr_types:
    docs:
      auto_merge: true
      min_confidence: 80
      hygiene_threshold: 60
      
    feature:
      auto_merge: false
      required_approvals: 2
      hygiene_threshold: 85
```

## 🔧 Setup

### 1. Enable GitHub Actions

The orchestrator runs via GitHub Actions. Ensure the workflow is active:

```bash
# The workflow is already in place at:
.github/workflows/pr-orchestrator.yml
```

### 2. Configure Branch Protection

Run the setup script to configure branch protection with orchestrator support:

```bash
./scripts/setup_branch_protection_with_orchestrator.sh
```

This will:
- Enable auto-merge capability
- Add orchestrator as a bypass app
- Create required labels
- Set up webhook secrets

### 3. Set Environment Variables

Add these secrets to your repository:

```bash
OPENAI_API_KEY          # For AI-powered conflict resolution
ANTHROPIC_API_KEY       # For Claude-based analysis
PR_ORCHESTRATOR_WEBHOOK_URL  # For monitoring notifications
```

## 💬 PR Commands

Users can control the orchestrator via PR comments:

| Command | Description | Permission |
|---------|-------------|------------|
| `/merge` | Force merge the PR | write |
| `/hold` | Prevent auto-merge | write |
| `/analyze` | Re-run PR analysis | read |
| `/hygiene` | Run hygiene fixes | write |

## 📊 Monitoring

### Launch the Dashboard

```bash
python scripts/pr_orchestrator/dashboard.py --repo owner/repo
```

The dashboard shows:
- Active PRs with orchestrator status
- Auto-merge metrics
- PR type distribution
- Recent activity log

### Metrics Tracked

- **Total PRs Processed**: All PRs analyzed by the orchestrator
- **Auto-Merge Rate**: Percentage successfully merged automatically
- **Average Merge Time**: Time from PR open to auto-merge
- **Hygiene Improvements**: Number of automated fixes applied
- **Conflicts Resolved**: Successfully resolved merge conflicts

## 🛡️ Safety Features

### Blocking Conditions
- Changes requested by reviewers
- Failed CI checks
- Protected file modifications
- Blocking labels (do-not-merge, wip, hold)
- Low hygiene scores

### Override Mechanisms
- Manual commands via PR comments
- Admin bypass capabilities
- Emergency hold procedures

### Protected Paths
The following paths always require manual review:
- `.github/workflows/**`
- `security/**`
- `auth/**`
- Files containing secrets/credentials

## 🔄 Workflow

1. **PR Opened/Updated**
   - Orchestrator analyzes PR type and content
   - Runs hygiene analysis
   - Calculates priority and confidence scores

2. **Decision Making**
   - Evaluates all safety gates
   - Checks approval requirements
   - Verifies CI status

3. **Auto-Merge Execution**
   - Enables GitHub auto-merge if criteria met
   - Applies hygiene fixes if needed
   - Posts decision summary

4. **Monitoring**
   - Tracks merge success
   - Updates metrics
   - Sends notifications

## 🎯 PR Type Handling

### Documentation PRs
- **Auto-merge**: Yes
- **Confidence**: 80%
- **Approvals**: 0
- **Fast-track**: Yes

### Test PRs
- **Auto-merge**: Yes
- **Confidence**: 85%
- **Approvals**: 0
- **Hygiene**: 70%

### Dependency Updates
- **Auto-merge**: Yes (trusted bots)
- **Confidence**: 90%
- **Security**: Vulnerability scan

### Feature PRs
- **Auto-merge**: No
- **Approvals**: 2
- **Hygiene**: 85%
- **Review**: Required

## 🐛 Troubleshooting

### PR Not Auto-Merging

1. Check the orchestrator comment for decision details
2. Verify all required checks are passing
3. Ensure no blocking labels are present
4. Check hygiene score meets threshold

### Conflict Resolution Failed

1. Review conflict type in logs
2. Check confidence scores
3. Manual resolution may be required for complex conflicts

### Dashboard Not Updating

1. Verify GitHub token has correct permissions
2. Check API rate limits
3. Ensure repository access is granted

## 🔮 Future Enhancements

- Machine learning for merge decisions
- Predictive conflict detection
- Custom PR templates per type
- Integration with issue tracking
- Performance impact analysis

## 📝 Contributing

To improve the orchestrator:

1. Update configuration in `config/pr-orchestrator.yaml`
2. Modify workflows in `.github/workflows/pr-orchestrator.yml`
3. Enhance conflict resolver in `scripts/pr_orchestrator/`
4. Test changes thoroughly before deploying

---

Built with ❤️ by the smartest CTO in the world 🚀