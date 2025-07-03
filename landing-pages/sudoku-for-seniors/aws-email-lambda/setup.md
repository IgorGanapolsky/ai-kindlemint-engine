# AWS Email Setup - 10 Minutes

## Step 1: Install Serverless Framework
```bash
npm install -g serverless
```

## Step 2: Configure AWS Credentials
```bash
serverless config credentials --provider aws --key YOUR_ACCESS_KEY --secret YOUR_SECRET_KEY
```

## Step 3: Verify Email in AWS SES
1. Go to AWS Console > SES > Verified Identities
2. Click "Create Identity"
3. Add your email address (for testing)
4. Check your email and click verification link

## Step 4: Deploy
```bash
cd aws-email-lambda
npm init -y
npm install aws-sdk
serverless deploy
```

## Step 5: Copy the API Endpoint
After deploy, you'll see:
```
endpoints:
  POST - https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/send-email
```

Copy this URL - we'll use it in the app.

## Total Monthly Cost: $0
- First 1M Lambda requests: FREE
- First 62,000 emails/month: FREE
- After that: $0.10 per 1,000 emails