#!/bin/bash
# Secure Environment Setup for GitHub MCP Server
# This script helps you set up environment variables securely

echo "🔐 Secure GitHub MCP Server Environment Setup"
echo "=============================================="
echo ""

echo "⚠️  SECURITY NOTICE:"
echo "The GitHub App credentials were previously hardcoded in scripts."
echo "This has been fixed - all scripts now use environment variables."
echo ""

echo "📋 Required Environment Variables:"
echo "=================================="
echo ""

echo "1. GITHUB_APP_ID (your GitHub App ID)"
echo "   Example: export GITHUB_APP_ID='1554609'"
echo ""

echo "2. GITHUB_CLIENT_ID (your GitHub App Client ID)"
echo "   Example: export GITHUB_CLIENT_ID='Iv23limbdVHqB1FKtnxK'"
echo ""

echo "3. GITHUB_TOKEN (your Personal Access Token)"
echo "   Example: export GITHUB_TOKEN='ghp_xxxxxxxxxxxx'"
echo ""

echo "4. ANTHROPIC_API_KEY (for Claude integration)"
echo "   Example: export ANTHROPIC_API_KEY='sk-xxxxxxxxxxxx'"
echo ""

echo "🚀 Setup Instructions:"
echo "======================"
echo ""

echo "1. Add these to your ~/.bashrc or ~/.zshrc:"
echo "   echo 'export GITHUB_APP_ID=\"YOUR_APP_ID\"' >> ~/.bashrc"
echo "   echo 'export GITHUB_CLIENT_ID=\"YOUR_CLIENT_ID\"' >> ~/.bashrc"
echo "   echo 'export GITHUB_TOKEN=\"YOUR_TOKEN\"' >> ~/.bashrc"
echo "   echo 'export ANTHROPIC_API_KEY=\"YOUR_API_KEY\"' >> ~/.bashrc"
echo ""

echo "2. Reload your shell:"
echo "   source ~/.bashrc"
echo ""

echo "3. Verify environment variables are set:"
echo "   echo \$GITHUB_APP_ID"
echo "   echo \$GITHUB_CLIENT_ID"
echo "   echo \$GITHUB_TOKEN (should show your token)"
echo "   echo \$ANTHROPIC_API_KEY (should show your key)"
echo ""

echo "🔒 Security Best Practices:"
echo "==========================="
echo ""
echo "- Never commit credentials to Git"
echo "- Use environment variables or secret management"
echo "- Rotate keys regularly"
echo "- Use minimal required permissions"
echo "- Store private keys securely (chmod 600)"
echo ""

echo "✅ Once environment variables are set, you can:"
echo "- Run: ./setup_github_mcp_server.sh"
echo "- Run: docker-compose up -d"
echo "- Use all MCP server tools securely"
echo ""

# Check if variables are already set
echo "🔍 Current Environment Status:"
echo "=============================="

check_var() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -n "$var_value" ]; then
        echo "✅ $var_name: Set (${var_value:0:10}...)"
    else
        echo "❌ $var_name: Not set"
    fi
}

check_var "GITHUB_APP_ID"
check_var "GITHUB_CLIENT_ID" 
check_var "GITHUB_TOKEN"
check_var "ANTHROPIC_API_KEY"

echo ""
echo "📝 Need your GitHub App credentials?"
echo "1. Go to: https://github.com/settings/apps"
echo "2. Click on your app 'MCP Orchestrator'"
echo "3. Copy the App ID and Client ID"
echo "4. Generate a new private key if needed"
echo ""

echo "🎯 Ready to proceed? Run your MCP setup commands!"