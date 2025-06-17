#!/bin/bash
# V3 Zero-Touch Publishing Engine - Complete Deployment Script

set -e

echo "🚀 V3 Zero-Touch Publishing Engine Deployment Starting..."

# Configuration
PROJECT_NAME="kindlemint-v3"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-kdp-publisher"

# Check required environment variables
required_vars=("KDP_EMAIL" "KDP_PASSWORD" "OPENAI_API_KEY" "SLACK_WEBHOOK_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var environment variable is required"
        exit 1
    fi
done

echo "📋 Configuration:"
echo "  Project: $PROJECT_NAME"
echo "  Region: $AWS_REGION"
echo "  Account: $AWS_ACCOUNT_ID"
echo "  ECR Repo: $ECR_REPOSITORY"

# Create ECR repository if it doesn't exist
echo "📦 Creating ECR repository..."
aws ecr describe-repositories --repository-names "${PROJECT_NAME}-kdp-publisher" --region $AWS_REGION >/dev/null 2>&1 || {
    echo "Creating new ECR repository: ${PROJECT_NAME}-kdp-publisher"
    aws ecr create-repository \
        --repository-name "${PROJECT_NAME}-kdp-publisher" \
        --image-scanning-configuration scanOnPush=true \
        --region $AWS_REGION
}

# Get ECR login token
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY

# Build and push Docker image
echo "🐳 Building Docker image..."
cd "$(dirname "$0")/.."  # Go to project root

# Build the image
docker build -f docker/Dockerfile -t "${PROJECT_NAME}-kdp-publisher:latest" .

# Tag for ECR
docker tag "${PROJECT_NAME}-kdp-publisher:latest" "$ECR_REPOSITORY:latest"

# Push to ECR
echo "📤 Pushing Docker image to ECR..."
docker push "$ECR_REPOSITORY:latest"

# Deploy CloudFormation stack
echo "☁️  Deploying CloudFormation infrastructure..."
aws cloudformation deploy \
    --template-file infrastructure/fargate-deployment.yaml \
    --stack-name "$PROJECT_NAME-infrastructure" \
    --parameter-overrides \
        ProjectName="$PROJECT_NAME" \
        ECRRepository="$ECR_REPOSITORY:latest" \
        KDPEmail="$KDP_EMAIL" \
        KDPPassword="$KDP_PASSWORD" \
        OpenAIAPIKey="$OPENAI_API_KEY" \
        SlackWebhookURL="$SLACK_WEBHOOK_URL" \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION

# Get CloudFormation outputs
echo "📋 Getting deployment outputs..."
FARGATE_INVOKER_ARN=$(aws cloudformation describe-stacks \
    --stack-name "$PROJECT_NAME-infrastructure" \
    --query 'Stacks[0].Outputs[?OutputKey==`FargateInvokerFunctionArn`].OutputValue' \
    --output text \
    --region $AWS_REGION)

CLUSTER_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$PROJECT_NAME-infrastructure" \
    --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' \
    --output text \
    --region $AWS_REGION)

echo "✅ V3 Zero-Touch Publishing Engine Deployed Successfully!"
echo ""
echo "🎯 Deployment Summary:"
echo "  ✅ ECR Repository: $ECR_REPOSITORY"
echo "  ✅ ECS Cluster: $CLUSTER_NAME"
echo "  ✅ Fargate Invoker: $FARGATE_INVOKER_ARN"
echo "  ✅ Docker Image: Built and pushed"
echo "  ✅ Infrastructure: Deployed via CloudFormation"
echo ""
echo "🚀 Next Steps:"
echo "  1. Test Fargate task execution"
echo "  2. Update Lambda orchestration to use Fargate invoker"
echo "  3. Configure EventBridge schedule for daily execution"
echo "  4. Monitor Slack notifications for publishing results"
echo ""
echo "💰 Your first dollar is now within reach!"

# Create a test payload for manual testing
cat > /tmp/test-payload.json <<EOF
{
  "book_id": "test_$(date +%s)",
  "s3_bucket": "kindlemint-books",
  "manuscript_key": "manuscripts/test_book.docx",
  "cover_key": "covers/test_book.jpg",
  "metadata": {
    "title": "Test Book V3",
    "subtitle": "Zero-Touch Publishing Test",
    "description": "This is a test book to validate the V3 zero-touch publishing engine.",
    "author": "Igor Ganapolsky",
    "keywords": ["test", "publishing", "automation"],
    "categories": ["Business", "Technology"],
    "price": 2.99
  }
}
EOF

echo "🧪 Test payload created at: /tmp/test-payload.json"
echo "   You can test the Fargate task with:"
echo "   aws lambda invoke --function-name $FARGATE_INVOKER_ARN --payload file:///tmp/test-payload.json /tmp/response.json"