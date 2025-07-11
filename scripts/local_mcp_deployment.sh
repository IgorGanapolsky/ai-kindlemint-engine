#!/bin/bash
# Local MCP Server Testing and Manual EC2 Deployment Guide
set -e

echo "🚀 MCP Server Local Testing & EC2 Recovery Guide"
echo "==============================================="

# Configuration
GITHUB_APP_ID="1554609"
GITHUB_APP_PRIVATE_KEY_PATH="$HOME/.ssh/github-mcp-orchestrator.private-key.pem"
EC2_IP="44.201.249.255"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}Current Situation:${NC}"
echo "- EC2 instance at $EC2_IP is not responding"
echo "- AWS credentials are expired"
echo "- GitHub App private key is available"
echo ""

echo -e "${BLUE}Option 1: Local Testing with Docker${NC}"
echo "========================================="
echo ""
echo "1. Install Docker locally (if not installed):"
echo "   sudo apt update && sudo apt install docker.io docker-compose"
echo ""
echo "2. Create local docker-compose.yml:"
cat << 'EOF'
cat > docker-compose.yml << 'COMPOSE'
version: '3.8'
services:
  mcp-server:
    image: ghcr.io/github/github-mcp-server:latest
    ports:
      - "8080:8080"
    environment:
      - GITHUB_APP_ID=1554609
      - GITHUB_APP_PRIVATE_KEY_PATH=/app/github-app-private-key.pem
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    volumes:
      - ~/.ssh/github-mcp-orchestrator.private-key.pem:/app/github-app-private-key.pem:ro
    command: server http
    restart: unless-stopped
COMPOSE
EOF

echo ""
echo "3. Set GitHub token and start locally:"
echo "   export GITHUB_TOKEN='your-github-token'"
echo "   docker-compose up -d"
echo ""
echo "4. Test local server:"
echo "   curl http://localhost:8080/health"
echo ""

echo -e "${BLUE}Option 2: Manual EC2 Recovery${NC}"
echo "====================================="
echo ""
echo "Since AWS CLI access is not available, use AWS Web Console:"
echo ""
echo "1. Login to AWS Console: https://console.aws.amazon.com"
echo ""
echo "2. Navigate to EC2 Dashboard → Instances"
echo ""
echo "3. Search for instance with IP: $EC2_IP"
echo ""
echo "4. Check instance status:"
echo "   - If STOPPED: Start the instance"
echo "   - If RUNNING: Check Security Group allows port 8080"
echo "   - If TERMINATED: Create new instance (see below)"
echo ""
echo "5. If SSH key is wrong, create new instance:"
echo "   a. Go to EC2 → Key Pairs → Create key pair"
echo "   b. Name: mcp-server-key"
echo "   c. Download the .pem file"
echo "   d. Launch new t2.micro instance with:"
echo "      - AMI: Amazon Linux 2023"
echo "      - Security group: Allow ports 22 and 8080"
echo "      - User data script (paste in Advanced Details):"
echo ""
cat << 'USERDATA'
#!/bin/bash
yum update -y
yum install -y docker
service docker start
usermod -a -G docker ec2-user
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
systemctl enable docker
USERDATA

echo ""
echo -e "${BLUE}Option 3: Using ngrok for Local Development${NC}"
echo "=============================================="
echo ""
echo "Run MCP server locally and expose via ngrok:"
echo ""
echo "1. Install ngrok: https://ngrok.com/download"
echo ""
echo "2. Start local MCP server (see Option 1)"
echo ""
echo "3. Expose via ngrok:"
echo "   ngrok http 8080"
echo ""
echo "4. Update GitHub webhook URL to ngrok URL"
echo ""

echo -e "${BLUE}Required Files for EC2 Deployment${NC}"
echo "===================================="
echo ""
echo "When you can access EC2 (via new credentials or fixed instance):"
echo ""
echo "1. Copy these files to EC2:"
echo "   scp -i your-key.pem docker-compose.yml ec2-user@EC2_IP:~/"
echo "   scp -i your-key.pem $GITHUB_APP_PRIVATE_KEY_PATH ec2-user@EC2_IP:~/github-app-private-key.pem"
echo ""
echo "2. SSH to instance and run:"
echo "   ssh -i your-key.pem ec2-user@EC2_IP"
echo "   cd ~"
echo "   docker-compose up -d"
echo "   docker logs -f \$(docker ps -q)"
echo ""

echo -e "${YELLOW}GitHub App Configuration${NC}"
echo "=========================="
echo "App ID: $GITHUB_APP_ID"
echo "Webhook URL: http://$EC2_IP:8080/webhook (or your ngrok URL)"
echo "Required permissions:"
echo "- Actions: Read & Write"
echo "- Checks: Read & Write"
echo "- Contents: Read & Write"
echo "- Issues: Write"
echo "- Pull requests: Read & Write"
echo "- Workflows: Write"
echo ""

echo -e "${GREEN}Next Steps:${NC}"
echo "1. Choose one of the options above based on your needs"
echo "2. For production: Get new AWS credentials and run deploy_mcp_server.sh"
echo "3. For development: Use local Docker or ngrok"
echo "4. Update GitHub webhook URL after deployment"
echo ""

# Generate docker-compose.yml for convenience
echo "Generating docker-compose.yml in current directory..."
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  mcp-server:
    image: ghcr.io/github/github-mcp-server:latest
    ports:
      - "8080:8080"
    environment:
      - GITHUB_APP_ID=1554609
      - GITHUB_APP_PRIVATE_KEY_PATH=/app/github-app-private-key.pem
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    volumes:
      - ~/.ssh/github-mcp-orchestrator.private-key.pem:/app/github-app-private-key.pem:ro
    command: server http
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF

echo -e "${GREEN}✅ Created docker-compose.yml${NC}"
echo ""
echo "To start locally:"
echo "  export GITHUB_TOKEN='your-token-here'"
echo "  docker-compose up -d"