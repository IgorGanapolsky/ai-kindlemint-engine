#!/bin/bash
# Deploy MCP Server to AWS EC2
set -e

echo "🚀 MCP Server AWS Deployment Script"
echo "===================================="

# Configuration
GITHUB_APP_ID="${GITHUB_APP_ID:-1554609}"
GITHUB_APP_PRIVATE_KEY_PATH="$HOME/.ssh/github-mcp-orchestrator.private-key.pem"
EXISTING_EC2_IP="44.201.249.255"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to create docker-compose.yml
create_docker_compose() {
    cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  mcp-server:
    image: ghcr.io/github/github-mcp-server:latest
    ports:
      - "8080:8080"
    environment:
      - GITHUB_APP_ID=${GITHUB_APP_ID}
      - GITHUB_APP_PRIVATE_KEY_PATH=/app/github-app-private-key.pem
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    volumes:
      - ./github-app-private-key.pem:/app/github-app-private-key.pem:ro
    command: server http
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF
}

# Function to create user data script for EC2
create_user_data() {
    cat > user_data.sh << 'EOF'
#!/bin/bash
# Update system
yum update -y

# Install Docker
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create app directory
mkdir -p /home/ec2-user/mcp-server
cd /home/ec2-user/mcp-server

# Start Docker service on boot
systemctl enable docker
EOF
}

# Check prerequisites
echo "Checking prerequisites..."

if [ ! -f "$GITHUB_APP_PRIVATE_KEY_PATH" ]; then
    echo -e "${RED}❌ GitHub App private key not found at: $GITHUB_APP_PRIVATE_KEY_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GitHub App private key found${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI installed${NC}"

# Test AWS credentials
echo "Testing AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not valid or expired${NC}"
    echo ""
    echo "Please configure AWS credentials:"
    echo "  aws configure"
    echo ""
    echo "Or set environment variables:"
    echo "  export AWS_ACCESS_KEY_ID=your-key"
    echo "  export AWS_SECRET_ACCESS_KEY=your-secret"
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials valid${NC}"

# Menu options
echo ""
echo "Choose deployment option:"
echo "1) Try to fix existing EC2 instance ($EXISTING_EC2_IP)"
echo "2) Create new EC2 instance"
echo "3) Generate deployment files only"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Attempting to fix existing EC2 instance..."
        echo ""
        echo "Since SSH is not working, we'll try alternative approaches:"
        echo ""
        echo "Option A: Use AWS Systems Manager (if installed on instance)"
        echo "  aws ssm start-session --target i-xxxxxxxxx"
        echo ""
        echo "Option B: Create new key pair and update instance"
        echo "  1. Create new key pair in EC2 console"
        echo "  2. Stop instance"
        echo "  3. Create AMI from instance"
        echo "  4. Launch new instance from AMI with new key pair"
        echo ""
        echo "Option C: Check EC2 instance status"
        aws ec2 describe-instances --filters "Name=ip-address,Values=$EXISTING_EC2_IP" \
            --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress,KeyName]' \
            --output table 2>/dev/null || echo "Cannot retrieve instance info"
        ;;
    
    2)
        echo ""
        echo "Creating new EC2 instance..."
        
        # Create security group
        echo "Creating security group..."
        SG_ID=$(aws ec2 create-security-group \
            --group-name mcp-server-sg \
            --description "Security group for MCP server" \
            --query 'GroupId' --output text 2>/dev/null || echo "")
        
        if [ -n "$SG_ID" ]; then
            echo -e "${GREEN}✅ Created security group: $SG_ID${NC}"
            
            # Add rules
            aws ec2 authorize-security-group-ingress \
                --group-id $SG_ID \
                --protocol tcp --port 8080 --cidr 0.0.0.0/0
            aws ec2 authorize-security-group-ingress \
                --group-id $SG_ID \
                --protocol tcp --port 22 --cidr 0.0.0.0/0
        else
            echo -e "${YELLOW}⚠️  Using default security group${NC}"
        fi
        
        # Create key pair
        echo "Creating new key pair..."
        KEY_NAME="mcp-server-key-$(date +%s)"
        aws ec2 create-key-pair --key-name $KEY_NAME \
            --query 'KeyMaterial' --output text > ~/.ssh/$KEY_NAME.pem
        chmod 400 ~/.ssh/$KEY_NAME.pem
        echo -e "${GREEN}✅ Created key pair: $KEY_NAME${NC}"
        
        # Launch instance
        echo "Launching EC2 instance..."
        create_user_data
        
        INSTANCE_ID=$(aws ec2 run-instances \
            --image-id ami-0c02fb55956c7d316 \
            --instance-type t2.micro \
            --key-name $KEY_NAME \
            --security-groups ${SG_ID:-default} \
            --user-data file://user_data.sh \
            --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=mcp-server}]' \
            --query 'Instances[0].InstanceId' --output text)
        
        echo -e "${GREEN}✅ Launched instance: $INSTANCE_ID${NC}"
        
        # Wait for instance
        echo "Waiting for instance to be running..."
        aws ec2 wait instance-running --instance-ids $INSTANCE_ID
        
        # Get public IP
        PUBLIC_IP=$(aws ec2 describe-instances \
            --instance-ids $INSTANCE_ID \
            --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
        
        echo -e "${GREEN}✅ Instance running at: $PUBLIC_IP${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Wait 2-3 minutes for instance initialization"
        echo "2. SSH to instance: ssh -i ~/.ssh/$KEY_NAME.pem ec2-user@$PUBLIC_IP"
        echo "3. Copy files and start MCP server"
        echo ""
        echo "Update GitHub webhook URL to: http://$PUBLIC_IP:8080/webhook"
        ;;
    
    3)
        echo ""
        echo "Generating deployment files..."
        create_docker_compose
        create_user_data
        
        echo -e "${GREEN}✅ Created docker-compose.yml${NC}"
        echo -e "${GREEN}✅ Created user_data.sh${NC}"
        echo ""
        echo "Manual deployment steps:"
        echo "1. Copy files to EC2 instance"
        echo "2. Copy GitHub App private key"
        echo "3. Run: docker-compose up -d"
        ;;
esac

echo ""
echo "📚 Documentation: docs/MCP_SERVER_DEPLOYMENT.md"
echo "🔧 Management: python3 scripts/mcp_server_tools.py"