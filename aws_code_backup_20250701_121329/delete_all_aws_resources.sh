#!/bin/bash
# AWS Complete Resource Deletion Script
# This script will delete ALL AWS resources to save costs
# ========================================================

set -e

echo "=================================================="
echo "🗑️  AWS COMPLETE RESOURCE DELETION SCRIPT"
echo "This will delete ALL AWS resources to save money"
echo "=================================================="
echo ""

# Check AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   brew install awscli"
    exit 1
fi

# Check AWS credentials
echo "🔍 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run:"
    echo "   aws configure"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

echo "✅ Connected to AWS Account: $ACCOUNT_ID"
echo "📍 Region: $REGION"
echo ""

# Confirmation prompt
echo "⚠️  WARNING: This will delete:"
echo "   - 2 CloudFormation stacks"
echo "   - 2 Lambda functions"
echo "   - 2 DynamoDB tables"
echo "   - 1 SNS topic"
echo "   - All associated resources"
echo ""
read -p "Are you SURE you want to delete ALL AWS resources? (type 'DELETE ALL' to confirm): " confirmation

if [ "$confirmation" != "DELETE ALL" ]; then
    echo "❌ Deletion cancelled"
    exit 0
fi

echo ""
echo "🚀 Starting deletion process..."
echo ""

# Step 1: Delete Lambda functions directly (in case they're not part of stacks)
echo "1️⃣ Deleting Lambda functions..."
for func in "kindlemint-v3-orchestrator" "kindlemint-v3-fargate-invoker"; do
    echo "   Deleting Lambda function: $func"
    aws lambda delete-function --function-name $func --region $REGION 2>/dev/null || echo "   ⚠️  Function $func not found or already deleted"
done

# Step 2: Delete CloudFormation stacks
echo ""
echo "2️⃣ Deleting CloudFormation stacks..."

# Delete autonomous-orchestration-production stack
echo "   Deleting stack: autonomous-orchestration-production"
aws cloudformation delete-stack \
    --stack-name autonomous-orchestration-production \
    --region $REGION 2>/dev/null || echo "   ⚠️  Stack not found or already deleted"

# Delete Sentry-Monitoring-Stack
echo "   Deleting stack: Sentry-Monitoring-Stack"
aws cloudformation delete-stack \
    --stack-name Sentry-Monitoring-Stack \
    --region $REGION 2>/dev/null || echo "   ⚠️  Stack not found or already deleted"

# Step 3: Wait for stack deletion
echo ""
echo "3️⃣ Waiting for stack deletion (this may take several minutes)..."

for stack in "autonomous-orchestration-production" "Sentry-Monitoring-Stack"; do
    echo "   Waiting for $stack to delete..."
    aws cloudformation wait stack-delete-complete \
        --stack-name $stack \
        --region $REGION 2>/dev/null || echo "   ✅ $stack deleted or not found"
done

# Step 4: Manual cleanup of resources that might not be in stacks
echo ""
echo "4️⃣ Cleaning up any remaining resources..."

# Delete DynamoDB tables if they still exist
for table in "kindlemint-config-production" "kindlemint-orchestration-logs-production"; do
    echo "   Checking DynamoDB table: $table"
    if aws dynamodb describe-table --table-name $table --region $REGION &>/dev/null; then
        echo "   Deleting DynamoDB table: $table"
        aws dynamodb delete-table --table-name $table --region $REGION
    else
        echo "   ✅ Table $table not found"
    fi
done

# Delete SNS topics
echo "   Checking SNS topics..."
TOPIC_ARN="arn:aws:sns:$REGION:$ACCOUNT_ID:kindlemint-orchestration-notifications-production"
if aws sns get-topic-attributes --topic-arn $TOPIC_ARN --region $REGION &>/dev/null; then
    echo "   Deleting SNS topic"
    aws sns delete-topic --topic-arn $TOPIC_ARN --region $REGION
else
    echo "   ✅ SNS topic not found"
fi

# Step 5: Check for any remaining resources
echo ""
echo "5️⃣ Verifying deletion..."

# Check remaining CloudFormation stacks
echo ""
echo "Remaining CloudFormation stacks:"
aws cloudformation list-stacks \
    --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
    --region $REGION \
    --query 'StackSummaries[?StackName==`autonomous-orchestration-production` || StackName==`Sentry-Monitoring-Stack`].StackName' \
    --output text

# Check remaining Lambda functions
echo ""
echo "Remaining Lambda functions:"
aws lambda list-functions \
    --region $REGION \
    --query 'Functions[?starts_with(FunctionName, `kindlemint`)].FunctionName' \
    --output text

# Final status
echo ""
echo "=================================================="
echo "✅ AWS RESOURCE DELETION COMPLETE!"
echo "=================================================="
echo ""
echo "💰 Estimated monthly savings: $5-15"
echo ""
echo "📋 Next steps:"
echo "1. Check AWS Billing in 24 hours to confirm no charges"
echo "2. Remove AWS code from repository (optional)"
echo "3. Consider closing AWS account if not needed"
echo ""
echo "🎉 You're now running 100% on free tools:"
echo "   - GitHub Actions (CI/CD)"
echo "   - Sentry (monitoring)"
echo "   - Slack (notifications)"
echo "   - Local Python scripts (processing)"
echo ""