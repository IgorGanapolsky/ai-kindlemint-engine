# 🚀 AI Assistant Quick Reference

## 📋 **Essential Commands**

```bash
# 1. ALWAYS START WITH THIS
cat docs/WORKTREE_STATUS.md

# 2. Verify worktree setup
git worktree list

# 3. Check current state
git status

# 4. Update status (manual)
./scripts/utilities/update_worktree_status.sh

# 5. Test MCP server
curl -s --connect-timeout 5 http://44.201.249.255:8080/health || echo "MCP server not responding"
```

## 🎯 **Key Files**

- `docs/WORKTREE_STATUS.md` ← **START HERE ALWAYS**
- `docs/AI_ASSISTANT_WORKFLOW.md` ← Full workflow
- `plan.md` ← Project roadmap
- `config/.worktree_orchestration_config.json` ← Settings

## 🔄 **Worktree Layout**

```
ai-kindlemint-engine/                    [feat/mcp-server-orchestration]
├── worktrees/
│   ├── main/                           [main] - Stable
│   ├── experiments/                    [experiments] - Testing
│   └── hotfix/                         [hotfix] - Emergency
```

## ⚡ **Quick Actions**

- **Emergency Fix**: `cd worktrees/hotfix`
- **Test Feature**: `cd worktrees/experiments`
- **Stable Work**: `cd worktrees/main`
- **Active Dev**: Stay in main directory

## 🎯 **Current Priority**

**MCP Server**: Fix connectivity at `44.201.249.255:8080`

---
*Read `docs/WORKTREE_STATUS.md` first - always!*
