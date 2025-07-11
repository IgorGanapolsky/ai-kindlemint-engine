# Project Plan

## Current Focus (July 11, 2025)
- **PRIMARY**: Setting up official GitHub MCP Server (github/github-mcp-server)
- **INTEGRATION**: Claude Code GitHub Actions for AI-powered PR assistance
- **AUTOMATION**: Continuous PR monitoring with automatic CI fix capabilities

## Active Implementation
1. **Docker Installation** - Required for MCP server
2. **GitHub MCP Server** - Official implementation with webhook support
3. **Claude Code Actions** - Already configured, needs API key in secrets
4. **GitHub App Integration** - App ID 1554609 with private key authentication

## Immediate Tasks
- [ ] Install Docker on the system
- [ ] Deploy GitHub MCP server with docker-compose
- [ ] Add ANTHROPIC_API_KEY to GitHub repository secrets
- [ ] Test automated PR fixing on existing PRs (#185, #186, #187)
- [ ] Enable auto-merge for approved PRs (after testing)

## Architecture
- **MCP Server**: Handles GitHub webhooks, monitors PRs, orchestrates fixes
- **Claude Code**: Responds to @claude mentions for complex code changes
- **GitHub App**: Provides authenticated access to repository
- **Fallback**: Direct API orchestrator when Docker unavailable

## Reference
- See `docs/WORKTREE_STATUS.md` for the latest orchestration and deployment state. 