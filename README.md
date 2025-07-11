# AI-Kindlemint-Engine

## Overview
AI-powered book publishing platform with automated publishing workflows and agentic orchestration.

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

## How to Resume Work
- See `docs/WORKTREE_STATUS.md` for the latest orchestration and deployment state.
- All keys, secrets, and configuration steps are documented there for seamless handoff.

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

## Plan
See `plan.md` for the current project roadmap and next steps.
