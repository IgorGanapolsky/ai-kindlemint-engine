# AI-Kindlemint-Engine

## Overview
AI-powered book publishing platform with automated publishing workflows and agentic orchestration.

## MCP Server Orchestration (Current Status)
- **MCP Server**: Deployed on AWS EC2 (Amazon Linux 2023) at `44.201.249.255:8080`
- **GitHub App**: MCP Orchestrator (App ID: 1554609)
- **Webhook**: Configured to `http://44.201.249.255:8080/webhook`
- **Private Key**: `/home/ec2-user/github-app-private-key.pem` (on EC2)
- **PAT**: Set as env var in Docker container
- **Docker Image**: `ghcr.io/github/github-mcp-server:latest`
- **Container Command**: `server http`
- **Permissions**: Minimal required for CI/CD and PR automation
- **Events Subscribed**: push, pull_request, check_suite, check_run, status (others optional)

## How to Resume Work
- See `docs/WORKTREE_STATUS.md` for the latest orchestration and deployment state.
- All keys, secrets, and configuration steps are documented there for seamless handoff.

## Quickstart
1. Launch EC2 instance and ensure Docker is installed.
2. Upload your GitHub App private key to `/home/ec2-user/github-app-private-key.pem`.
3. Run the MCP server Docker container with the documented environment variables.
4. Confirm webhook delivery and agent actions in logs.

## Plan
See `plan.md` for the current project roadmap and next steps.