#!/bin/bash
# Setup official GitHub MCP Server from github/github-mcp-server

echo "🚀 Setting up Official GitHub MCP Server"
echo "======================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed!"
    echo "Run: ./install_docker.sh first"
    exit 1
fi

echo "✅ Docker found"

# Clone the official GitHub MCP server
echo "📦 Cloning github/github-mcp-server..."
if [ ! -d "github-mcp-server" ]; then
    git clone https://github.com/github/github-mcp-server.git
else
    echo "Repository already exists, pulling latest..."
    cd github-mcp-server && git pull && cd ..
fi

# Create configuration
echo "📝 Creating MCP server configuration..."
cat > github-mcp-server-config.json << EOF
{
  "github": {
    "app_id": 1554609,
    "client_id": "Iv23limbdVHqB1FKtnxK",
    "webhook_secret": "your-webhook-secret",
    "private_key_path": "/app/github-app-private-key.pem"
  },
  "server": {
    "port": 8080,
    "host": "0.0.0.0"
  },
  "repository": {
    "owner": "IgorGanapolsky",
    "name": "ai-kindlemint-engine"
  },
  "automation": {
    "auto_fix_ci": true,
    "auto_merge": false,
    "pr_monitoring_interval": 300
  }
}
EOF

# Create docker-compose for MCP server
echo "🐳 Creating docker-compose configuration..."
cat > docker-compose.mcp.yml << 'EOF'
version: '3.8'

services:
  github-mcp-server:
    build: ./github-mcp-server
    container_name: github-mcp-server
    ports:
      - "8080:8080"
    environment:
      - GITHUB_APP_ID=1554609
      - GITHUB_CLIENT_ID=Iv23limbdVHqB1FKtnxK
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - CONFIG_PATH=/app/config.json
    volumes:
      - ./github-mcp-server-config.json:/app/config.json:ro
      - ~/.ssh/github-mcp-orchestrator.private-key.pem:/app/github-app-private-key.pem:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - mcp-network

  claude-code-integration:
    image: anthropic/claude-code:latest
    container_name: claude-code-mcp
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - MCP_SERVER_URL=http://github-mcp-server:8080
    depends_on:
      - github-mcp-server
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
EOF

echo ""
echo "✅ Setup files created!"
echo ""
echo "Next steps:"
echo "1. Ensure your GitHub App private key is at: ~/.ssh/github-mcp-orchestrator.private-key.pem"
echo "2. Set environment variables:"
echo "   export GITHUB_TOKEN='your-github-pat'"
echo "   export ANTHROPIC_API_KEY='your-anthropic-key'"
echo "3. Start the MCP server:"
echo "   docker compose -f docker-compose.mcp.yml up -d"
echo "4. Check server health:"
echo "   curl http://localhost:8080/health"
echo ""
echo "The server will:"
echo "- Monitor all PRs continuously"
echo "- Auto-fix CI failures"
echo "- Integrate with Claude Code for intelligent fixes"
echo "- Handle GitHub webhooks for real-time updates"