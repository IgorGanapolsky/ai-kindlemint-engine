# Worktree Status: MCP Server & Orchestration

**Date:** $(date)

## Current State
- **MCP Server**: Deployed on AWS EC2 (Amazon Linux 2023) at `44.201.249.255:8080`
- **GitHub App**: MCP Orchestrator (App ID: 1554609)
- **Webhook**: Configured to `http://44.201.249.255:8080/webhook`
- **Private Key**: `/home/ec2-user/github-app-private-key.pem` (on EC2)
- **PAT**: Set as env var in Docker container
- **Docker Image**: `ghcr.io/github/github-mcp-server:latest`
- **Container Command**: `server http`
- **Permissions**: Minimal required for CI/CD and PR automation
- **Events Subscribed**: push, pull_request, check_suite, check_run, status (others optional)

## What Works
- MCP server starts and listens for webhooks
- GitHub App is registered and installed on repo
- All secrets and keys are in place

## Next Steps
- Confirm webhook delivery and agent actions in logs
- Add/modify agents for custom automation (CI/CD cleanup, PR auto-fix, etc.)
- Harden deployment (HTTPS, domain, scaling, monitoring)

## Recent Changes
- All setup steps, keys, and configuration are documented here for continuity
- README and plan.md to be updated to reflect MCP orchestration and automation

---
*This file is auto-updated to preserve orchestration state for seamless handoff across machines and sessions.*
