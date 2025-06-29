# 🚀 Manual AWS Infrastructure Deployment Guide

## Quick Console Deployment (5 minutes)

### Step 1: Create CloudFormation Stack

1. **Open AWS CloudFormation Console**:
   https://console.aws.amazon.com/cloudformation/home?region=us-east-1

2. **Create New Stack**:
   - Click "Create stack" → "With new resources (standard)"

3. **Upload Template**:
   - Choose "Upload a template file"
   - Select: `lambda/deployment/autonomous-orchestration-template.yaml`
   - Click "Next"

### Step 2: Configure Stack Parameters

**Stack Name**: `kindlemint-autonomous-orchestration`

**Parameters**:
- **Environment**: `production`
- **GitHubToken**: [Create at https://github.com/settings/tokens]
  - Required scopes: `repo`, `workflow`, `actions:read`
- **SlackWebhookURL**: [Create at https://api.slack.com/messaging/webhooks]
- **SentryDSN**: (Optional - leave blank if not using)
- **SentryAuthToken**: (Optional - leave blank if not using)

### Step 3: Deploy Stack

1. **Configure Stack Options**: (Keep defaults)
2. **Review**: Check "I acknowledge that AWS CloudFormation might create IAM resources"
3. **Create Stack**: Click "Create stack"

**⏱️ Deployment Time**: 3-5 minutes

### Step 4: Verify Deployment

**Check Stack Status**:
- Status should show `CREATE_COMPLETE`
- Click "Outputs" tab to see:
  - Lambda Function ARNs
  - DynamoDB Table Names
  - API Gateway URL

**Test Lambda Functions**:
```bash
# In CloudFormation outputs, find the function names
# Go to Lambda Console and test the functions
```

## 🔍 Post-Deployment Verification

### Update Status Badges
```bash
python3 scripts/aws_status_checker.py
```

### Test Infrastructure
1. **Lambda Functions**: Visit AWS Lambda Console
2. **DynamoDB Tables**: Check `kindlemint-config` and `kindlemint-orchestration-logs`
3. **CloudWatch**: Verify scheduled events are working

## 💰 Cost Monitoring

**Expected Monthly Cost**: $5-15
**Cost Savings vs GitHub Actions**: 96% reduction ($1,597/year saved)

## 🛠️ Troubleshooting

**If deployment fails**:
1. Check IAM permissions
2. Verify template syntax
3. Check CloudFormation events tab for errors

**If Lambda functions fail**:
1. Check environment variables
2. Verify DynamoDB permissions
3. Check CloudWatch logs

## 🎯 Next Steps

1. **Commit Changes**: 
   ```bash
   git add .
   git commit -m "Deploy AWS infrastructure with status monitoring"
   git push
   ```

2. **Monitor Operations**:
   - CloudWatch Dashboard
   - Slack notifications
   - GitHub status badges

## 📞 Support

If you encounter issues:
1. Check CloudFormation Events tab
2. Review Lambda CloudWatch logs
3. Verify all parameters are correct

---

**🎉 Success Indicators**:
- ✅ Stack Status: `CREATE_COMPLETE`
- ✅ Lambda Functions: 2 functions deployed
- ✅ DynamoDB: 2 tables created
- ✅ Status Badges: Updated and working