# AI-Kindlemint-Engine

## Overview
AI-powered book publishing platform with automated publishing workflows and agentic orchestration.

## GitHub Workflow Orchestration (Current Approach)
- **Strategy**: Direct GitHub API integration using Personal Access Token (PAT)
- **Orchestrator Script**: `scripts/github_workflow_orchestrator.py` - Full workflow automation
- **GitHub App**: MCP Orchestrator (App ID: 1554609) - Configured for future use
- **Previous MCP Server**: EC2 at `44.201.249.255:8080` (currently offline due to AWS creds)
- **Current Method**: GitHub PAT with workflow dispatch and API automation
- **Capabilities**: 
  - Trigger any workflow on demand
  - Monitor workflow runs in real-time
  - Automate PR labeling, reviews, and merging
  - Direct API access without webhook dependencies

## How to Resume Work
- See `docs/WORKTREE_STATUS.md` for the latest orchestration and deployment state.
- All keys, secrets, and configuration steps are documented there for seamless handoff.

## For AI Assistants
- **ALWAYS START HERE**: Read `docs/WORKTREE_STATUS.md` first to understand current state
- **Follow Workflow**: See `docs/AI_ASSISTANT_WORKFLOW.md` for handoff process
- **Update Status**: Use `scripts/utilities/update_worktree_status.sh` to maintain state
- **Key Principle**: Never start work without reading the status file first

## Quickstart
1. Set your GitHub PAT: `export GITHUB_TOKEN='your-pat-here'`
2. List workflows: `python3 scripts/github_workflow_orchestrator.py list`
3. Trigger a workflow: `python3 scripts/github_workflow_orchestrator.py trigger <workflow_id>`
4. Monitor runs: `python3 scripts/github_workflow_orchestrator.py runs`
5. For MCP server setup (when Docker available), see `docs/WORKTREE_STATUS.md`

## Plan
See `plan.md` for the current project roadmap and next steps.
