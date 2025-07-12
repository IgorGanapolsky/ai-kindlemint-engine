# AI-KindleMint-Engine 🚀

Automated puzzle book publishing system leveraging AI for content generation, quality assurance, and marketing.

<<<<<<< HEAD
## 🎯 Current Focus: $300/Day Revenue Goal
=======
## GitHub Workflow Orchestration

### Current Implementation (July 2025)
- **Primary**: Official GitHub MCP Server (github/github-mcp-server) with Docker
- **GitHub App**: MCP Orchestrator (App ID: 1554609) with webhook integration
- **Claude Code Integration**: GitHub Actions for AI-powered PR assistance
- **Fallback**: Direct API via `scripts/github_workflow_orchestrator.py` when Docker unavailable

### Key Components
1. **GitHub MCP Server** (Port 8080)
   - Continuous PR monitoring
   - Automatic CI failure detection and fixing
   - GitHub App webhook handling
   - Real-time PR status updates

2. **Claude Code GitHub Actions**
   - Responds to @claude mentions in issues/PRs
   - Automated code implementation
   - Follows CLAUDE.md guidelines

3. **Automated Capabilities**
   - Fix linting errors automatically
   - Resolve test failures
   - Handle dependency issues
   - Auto-merge when all checks pass (configurable)
>>>>>>> origin

We're implementing a systematic approach to reach $300/day in revenue through our automated puzzle book publishing system.

<<<<<<< HEAD
### 🚀 Traffic Generation System (MERGED TO MAIN)
=======
## For AI Assistants
- **ALWAYS START HERE**: Read `docs/WORKTREE_STATUS.md` first to understand current state
- **Follow Workflow**: See `docs/AI_ASSISTANT_WORKFLOW.md` for handoff process
- **Update Status**: Use `scripts/utilities/update_worktree_status.sh` to maintain state
- **Key Principle**: Never start work without reading the status file first

## Quickstart

### Docker + MCP Server Setup (Recommended)
1. Install Docker: `./install_docker.sh`
2. Set up MCP server: `./setup_github_mcp_server.sh`
3. Set environment variables:
   ```bash
   export GITHUB_TOKEN='your-github-pat'
   export ANTHROPIC_API_KEY='your-anthropic-key'
   ```
4. Start monitoring: `docker compose -f docker-compose.mcp.yml up -d`

### Direct API Setup (No Docker)
1. Set GitHub PAT: `export GITHUB_TOKEN='your-pat-here'`
2. Start monitoring: `./start_pr_monitor.sh`

### Claude Code GitHub Actions
- Already configured in `.github/workflows/claude-code.yml`
- Add `ANTHROPIC_API_KEY` to repository secrets
- Mention @claude in any issue or PR comment
>>>>>>> origin

**Status**: Production-ready traffic system now in main branch
- **Reddit System**: Manual posting ready - generates 200-500 visitors/day
- **Pinterest**: Automation script ready (pending API key)
- **Facebook**: Engagement script ready (pending Chrome setup)
- **Revenue Projection**: $122-256/day from Reddit alone, $600+/day full system

**Quick Start**:
```bash
cd scripts/traffic_generation
python3 reddit_quick_start.py  # Generate Reddit content
./setup_traffic_generation.sh   # Full setup guide
```

**⚠️ CRITICAL**: Update Gumroad price to $4.99 (see UPDATE_GUMROAD_NOW.md)

### 💰 Revenue Path
- **Landing Page**: ✅ LIVE at https://dvdyff0b2oove.cloudfront.net
- **Email Capture**: ✅ Working (Web3Forms)
- **Frontend Product**: $4.99 puzzle books (UPDATE PRICE!)
- **Backend Product**: $97 "Create Your Own Puzzle Book" course
- **Projected**: $600+/day with full traffic system

## 🛠️ Automated Systems

### Code Hygiene (NEW!)
- **GitHub Action**: Enforces hygiene on every PR
- **Pre-commit Hooks**: Catches issues before commit
- **Weekly Cleanup**: Automated maintenance
- **Setup**: `./scripts/setup_hygiene_automation.sh`

### MCP Server Orchestration
- **Branch**: `feat/mcp-server-orchestration`
- **Tools**: GitHub workflow automation, PR management
- **Status**: Infrastructure ready, AWS deployment pending

### Worktree Strategy
- **Main**: Feature development
- **Experiments**: Traffic generation system ✅
- **Hotfix**: Emergency fixes

## 🏗️ Architecture

```
ai-kindlemint-engine/
├── src/kindlemint/        # Core engine
├── scripts/               # Automation scripts
├── agents/               # AI orchestration agents
├── worktrees/           # Git worktrees for parallel development
│   ├── experiments/     # Traffic generation system
│   ├── hotfix/         # Emergency fixes
│   └── main/           # Stable main branch
└── docs/               # Documentation
```

## 🚀 Quick Start

### Install & Setup
```bash
pip install -e .
./scripts/setup_hygiene_automation.sh
```

### Generate Traffic NOW
```bash
cd worktrees/experiments/scripts/traffic_generation
python3 reddit_quick_start.py
```

### Run Tests
```bash
python -m pytest tests/ -v
```

### Check Code Hygiene
```bash
git hygiene  # Alias for hygiene check
```

## 📊 Key Metrics
- **Goal**: $300/day revenue
- **Traffic Target**: 1000+ visitors/day
- **Conversion Path**: Traffic → Email (25%) → Sale (10%) → Backend (20%)
- **Current Status**: Traffic system deployed, awaiting activation

## 🔧 Development

### Commit Standards
- ✅ Automated hygiene checks on every PR
- ✅ Pre-commit hooks for code quality
- ✅ Conventional commits enforced

### Testing
- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- Coverage target: 80%+

## 📚 Documentation
- [Automated Hygiene](docs/AUTOMATED_HYGIENE.md) - Code quality enforcement
- [Worktree Status](docs/WORKTREE_STATUS.md) - Current development state
- [Revenue Roadmap](docs/REVENUE_ROADMAP_300_DAY.md) - Path to $300/day
- [Claude Integration](docs/CLAUDE.md) - AI assistant configuration

## 🤝 Contributing
See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📄 License
MIT License - see [LICENSE](LICENSE) file.

---

**Remember**: Every commit should move us closer to $300/day! 💰