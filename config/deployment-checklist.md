# V3 Zero-Touch Engine + Autonomous Promotion Pipeline
## Complete Deployment Checklist

### 🚀 PRE-DEPLOYMENT SETUP

#### 1. AWS Account Preparation
- [ ] AWS CLI configured with admin permissions
- [ ] Default region set to `us-east-1` (recommended)
- [ ] AWS account has sufficient limits for:
  - Lambda functions (10+)
  - Fargate tasks (5+)
  - DynamoDB tables (5+)
  - Secrets Manager secrets (5+)

#### 2. Required API Keys & Credentials

**📚 V3 Publishing Engine:**
- [ ] OpenAI API key with GPT-4 access
- [ ] KDP account email and password
- [ ] Slack webhook URL for notifications

**📱 Promotion Pipeline:**
- [ ] Buffer API key and access token
- [ ] Buffer profile IDs (Twitter, Facebook, Instagram)
- [ ] Amazon Advertising API credentials:
  - [ ] Client ID
  - [ ] Client Secret  
  - [ ] Refresh Token
  - [ ] Profile ID

#### 3. External Service Setup

**Buffer Social Media:**
1. Create Buffer account at buffer.com
2. Connect social media profiles
3. Generate API key in Buffer dashboard
4. Get profile IDs from Buffer API

**Amazon Advertising:**
1. Register for Amazon Advertising API access
2. Complete API application process (can take 1-2 weeks)
3. Generate client credentials
4. Obtain refresh token via OAuth flow

### 🏗️ DEPLOYMENT SEQUENCE

#### Step 1: Deploy V3 Zero-Touch Publishing Engine
```bash
# Set environment variables
export KDP_EMAIL="your-kdp-email@example.com"
export KDP_PASSWORD="your-kdp-password"
export OPENAI_API_KEY="sk-your-openai-api-key"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK"

# Deploy V3 engine
cd infrastructure
chmod +x deploy-v3.sh
./deploy-v3.sh
```

**Expected Outputs:**
- [ ] ECR repository created
- [ ] Docker image built and pushed
- [ ] ECS cluster operational
- [ ] Lambda orchestration functions deployed
- [ ] Fargate task definition created
- [ ] Secrets Manager configured

#### Step 2: Deploy Autonomous Promotion Pipeline
```bash
# Set promotion pipeline environment variables
export BUFFER_API_KEY="your-buffer-api-key"
export BUFFER_ACCESS_TOKEN="your-buffer-access-token"
export BUFFER_TWITTER_PROFILE_ID="your-twitter-profile-id"
export BUFFER_FACEBOOK_PROFILE_ID="your-facebook-profile-id"
export BUFFER_INSTAGRAM_PROFILE_ID="your-instagram-profile-id"
export AMAZON_ADS_CLIENT_ID="amzn1.application-oa2-client.your-id"
export AMAZON_ADS_CLIENT_SECRET="your-client-secret"
export AMAZON_ADS_REFRESH_TOKEN="Atzr|your-refresh-token"
export AMAZON_ADS_PROFILE_ID="your-profile-id"

# Deploy promotion pipeline
chmod +x deploy-promotion-pipeline.sh
./deploy-promotion-pipeline.sh
```

**Expected Outputs:**
- [ ] Promotion Lambda functions deployed
- [ ] DynamoDB tables created
- [ ] EventBridge rules configured
- [ ] Secrets Manager updated
- [ ] Daily optimization scheduled

### ✅ POST-DEPLOYMENT VALIDATION

#### 1. V3 Engine Health Check
```bash
# Test V3 orchestration
aws lambda invoke \
  --function-name kindlemint-v3-orchestrator \
  --payload '{"topic": "Test Book", "source": "manual"}' \
  response.json

# Check response
cat response.json
```

#### 2. Promotion Pipeline Health Check
```bash
# Test promotion orchestrator
aws lambda invoke \
  --function-name kindlemint-v3-promotion-orchestrator \
  --payload '{"asin": "TEST123", "title": "Test Book"}' \
  promo-response.json

# Check response
cat promo-response.json
```

#### 3. End-to-End Integration Test
- [ ] Trigger V3 pipeline manually
- [ ] Verify book generation completes
- [ ] Confirm promotion pipeline activates
- [ ] Check Slack notifications received
- [ ] Validate DynamoDB records created

### 🔧 OPERATIONAL VERIFICATION

#### Daily Automation Check
- [ ] EventBridge rules active
- [ ] Scheduled triggers configured
- [ ] Slack channels receiving notifications
- [ ] DynamoDB memory system updating

#### Performance Monitoring
- [ ] CloudWatch dashboards created
- [ ] Lambda function metrics available
- [ ] Fargate task monitoring active
- [ ] Cost tracking configured

### 🚨 TROUBLESHOOTING COMMON ISSUES

#### V3 Engine Issues:
- **Docker build fails**: Check available disk space and Docker daemon
- **Fargate task crashes**: Review CloudWatch logs for browser automation errors  
- **KDP login fails**: Verify credentials in Secrets Manager

#### Promotion Pipeline Issues:
- **Buffer API errors**: Check rate limits and profile ID validity
- **Amazon Ads API fails**: Verify API approval status and credentials
- **Social media posts not scheduling**: Check Buffer profile connections

#### Integration Issues:
- **Promotion not triggering**: Verify Lambda ARN environment variables
- **Missing Slack notifications**: Check webhook URL and permissions
- **DynamoDB access denied**: Review IAM role permissions

### 📊 SUCCESS METRICS

**System is operational when:**
- [ ] Books publish to KDP automatically
- [ ] Social media posts schedule automatically  
- [ ] Amazon ad campaigns create automatically
- [ ] Promotional pricing sets automatically
- [ ] Daily optimization runs automatically
- [ ] Slack notifications work for all events

### 🎯 FIRST DOLLAR MILESTONE

**Your autonomous revenue engine is ready when:**
1. ✅ V3 engine publishes books to KDP
2. ✅ Promotion pipeline activates marketing
3. ✅ All automation runs without manual intervention
4. ✅ Performance monitoring shows system health
5. ✅ First book sales appear in KDP dashboard

**🎉 CONGRATULATIONS! Your industrial automation is now generating passive income!**