# Worktree Workflow System - Permanent Memory

## 🎯 **Core Working Principle**

**ALWAYS START EVERY SESSION BY READING `docs/WORKTREE_STATUS.md`**

This is the single source of truth for:
- Current worktree states and branches
- Work in progress and priorities  
- Infrastructure status (MCP server, etc.)
- Last session's progress
- Immediate actions required

## 🔄 **Session Startup Protocol (MANDATORY)**

1. **Read Status First**: `cat docs/WORKTREE_STATUS.md`
2. **Verify Worktrees**: `git worktree list`
3. **Check Current State**: `git status`
4. **Test MCP Server**: `curl -s --connect-timeout 5 http://44.201.249.255:8080/health`

## 📋 **Worktree Strategy (3-Worktree System)**

```
ai-kindlemint-engine/                    [feat/mcp-server-orchestration] - Active dev
├── worktrees/
│   ├── main/                           [main] - Stable, hotfixes
│   ├── experiments/                    [experiments] - Testing, risky changes
│   └── hotfix/                         [hotfix] - Emergency fixes
```

### Usage Rules:
- **Main Directory**: Current feature development (feat/mcp-server-orchestration)
- **worktrees/main**: Emergency hotfixes, clean main branch
- **worktrees/experiments**: Testing risky changes, AI experiments
- **worktrees/hotfix**: Urgent fixes that can't wait

## 🛠️ **Automation Tools Available**

- **Status Update**: `./scripts/utilities/update_worktree_status.sh`
- **Pre-commit Hook**: Auto-updates status on every commit
- **MCP Server**: `python3 scripts/utilities/mcp_server.py` (local)
- **Setup Script**: `scripts/utilities/setup_mcp_monetization.sh`

## 🎯 **Current Project Focus (as of last session)**

### Primary: MCP Server Orchestration
- **Infrastructure**: AWS EC2 at `44.201.249.255:8080` (currently not responding)
- **GitHub App**: MCP Orchestrator (App ID: 1554609) - configured
- **Local Alternative**: MCP server available for development
- **Branch**: `feat/mcp-server-orchestration`

### Immediate Actions Required:
1. Fix MCP server connectivity (EC2 or local)
2. Complete MCP server orchestration features
3. Test GitHub App automation

## 📚 **Documentation Hierarchy**

1. **`docs/WORKTREE_STATUS.md`** - Current state (READ FIRST)
2. **`docs/AI_ASSISTANT_WORKFLOW.md`** - Complete workflow guide
3. **`docs/AI_QUICK_REFERENCE.md`** - Fast command reference
4. **`docs/CLAUDE_CODE_WORKTREE_STRATEGY.md`** - Worktree strategy details
5. **`config/.worktree_orchestration_config.json`** - Automation settings

## 💡 **Session End Protocol**

Before ending any session:
1. Update `docs/WORKTREE_STATUS.md` with current progress
2. Document any new issues or changes
3. Set clear priorities for next session
4. Commit all changes with descriptive messages
5. Push to remote repository

## 🚨 **Critical Reminders**

- **NEVER** start work without reading the status file first
- **ALWAYS** update status before ending a session
- **USE** worktrees appropriately (don't create new ones unnecessarily)
- **DOCUMENT** any infrastructure changes or new tools
- **MAINTAIN** clean working directories across all worktrees

## 🔧 **Key Commands to Remember**

```bash
# Session startup essentials
cat docs/WORKTREE_STATUS.md
git worktree list
git status

# Status management
./scripts/utilities/update_worktree_status.sh

# MCP server testing
curl -s --connect-timeout 5 http://44.201.249.255:8080/health

# Worktree navigation
cd worktrees/main          # For hotfixes
cd worktrees/experiments   # For testing
cd worktrees/hotfix        # For emergencies
```

## 🎯 **Success Metrics**

This workflow ensures:
- ✅ Perfect continuity across AI assistant sessions
- ✅ No lost context or forgotten progress
- ✅ Clear handoff between different assistants
- ✅ Automatic status tracking with pre-commit hooks
- ✅ Self-documenting project state

## 📝 **Configuration Notes**

- Claude config has memory enabled (`"memory": true`)
- Auto-save memory is enabled (`"autoSaveMemory": true`)
- Pre-commit hooks are active and working
- Worktree orchestration config is in `config/.worktree_orchestration_config.json`

---

**Last Updated**: 2025-07-10T21:26:14Z  
**Context**: Established comprehensive worktree workflow system for seamless cross-session continuity  
**Status**: Active and committed to repository with automation tools
