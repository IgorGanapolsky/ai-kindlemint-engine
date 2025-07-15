# Documentation Cleanup Plan

## 🚨 Current State Analysis

### Problems Identified:
1. **85+ documentation files** scattered across docs/
2. **Massive MCP references** throughout (now obsolete)
3. **Duplicate content** across multiple files
4. **Outdated information** about AWS, MCP, old workflows
5. **No clear organization** - files mixed randomly
6. **Backup files** cluttering the directory

### Files to DELETE (Outdated/Obsolete):
```
docs/MCP_SERVER_DEPLOYMENT.md          # MCP is removed
docs/requirements_mcp.txt              # MCP dependencies removed
docs/WORKTREE_STATUS.md.backup         # Duplicate backup
docs/README_FALSE_CLAIMS_BACKUP.md     # Outdated backup
docs/AWS_MIGRATION_COMPLETE.md         # AWS removed
docs/infrastructure/MANUAL_AWS_DEPLOYMENT.md  # AWS removed
docs/ADVANCED_INTEGRATIONS.md          # Contains MCP references
docs/AI_QUICK_REFERENCE.md             # Contains MCP references
docs/AI_ASSISTANT_WORKFLOW.md          # Contains MCP references
docs/scripts_to_archive.txt            # Temporary file
docs/requirements-booktok.txt          # Consolidated into main requirements
docs/requirements-locked.txt           # Too large, use setup.py instead
docs/requirements-visual-qa.txt        # Consolidated
docs/reddit_post.txt                   # Temporary file
docs/pay_per_crawl.md                  # Outdated strategy
docs/artifact_storage_strategy.md      # Outdated
docs/automated_market_research_prs.md  # Outdated
docs/badge_fix_plan.md                 # Completed
docs/cleanup_orchestration_improvement_report.md  # Completed
docs/claude_code_flow_integration.md   # Outdated
docs/PR_MANAGEMENT_AUTOMATION.md       # Superseded by new workflows
docs/PR_ORCHESTRATOR.md                # Superseded by new workflows
docs/PR_ORCHESTRATOR_QUICKSTART.md     # Superseded by new workflows
docs/PR_STRATEGY_IMPLEMENTATION.md     # Superseded by new workflows
docs/QA_ENHANCEMENT_STRATEGY_2025.md   # Completed
docs/QA_ORCHESTRATION_COMPLETE.md      # Completed
docs/README_BADGE_UPDATE.md            # Completed
docs/REVENUE_PIVOT_STATUS.md           # Outdated
docs/REVENUE_PIVOT_STATUS_FINAL.md     # Outdated
docs/REVENUE_ROADMAP_300_DAY.md        # Outdated
docs/SECURITY_FIX.md                   # Completed
docs/SENTRY_AGENT_MONITORING_GUIDE.md  # Superseded by new workflows
docs/SERIES_REQUIREMENTS.md            # Outdated
docs/SLACK_NOTIFICATIONS_GUIDE.md      # Superseded by new workflows
docs/START_HERE.md                     # Superseded by main README
docs/STOP_BOT_EMAILS.md                # Completed
docs/VOICE_TO_BOOK_PIPELINE_ARCHITECTURE.md  # Outdated
docs/YC_Publishing_Playbook.md         # Outdated
docs/COVER_GENERATION_FIXES_SUMMARY.md # Completed
docs/CTO_PR_ORCHESTRATION_STRATEGY.md  # Superseded by new workflows
docs/CURSOR_BUGBOT_STATUS.md           # Completed
docs/CURSOR_BUGBOT_TROUBLESHOOTING.md  # Completed
docs/DEVELOPMENT_WORKFLOW.md           # Superseded by CLAUDE.md
docs/EVERYDAY_AI_PUBLISHING_REVOLUTION.md  # Outdated
docs/FIREBASE_AI_INTEGRATION_STRATEGY.md  # Outdated
docs/FIREBASE_IMPLEMENTATION_PLAN.md   # Outdated
docs/FREE_DEPLOYMENT_GUIDE.md          # Outdated
docs/GITHUB_SECRETS_SETUP.md           # Superseded by new workflows
docs/GIT_WORKFLOW.md                   # Superseded by CLAUDE.md
docs/IMMEDIATE_ACTION_PLAN.md          # Outdated
docs/IMPLEMENTATION_SUMMARY.md         # Outdated
docs/KDP_AUTOMATION_SETUP.md           # Superseded by new workflows
docs/KDP_COVER_CALCULATOR_INTEGRATION.md  # Outdated
docs/LANDING_PAGE_QA_FLOW.md           # Superseded by new workflows
docs/MAGNETIC_MARKETING_SYSTEM.md      # Outdated
docs/MARKETING_STRATEGY_2025.md        # Outdated
docs/MARKET_ALIGNMENT_IMPLEMENTATION.md  # Outdated
docs/MONETIZATION_SETUP.md             # Outdated
docs/MULTI_AGENT_ARCHITECTURE_DESIGN.md  # Outdated (A2A removed)
docs/OPENHANDS_EMAIL_AUTOMATION.md     # Outdated
docs/ORCHESTRATION_ARCHITECTURE.md     # Outdated
docs/ORCHESTRATION_SYSTEM.md           # Outdated
docs/PAYMENT_INTEGRATION.md            # Outdated
docs/PAY_PER_CRAWL_IMPLEMENTATION.md  # Outdated
docs/PDF_QUALITY_STANDARDS.md          # Superseded by new workflows
docs/PRODUCTION_QA_CHECKLIST.md        # Superseded by new workflows
docs/2025_EXECUTIVE_PLAN.md            # Outdated
docs/AI_ORCHESTRATION_COMPLETE.md      # Completed
docs/ALEMBIC_INTEGRATION.md            # Outdated
docs/ARCHIVAL_WORKFLOW.md              # Outdated
docs/TRAFFIC_GENERATION_STATUS.md      # Outdated
docs/AUTOMATED_HYGIENE.md              # Superseded by new workflows
docs/GITHUB_API_KEY_SETUP.md           # Superseded by new workflows
docs/sentry-ai-automation-summary.md   # Superseded by new workflows
docs/sentry-streamlining-guide.md      # Superseded by new workflows
docs/slack-qa-notifications-explained.md  # Superseded by new workflows
docs/slack_integration_guide.md        # Superseded by new workflows
docs/PROSPECTING_AUTOMATION.md         # Outdated
docs/CLOUD_DATA_MIGRATION.md           # Outdated
```

### Files to KEEP (Essential):
```
docs/CLAUDE.md                          # Main development guide
docs/WORKTREE_STATUS.md                 # Current status (needs MCP cleanup)
docs/plan.md                            # Main project plan
docs/SECURITY.md                        # Security policy
docs/README_ENHANCED.md                 # Enhanced README
docs/BOT_CONFIGURATION.md               # Current bot setup
docs/guides/CODE_HYGIENE_GUIDE.md       # Code hygiene guide
docs/checklists/plan.md                 # Current checklist
docs/checklists/STEALTH_MODE_ACTION_PLAN.md  # Current action plan
docs/architecture/QA_SYSTEM_FAILURE_ANALYSIS.md  # Technical analysis
docs/architecture/ARCHITECTURE_MIGRATION_STATUS.md  # Current status
docs/infrastructure/INFRASTRUCTURE_IMPLEMENTATION_COMPLETE.md  # Current status
docs/analysis/duplicate_files_report.md  # Current analysis
docs/analysis/code_hygiene_report.md    # Current analysis
docs/analysis/MIGRATION_EXAMPLE.md      # Migration guide
docs/infrastructure/MIGRATION_CI_FIX.md # CI fix guide
```

### Files to UPDATE (Remove MCP references):
```
docs/WORKTREE_STATUS.md                 # Remove all MCP references
docs/CLAUDE.md                          # Already updated
```

## 🗂️ New Organization Structure

### Keep this structure:
```
docs/
├── CLAUDE.md                           # Main development guide
├── WORKTREE_STATUS.md                  # Current project status
├── plan.md                             # Main project plan
├── SECURITY.md                         # Security policy
├── README_ENHANCED.md                  # Enhanced README
├── BOT_CONFIGURATION.md                # Bot configuration
├── guides/                             # How-to guides
│   └── CODE_HYGIENE_GUIDE.md
├── checklists/                         # Action checklists
│   ├── plan.md
│   └── STEALTH_MODE_ACTION_PLAN.md
├── architecture/                       # Technical architecture
│   ├── QA_SYSTEM_FAILURE_ANALYSIS.md
│   └── ARCHITECTURE_MIGRATION_STATUS.md
├── infrastructure/                     # Infrastructure docs
│   ├── INFRASTRUCTURE_IMPLEMENTATION_COMPLETE.md
│   └── MIGRATION_CI_FIX.md
├── analysis/                           # Analysis reports
│   ├── duplicate_files_report.md
│   ├── code_hygiene_report.md
│   └── MIGRATION_EXAMPLE.md
└── templates/                          # Template files
    └── (keep existing templates)
```

## 🚀 Cleanup Execution Plan

### Phase 1: Delete Obsolete Files (Immediate)
```bash
# Delete all MCP-related files
rm docs/MCP_SERVER_DEPLOYMENT.md
rm docs/requirements_mcp.txt
rm docs/ADVANCED_INTEGRATIONS.md
rm docs/AI_QUICK_REFERENCE.md
rm docs/AI_ASSISTANT_WORKFLOW.md

# Delete AWS-related files
rm docs/AWS_MIGRATION_COMPLETE.md
rm docs/infrastructure/MANUAL_AWS_DEPLOYMENT.md

# Delete backup files
rm docs/WORKTREE_STATUS.md.backup
rm docs/README_FALSE_CLAIMS_BACKUP.md

# Delete temporary files
rm docs/scripts_to_archive.txt
rm docs/reddit_post.txt
rm docs/requirements-*.txt
```

### Phase 2: Delete Outdated Content (Today)
```bash
# Delete all the outdated strategy files
rm docs/pay_per_crawl.md
rm docs/artifact_storage_strategy.md
rm docs/automated_market_research_prs.md
# ... (all the files listed above)
```

### Phase 3: Update Remaining Files (Today)
```bash
# Update WORKTREE_STATUS.md to remove MCP references
# Update any remaining files with current information
```

### Phase 4: Organize Structure (Today)
```bash
# Move files to appropriate subdirectories
# Ensure all essential files are in the right place
```

## 📊 Expected Results

### Before Cleanup:
- **85+ files** in docs/
- **Massive MCP references** throughout
- **Duplicate content** everywhere
- **Outdated information** causing confusion
- **No clear organization**

### After Cleanup:
- **~15 essential files** in docs/
- **Zero MCP references**
- **No duplicate content**
- **Current, accurate information**
- **Clear organization** by category

## ✅ Success Criteria

1. **Zero MCP references** in any documentation
2. **No duplicate content** across files
3. **All information current** and accurate
4. **Clear organization** by category
5. **Essential files only** - no obsolete content
6. **Easy navigation** and finding information

## 🎯 Benefits

1. **Reduced confusion** - developers know where to find info
2. **Faster onboarding** - clear, current documentation
3. **No outdated references** - everything matches current system
4. **Easier maintenance** - fewer files to keep updated
5. **Professional appearance** - clean, organized docs

This cleanup will transform the docs directory from a confusing mess into a clean, professional, and useful documentation system. 