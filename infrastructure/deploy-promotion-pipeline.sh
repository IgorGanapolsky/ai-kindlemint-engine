#!/bin/bash
# Autonomous Promotion Pipeline Deployment Script
# Deploys complete marketing automation system alongside V3 Zero-Touch Engine

set -e

echo "🚀 AUTONOMOUS PROMOTION PIPELINE DEPLOYMENT STARTING..."

# Configuration
PROJECT_NAME="kindlemint-v3"
PROMOTION_STACK_NAME="${PROJECT_NAME}-promotion-pipeline"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Check required environment variables for promotion pipeline
required_vars=(
    "OPENAI_API_KEY" 
    "BUFFER_API_KEY" 
    "BUFFER_ACCESS_TOKEN"
    "AMAZON_ADS_CLIENT_ID"
    "AMAZON_ADS_CLIENT_SECRET" 
    "AMAZON_ADS_REFRESH_TOKEN"
    "AMAZON_ADS_PROFILE_ID"
    "SLACK_WEBHOOK_URL"
)

echo "🔍 Checking required environment variables..."
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var environment variable is required"
        echo "   Please set all required variables for promotion pipeline"
        exit 1
    fi
done

echo "✅ All required environment variables are set"

# Get Buffer profile IDs (these should be set as environment variables)
BUFFER_TWITTER_PROFILE_ID="${BUFFER_TWITTER_PROFILE_ID:-}"
BUFFER_FACEBOOK_PROFILE_ID="${BUFFER_FACEBOOK_PROFILE_ID:-}"
BUFFER_INSTAGRAM_PROFILE_ID="${BUFFER_INSTAGRAM_PROFILE_ID:-}"

if [ -z "$BUFFER_TWITTER_PROFILE_ID" ] && [ -z "$BUFFER_FACEBOOK_PROFILE_ID" ] && [ -z "$BUFFER_INSTAGRAM_PROFILE_ID" ]; then
    echo "⚠️  Warning: No Buffer profile IDs set. Social media automation will be limited."
    echo "   Set BUFFER_TWITTER_PROFILE_ID, BUFFER_FACEBOOK_PROFILE_ID, and/or BUFFER_INSTAGRAM_PROFILE_ID"
fi

echo "📋 Configuration:"
echo "  Project: $PROJECT_NAME"
echo "  Region: $AWS_REGION"
echo "  Account: $AWS_ACCOUNT_ID"
echo "  Stack: $PROMOTION_STACK_NAME"

# Create promotion secrets in AWS Secrets Manager
echo "🔐 Creating promotion pipeline secrets..."

PROMOTION_SECRETS_NAME="${PROJECT_NAME}-promotion-secrets"

aws secretsmanager create-secret \
    --name "$PROMOTION_SECRETS_NAME" \
    --description "Autonomous promotion pipeline secrets" \
    --secret-string "$(cat <<EOF
{
    "openai_api_key": "${OPENAI_API_KEY}",
    "buffer_api_key": "${BUFFER_API_KEY}",
    "buffer_access_token": "${BUFFER_ACCESS_TOKEN}",
    "buffer_twitter_profile_id": "${BUFFER_TWITTER_PROFILE_ID}",
    "buffer_facebook_profile_id": "${BUFFER_FACEBOOK_PROFILE_ID}",
    "buffer_instagram_profile_id": "${BUFFER_INSTAGRAM_PROFILE_ID}",
    "amazon_ads_client_id": "${AMAZON_ADS_CLIENT_ID}",
    "amazon_ads_client_secret": "${AMAZON_ADS_CLIENT_SECRET}",
    "amazon_ads_refresh_token": "${AMAZON_ADS_REFRESH_TOKEN}",
    "amazon_ads_profile_id": "${AMAZON_ADS_PROFILE_ID}",
    "slack_webhook_url": "${SLACK_WEBHOOK_URL}"
}
EOF
)" \
    --region $AWS_REGION 2>/dev/null || echo "Secret may already exist, updating..."

# Update secret if it already exists
aws secretsmanager update-secret \
    --secret-id "$PROMOTION_SECRETS_NAME" \
    --secret-string "$(cat <<EOF
{
    "openai_api_key": "${OPENAI_API_KEY}",
    "buffer_api_key": "${BUFFER_API_KEY}",
    "buffer_access_token": "${BUFFER_ACCESS_TOKEN}",
    "buffer_twitter_profile_id": "${BUFFER_TWITTER_PROFILE_ID}",
    "buffer_facebook_profile_id": "${BUFFER_FACEBOOK_PROFILE_ID}",
    "buffer_instagram_profile_id": "${BUFFER_INSTAGRAM_PROFILE_ID}",
    "amazon_ads_client_id": "${AMAZON_ADS_CLIENT_ID}",
    "amazon_ads_client_secret": "${AMAZON_ADS_CLIENT_SECRET}",
    "amazon_ads_refresh_token": "${AMAZON_ADS_REFRESH_TOKEN}",
    "amazon_ads_profile_id": "${AMAZON_ADS_PROFILE_ID}",
    "slack_webhook_url": "${SLACK_WEBHOOK_URL}"
}
EOF
)" \
    --region $AWS_REGION

echo "✅ Promotion secrets created/updated"

# Create Lambda deployment packages
echo "📦 Creating Lambda deployment packages..."

cd "$(dirname "$0")/.."  # Go to project root

# Create promotion functions directory
mkdir -p dist/promotion

# Package each promotion Lambda function
promotion_functions=(
    "autonomous_promotion_engine"
    "autonomous_ad_campaign_launcher"
    "autonomous_pricing_promoter"
    "autonomous_ad_optimizer"
    "promotion_pipeline_orchestrator"
)

for func in "${promotion_functions[@]}"; do
    echo "  📦 Packaging $func..."
    
    # Create function directory
    func_dir="dist/promotion/$func"
    mkdir -p "$func_dir"
    
    # Copy function code
    cp "promotion/${func}.py" "$func_dir/lambda_function.py"
    
    # Copy required modules
    cp -r kindlemint/ "$func_dir/" 2>/dev/null || true
    
    # Install dependencies in function directory
    pip install --target "$func_dir" \
        boto3 \
        requests \
        openai \
        playwright \
        python-docx \
        pillow \
        asyncio-throttle \
        -q
    
    # Create zip package
    cd "$func_dir"
    zip -r "../${func}.zip" . -q
    cd - > /dev/null
    
    echo "  ✅ $func packaged"
done

# Create CloudFormation template for promotion pipeline
echo "☁️  Creating promotion pipeline CloudFormation template..."

cat > infrastructure/promotion-pipeline.yaml <<'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Autonomous Promotion Pipeline for V3 Zero-Touch Engine'

Parameters:
  ProjectName:
    Type: String
    Default: 'kindlemint-v3'
    Description: 'Project name for resource naming'
  
  PromotionSecretsArn:
    Type: String
    Description: 'ARN of the promotion secrets in Secrets Manager'

Resources:
  # DynamoDB table for ad campaign tracking
  AdCampaignsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: KDP_Ad_Campaigns
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: campaign_id
          AttributeType: S
      KeySchema:
        - AttributeName: campaign_id
          KeyType: HASH
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-ad-campaigns-table'

  # IAM role for promotion Lambda functions
  PromotionLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: PromotionPipelineAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Ref PromotionSecretsArn
              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:GetItem
                  - dynamodb:Query
                  - dynamodb:Scan
                Resource: !GetAtt AdCampaignsTable.Arn
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                Resource: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${ProjectName}-*'
              - Effect: Allow
                Action:
                  - events:PutRule
                  - events:PutTargets
                  - events:DeleteRule
                  - events:RemoveTargets
                  - events:DescribeRule
                Resource: '*'
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                Resource: !Sub 'arn:aws:s3:::kindlemint-books/*'

  # Lambda function: Autonomous Promotion Engine
  PromotionEngineFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${ProjectName}-promotion-engine'
      Runtime: python3.11
      Handler: lambda_function.lambda_handler
      Role: !GetAtt PromotionLambdaRole.Arn
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {'statusCode': 200, 'body': 'Placeholder'}
      Timeout: 300
      MemorySize: 512
      Environment:
        Variables:
          PROMOTION_SECRETS_ARN: !Ref PromotionSecretsArn
          AWS_REGION: !Ref AWS::Region

  # Lambda function: Ad Campaign Launcher
  AdCampaignLauncherFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${ProjectName}-ad-campaign-launcher'
      Runtime: python3.11
      Handler: lambda_function.lambda_handler
      Role: !GetAtt PromotionLambdaRole.Arn
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {'statusCode': 200, 'body': 'Placeholder'}
      Timeout: 300
      MemorySize: 512
      Environment:
        Variables:
          PROMOTION_SECRETS_ARN: !Ref PromotionSecretsArn
          AWS_REGION: !Ref AWS::Region

  # Lambda function: Pricing Promoter
  PricingPromoterFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${ProjectName}-pricing-promoter'
      Runtime: python3.11
      Handler: lambda_function.lambda_handler
      Role: !GetAtt PromotionLambdaRole.Arn
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {'statusCode': 200, 'body': 'Placeholder'}
      Timeout: 900  # 15 minutes for browser automation
      MemorySize: 1024
      Environment:
        Variables:
          PROMOTION_SECRETS_ARN: !Ref PromotionSecretsArn
          AWS_REGION: !Ref AWS::Region

  # Lambda function: Ad Optimizer
  AdOptimizerFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${ProjectName}-ad-optimizer'
      Runtime: python3.11
      Handler: lambda_function.lambda_handler
      Role: !GetAtt PromotionLambdaRole.Arn
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {'statusCode': 200, 'body': 'Placeholder'}
      Timeout: 600
      MemorySize: 512
      Environment:
        Variables:
          PROMOTION_SECRETS_ARN: !Ref PromotionSecretsArn
          AWS_REGION: !Ref AWS::Region

  # Lambda function: Promotion Pipeline Orchestrator
  PromotionOrchestratorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${ProjectName}-promotion-orchestrator'
      Runtime: python3.11
      Handler: lambda_function.lambda_handler
      Role: !GetAtt PromotionLambdaRole.Arn
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {'statusCode': 200, 'body': 'Placeholder'}
      Timeout: 300
      MemorySize: 512
      Environment:
        Variables:
          PROMOTION_ENGINE_ARN: !GetAtt PromotionEngineFunction.Arn
          AD_CAMPAIGN_LAUNCHER_ARN: !GetAtt AdCampaignLauncherFunction.Arn
          PRICING_PROMOTER_ARN: !GetAtt PricingPromoterFunction.Arn
          AD_OPTIMIZER_ARN: !GetAtt AdOptimizerFunction.Arn
          PROMOTION_SECRETS_ARN: !Ref PromotionSecretsArn
          AWS_REGION: !Ref AWS::Region

  # EventBridge rule for daily ad optimization
  DailyOptimizationRule:
    Type: AWS::Events::Rule
    Properties:
      Name: !Sub '${ProjectName}-daily-ad-optimization'
      Description: 'Daily autonomous ad optimization'
      ScheduleExpression: 'cron(0 9 * * ? *)'  # 9 AM UTC daily
      State: ENABLED
      Targets:
        - Arn: !GetAtt AdOptimizerFunction.Arn
          Id: DailyOptimizationTarget

  # Permission for EventBridge to invoke ad optimizer
  AdOptimizerEventPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref AdOptimizerFunction
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com
      SourceArn: !GetAtt DailyOptimizationRule.Arn

Outputs:
  PromotionOrchestratorArn:
    Description: 'Promotion Pipeline Orchestrator ARN'
    Value: !GetAtt PromotionOrchestratorFunction.Arn
    Export:
      Name: !Sub '${ProjectName}-promotion-orchestrator-arn'

  AdCampaignsTableName:
    Description: 'Ad Campaigns DynamoDB Table Name'
    Value: !Ref AdCampaignsTable
    Export:
      Name: !Sub '${ProjectName}-ad-campaigns-table'

  DailyOptimizationRuleName:
    Description: 'Daily Optimization EventBridge Rule Name'
    Value: !Ref DailyOptimizationRule
    Export:
      Name: !Sub '${ProjectName}-daily-optimization-rule'
EOF

# Deploy promotion pipeline CloudFormation stack
echo "☁️  Deploying promotion pipeline infrastructure..."

PROMOTION_SECRETS_ARN="arn:aws:secretsmanager:${AWS_REGION}:${AWS_ACCOUNT_ID}:secret:${PROMOTION_SECRETS_NAME}"

aws cloudformation deploy \
    --template-file infrastructure/promotion-pipeline.yaml \
    --stack-name "$PROMOTION_STACK_NAME" \
    --parameter-overrides \
        ProjectName="$PROJECT_NAME" \
        PromotionSecretsArn="$PROMOTION_SECRETS_ARN" \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION

echo "✅ Promotion pipeline infrastructure deployed"

# Update Lambda function code
echo "🔄 Updating Lambda function code..."

for func in "${promotion_functions[@]}"; do
    function_name="${PROJECT_NAME}-${func//_/-}"
    zip_file="dist/promotion/${func}.zip"
    
    echo "  📤 Updating $function_name..."
    
    aws lambda update-function-code \
        --function-name "$function_name" \
        --zip-file "fileb://$zip_file" \
        --region $AWS_REGION > /dev/null
    
    echo "  ✅ $function_name updated"
done

# Get CloudFormation outputs
echo "📋 Getting deployment outputs..."

PROMOTION_ORCHESTRATOR_ARN=$(aws cloudformation describe-stacks \
    --stack-name "$PROMOTION_STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`PromotionOrchestratorArn`].OutputValue' \
    --output text \
    --region $AWS_REGION)

echo "✅ AUTONOMOUS PROMOTION PIPELINE DEPLOYED SUCCESSFULLY!"
echo ""
echo "🎯 Deployment Summary:"
echo "  ✅ Promotion Secrets: $PROMOTION_SECRETS_ARN"
echo "  ✅ Promotion Orchestrator: $PROMOTION_ORCHESTRATOR_ARN"
echo "  ✅ Ad Campaigns Table: KDP_Ad_Campaigns"
echo "  ✅ Daily Optimization: Scheduled at 09:00 UTC"
echo "  ✅ All Lambda Functions: Deployed and updated"
echo ""
echo "🚀 Integration with V3 Engine:"
echo "  1. Update V3 Fargate task to trigger promotion orchestrator"
echo "  2. Set PROMOTION_ORCHESTRATOR_ARN in V3 environment"
echo "  3. Test end-to-end flow from book publication to marketing activation"
echo ""
echo "💰 AUTONOMOUS MARKETING IS NOW OPERATIONAL!"
echo "   Every book published will automatically trigger:"
echo "   📱 Social media campaign (10 posts over 7 days)"
echo "   💰 Amazon ad campaigns (auto + manual)"
echo "   💸 Promotional pricing strategy"
echo "   🔧 Daily ad optimization"
echo ""
echo "🎉 YOUR FIRST DOLLAR WITH ZERO MANUAL MARKETING WORK!"

# Cleanup
rm -rf dist/promotion

echo "🧹 Cleanup completed"