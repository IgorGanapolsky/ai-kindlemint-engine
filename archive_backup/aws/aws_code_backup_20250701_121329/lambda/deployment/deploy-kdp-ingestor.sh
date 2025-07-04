#!/bin/bash

# KDP Report Ingestor Deployment Script
# Memory-Driven Publishing Engine V2.0

set -e

# Configuration
STACK_NAME="kindlemint-kdp-ingestor"
REGION="us-east-2"
PROFILE="kindlemint-keys"
LAMBDA_FUNCTION_NAME="KDP-Report-Ingestor"

echo "=========================================="
echo "KDP Report Ingestor Deployment"
echo "Memory-Driven Publishing Engine V2.0"
echo "=========================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity --profile $PROFILE >/dev/null 2>&1; then
    echo "ERROR: AWS CLI not configured for profile $PROFILE"
    echo "Please run: aws configure --profile $PROFILE"
    exit 1
fi

echo "✓ AWS CLI configured for profile: $PROFILE"

# Create deployment package
echo "📦 Creating Lambda deployment package..."
cd "$(dirname "$0")/.."

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
cp kdp_report_ingestor.py $TEMP_DIR/
cd $TEMP_DIR

# Install dependencies if requirements.txt exists
if [ -f "../requirements.txt" ]; then
    echo "📥 Installing Python dependencies..."
    pip install -r ../requirements.txt -t .
fi

# Create deployment zip
zip -r kdp-ingestor-deployment.zip .
DEPLOYMENT_PACKAGE="$TEMP_DIR/kdp-ingestor-deployment.zip"

echo "✓ Deployment package created: $DEPLOYMENT_PACKAGE"

# Go back to deployment directory
cd - >/dev/null

# Check if DynamoDB table exists
echo "🔍 Checking DynamoDB table..."
if aws dynamodb describe-table --table-name KDP_Business_Memory --region $REGION --profile $PROFILE >/dev/null 2>&1; then
    echo "✓ DynamoDB table KDP_Business_Memory exists"
else
    echo "❌ DynamoDB table KDP_Business_Memory does not exist"
    echo "Please create the table first using the memory system setup"
    exit 1
fi

# Deploy CloudFormation stack
echo "🚀 Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file deployment/kdp-ingestor-template.yaml \
    --stack-name $STACK_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION \
    --profile $PROFILE \
    --parameter-overrides \
        DynamoDBTableName=KDP_Business_Memory \
        S3BucketName=kindlemint-reports-$(date +%s) \
        ScheduleExpression="rate(7 days)"

if [ $? -eq 0 ]; then
    echo "✓ CloudFormation stack deployed successfully"
else
    echo "❌ CloudFormation deployment failed"
    exit 1
fi

# Update Lambda function code
echo "📝 Updating Lambda function code..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://$DEPLOYMENT_PACKAGE \
    --region $REGION \
    --profile $PROFILE

if [ $? -eq 0 ]; then
    echo "✓ Lambda function code updated successfully"
else
    echo "❌ Lambda function code update failed"
    exit 1
fi

# Get stack outputs
echo "📋 Getting deployment information..."
S3_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --profile $PROFILE \
    --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
    --output text)

LAMBDA_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --profile $PROFILE \
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionArn`].OutputValue' \
    --output text)

# Test the Lambda function
echo "🧪 Testing Lambda function..."
TEST_EVENT='{
    "csv_content": "Title,ASIN,Units Sold,Pages Read,Royalties\\nTest Book,B123456789,5,250,12.50",
    "report_date": "'$(date +%Y-%m-%d)'"
}'

aws lambda invoke \
    --function-name $LAMBDA_FUNCTION_NAME \
    --region $REGION \
    --profile $PROFILE \
    --payload "$TEST_EVENT" \
    response.json

if [ $? -eq 0 ]; then
    echo "✓ Lambda function test completed"
    echo "Response:"
    cat response.json | jq .
    rm response.json
else
    echo "❌ Lambda function test failed"
fi

# Cleanup
rm -rf $TEMP_DIR

echo ""
echo "=========================================="
echo "🎯 DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "📊 KDP Report Ingestor Details:"
echo "   Lambda Function: $LAMBDA_FUNCTION_NAME"
echo "   Lambda ARN: $LAMBDA_ARN"
echo "   S3 Bucket: $S3_BUCKET"
echo "   Schedule: Every 7 days (automatic)"
echo ""
echo "📝 Next Steps:"
echo "   1. Upload KDP CSV reports to S3 bucket: $S3_BUCKET"
echo "   2. Reports will be automatically processed"
echo "   3. Check DynamoDB table for updated ROI data"
echo "   4. Use memory-driven pipeline for intelligent topic generation"
echo ""
echo "🧠 The learning loop is now ACTIVE!"
echo "Your system will automatically learn from real sales data."
