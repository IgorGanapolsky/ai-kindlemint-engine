# MCP Server Deployment Guide

## Overview
This guide documents the MCP (Model Context Protocol) server deployment for automated CI/CD and PR management.

## Current Deployment Status
- **Server**: AWS EC2 (Amazon Linux 2023)
- **IP Address**: 44.201.249.255
- **Port**: 8080
- **GitHub App**: MCP Orchestrator (App ID: 1554609)
- **Status**: Deployed but not responding (needs investigation)

## Architecture Components

### 1. MCP Server
- Running in Docker container: `ghcr.io/github/github-mcp-server:latest`
- Command: `server http`
- Webhook endpoint: `http://44.201.249.255:8080/webhook`

### 2. GitHub App Configuration
- **Permissions Required**:
  - Actions: Read & Write
  - Checks: Read & Write
  - Contents: Read & Write
  - Issues: Write (for PR comments)
  - Pull requests: Read & Write
  - Workflows: Write

- **Events Subscribed**:
  - push
  - pull_request
  - check_suite
  - check_run
  - workflow_run
  - status

### 3. Automation Agents

#### CI/CD Cleanup Agent (`scripts/agents/cicd_cleanup_agent.py`)
- Automatically cancels and deletes failed workflow runs
- Cleans up stale checks on PRs
- Runs on schedule (every 6 hours) and webhook triggers

#### PR Auto-Fix Agent (`scripts/agents/pr_autofix_agent.py`)
- Fixes formatting issues
- Resolves simple merge conflicts
- Applies linting fixes
- Comments on PRs with applied fixes

## Management Tools

### MCP Server Tools (`scripts/mcp_server_tools.py`)
```bash
# Check server status
python3 scripts/mcp_server_tools.py status

# Test webhook endpoint
python3 scripts/mcp_server_tools.py test-webhook

# Send test PR event
python3 scripts/mcp_server_tools.py test-pr

# Monitor webhook activity
python3 scripts/mcp_server_tools.py monitor

# Run all checks
python3 scripts/mcp_server_tools.py all
```

## Deployment Steps

### 1. EC2 Instance Setup
```bash
# SSH into EC2 instance
ssh -i /path/to/key.pem ec2-user@44.201.249.255

# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Deploy MCP Server
```bash
# Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  mcp-server:
    image: ghcr.io/github/github-mcp-server:latest
    ports:
      - "8080:8080"
    environment:
      - GITHUB_APP_ID=1554609
      - GITHUB_APP_PRIVATE_KEY_PATH=/app/github-app-private-key.pem
      - GITHUB_TOKEN=\${GITHUB_TOKEN}
    volumes:
      - ./github-app-private-key.pem:/app/github-app-private-key.pem:ro
    command: server http
    restart: unless-stopped
EOF

# Start the server
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 3. Configure Security Group
Ensure EC2 security group allows:
- Inbound: Port 8080 from GitHub webhook IPs
- Outbound: HTTPS (443) to GitHub API

### 4. Set Up HTTPS (TODO)
```bash
# Install Certbot
sudo yum install -y certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Update docker-compose.yml to use HTTPS
```

## Monitoring

### Check Server Health
```bash
# From local machine
curl http://44.201.249.255:8080/health

# From EC2 instance
docker ps
docker logs $(docker ps -q)
```

### Webhook Delivery
1. Go to GitHub App settings
2. Navigate to "Advanced" tab
3. Check "Recent Deliveries" section
4. Verify webhook responses

## Troubleshooting

### Server Not Responding
1. Check EC2 instance status in AWS Console
2. Verify Docker container is running
3. Check security group rules
4. Review Docker logs for errors

### Webhook Failures
1. Verify GitHub App private key is correct
2. Check webhook URL configuration
3. Ensure server has internet connectivity
4. Review webhook delivery logs in GitHub

### Agent Issues
1. Verify GitHub token has required permissions
2. Check agent logs in MCP server
3. Test agents locally before deployment
4. Ensure webhook events are properly configured

## Next Steps

1. **Immediate**: Investigate why server is not responding
2. **High Priority**: Set up HTTPS with proper domain
3. **Medium Priority**: Implement monitoring and alerting
4. **Future**: Add more automation agents as needed

## Security Considerations

- Never commit private keys or tokens
- Use environment variables for sensitive data
- Regularly rotate GitHub tokens
- Monitor for unusual webhook activity
- Keep Docker images updated

## References

- [MCP Documentation](https://github.com/github/mcp)
- [GitHub Apps Documentation](https://docs.github.com/en/developers/apps)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)