#!/bin/bash

# Apply ECR Lifecycle Policy for Cost Management
# This script applies a lifecycle policy to clean up old container images

set -e

# Configuration
REPOSITORY_NAME="kindlemint-v3-kdp-publisher"
POLICY_FILE="infrastructure/ecr-lifecycle-policy.json"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "🚀 Applying ECR Lifecycle Policy..."
echo "Repository: $REPOSITORY_NAME"
echo "Region: $AWS_REGION"
echo "Policy File: $POLICY_FILE"

# List existing repositories first
echo "📋 Checking existing ECR repositories..."
aws ecr describe-repositories --region "$AWS_REGION" --query 'repositories[].repositoryName' --output table 2>/dev/null || {
    echo "⚠️  Unable to list repositories. Please ensure AWS credentials are configured."
    echo "Run: aws sso login"
    exit 1
}

# Check if repository exists
if ! aws ecr describe-repositories --repository-names "$REPOSITORY_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "❌ ECR repository '$REPOSITORY_NAME' not found in region '$AWS_REGION'"
    echo ""
    echo "🔧 To create the repository, run:"
    echo "   aws ecr create-repository --repository-name $REPOSITORY_NAME --region $AWS_REGION"
    echo ""
    echo "Or use the existing deployment script:"
    echo "   ./infrastructure/deploy-v3.sh"
    exit 1
fi

# Check if policy file exists
if [ ! -f "$POLICY_FILE" ]; then
    echo "❌ Policy file '$POLICY_FILE' not found"
    exit 1
fi

# Apply lifecycle policy
echo "📋 Applying lifecycle policy to repository..."
aws ecr put-lifecycle-policy \
    --repository-name "$REPOSITORY_NAME" \
    --lifecycle-policy-text "file://$POLICY_FILE" \
    --region "$AWS_REGION"

echo "✅ ECR Lifecycle Policy applied successfully!"

# Display policy details
echo ""
echo "📊 Policy Summary:"
echo "  • Untagged images: Deleted after 1 day"
echo "  • Tagged images: Keep only last 10 versions"
echo "  • Tagged images: Deleted after 30 days"

# Get current repository usage
echo ""
echo "📈 Current Repository Status:"
IMAGE_COUNT=$(aws ecr describe-images --repository-name "$REPOSITORY_NAME" --region "$AWS_REGION" --query 'length(imageDetails)' --output text 2>/dev/null || echo "N/A")
REPO_SIZE=$(aws ecr describe-images --repository-name "$REPOSITORY_NAME" --region "$AWS_REGION" --query 'sum(imageDetails[].imageSizeInBytes)' --output text 2>/dev/null || echo "N/A")

if [ "$IMAGE_COUNT" != "N/A" ]; then
    echo "  • Total images: $IMAGE_COUNT"
fi

if [ "$REPO_SIZE" != "N/A" ] && [ "$REPO_SIZE" != "null" ]; then
    REPO_SIZE_MB=$((REPO_SIZE / 1024 / 1024))
    echo "  • Repository size: ${REPO_SIZE_MB} MB"
fi

echo ""
echo "🎯 Lifecycle policy will automatically clean up old images to stay within AWS Free Tier limits"
echo "   Free Tier: 500 MB storage per month for 12 months"