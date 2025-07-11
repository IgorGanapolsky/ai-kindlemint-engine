#!/bin/bash
# Setup script for GitHub MCP Server with GitHub App

echo "🚀 GitHub MCP Server Setup"
echo "========================="

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN not set"
    echo "Please run: export GITHUB_TOKEN='your-github-pat'"
    exit 1
fi

echo "✅ GitHub token found"

# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh

# Check for private key
PRIVATE_KEY_PATH="$HOME/.ssh/github-mcp-orchestrator.private-key.pem"

if [ ! -f "$PRIVATE_KEY_PATH" ]; then
    echo ""
    echo "⚠️  GitHub App private key not found at: $PRIVATE_KEY_PATH"
    echo ""
    echo "To set up your GitHub App private key:"
    echo "1. Go to https://github.com/settings/apps"
    echo "2. Click on your app 'MCP Orchestrator' (App ID: 1554609)"
    echo "3. Generate a new private key"
    echo "4. Save it as: $PRIVATE_KEY_PATH"
    echo "5. Set permissions: chmod 600 $PRIVATE_KEY_PATH"
    echo ""
    echo "For now, we'll use direct API mode without the MCP server."
    echo ""
fi

# Check Docker availability
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    
    # Check docker-compose
    if command -v docker-compose &> /dev/null; then
        echo "✅ docker-compose is installed"
        DOCKER_AVAILABLE=true
    else
        echo "❌ docker-compose not found"
        DOCKER_AVAILABLE=false
    fi
else
    echo "❌ Docker not installed"
    echo "To use MCP server, install Docker: https://docs.docker.com/get-docker/"
    DOCKER_AVAILABLE=false
fi

echo ""
echo "Configuration Summary:"
echo "====================="
echo "GitHub Token: ✅ Set"
echo "GitHub App ID: 1554609"
echo "Repository: IgorGanapolsky/ai-kindlemint-engine"
echo "Private Key: $([ -f "$PRIVATE_KEY_PATH" ] && echo "✅ Found" || echo "❌ Missing")"
echo "Docker: $([ "$DOCKER_AVAILABLE" = true ] && echo "✅ Available" || echo "❌ Not Available")"
echo ""

# Make orchestrator script executable
chmod +x scripts/github_mcp_orchestrator.py

echo "Available Commands:"
echo "=================="
echo ""
echo "1. Monitor PRs continuously (auto-fix CI failures):"
echo "   python3 scripts/github_mcp_orchestrator.py monitor"
echo ""
echo "2. Check current PR status:"
echo "   python3 scripts/github_mcp_orchestrator.py status"
echo ""
echo "3. Setup MCP server (requires Docker):"
echo "   python3 scripts/github_mcp_orchestrator.py setup"
echo ""

if [ "$DOCKER_AVAILABLE" = false ]; then
    echo "Note: Running in direct API mode (no Docker/MCP server)"
    echo "This mode can still:"
    echo "  - Monitor all PRs"
    echo "  - Detect CI failures"
    echo "  - Trigger fix workflows"
    echo "  - Auto-format code"
    echo ""
fi

echo "Ready to start monitoring! 🎯"