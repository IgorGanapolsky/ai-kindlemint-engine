# AI Assistant Workflow & Handoff Process

## 🎯 **How We Work Together**

This document defines the standard workflow for AI assistants working on this project to ensure seamless handoff across sessions and conversations.

## 🔄 **Session Startup Protocol**

When starting any new conversation or session:

1. **Read Status First**: Always check `docs/WORKTREE_STATUS.md` to understand:
   - Current worktree states and branches
   - Work in progress and priorities
   - Infrastructure status (MCP server, etc.)
   - Last session's progress

2. **Verify Environment**: Run these commands to confirm setup:
   ```bash
   git worktree list                    # Verify all worktrees
   git status                          # Check current branch state
   curl -s --connect-timeout 5 http://44.201.249.255:8080/health || echo "MCP server not responding"
   ```

3. **Update Status**: Use the automation tools:
   ```bash
   ./scripts/utilities/update_worktree_status.sh    # Manual update
   # Or let pre-commit hook auto-update on commits
   ```

## 📋 **Working Principles**

### Worktree Strategy
- **Main Directory**: Active development work
- **worktrees/main**: Clean main branch for hotfixes
- **worktrees/experiments**: Testing risky changes
- **worktrees/hotfix**: Emergency fixes

### Status Tracking
- Every session must end with updated `docs/WORKTREE_STATUS.md`
- Document current work, next steps, and any issues
- Include infrastructure status and connectivity checks

### Handoff Requirements
- Never leave uncommitted work without documenting it
- Always update priorities and immediate actions
- Note any configuration changes or new tools added

## 🎯 **Key Files to Monitor**

- `docs/WORKTREE_STATUS.md` - Current state tracking
- `docs/AI_ASSISTANT_WORKFLOW.md` - This workflow (you are here)
- `docs/CLAUDE_CODE_WORKTREE_STRATEGY.md` - Worktree strategy guide
- `config/.worktree_orchestration_config.json` - Orchestration settings
- `scripts/utilities/update_worktree_status.sh` - Status update automation

## 🚀 **Session End Protocol**

Before ending any session:

1. **Update Status**: Ensure `docs/WORKTREE_STATUS.md` reflects current state
2. **Document Progress**: Note what was accomplished
3. **Set Priorities**: Update immediate actions and next steps
4. **Commit Changes**: Save all work with descriptive commit messages
5. **Push Changes**: Sync with remote repository

## 💡 **Best Practices**

- Always read the status file first - it's the source of truth
- Use the pre-commit hook to auto-update status
- Keep worktrees clean and purposeful
- Document any infrastructure changes or issues
- Maintain clear development priorities

## 🔧 **Tools & Automation**

- **Status Update**: `./scripts/utilities/update_worktree_status.sh`
- **Pre-commit Hook**: Auto-updates status on commits
- **Worktree Management**: Standard git worktree commands
- **MCP Server**: Local and remote options available

---

*This workflow ensures perfect continuity across AI assistant sessions and prevents loss of context or progress.*
