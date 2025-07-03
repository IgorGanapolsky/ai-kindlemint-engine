# FREE Email Setup with AWS - Complete Guide

## Total Cost: $0/month for your volume

## What You Need:
1. AWS Account (free tier eligible)
2. 10 minutes

## Step-by-Step Setup:

### 1. Get AWS Credentials
1. Go to https://aws.amazon.com
2. Sign in to console
3. Click your name (top right) → Security Credentials
4. Create new Access Key
5. Save the Access Key ID and Secret Access Key

### 2. Install AWS CLI (one time)
```bash
# On Mac:
brew install awscli

# Or download from: https://aws.amazon.com/cli/
```

### 3. Configure AWS
```bash
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Default region: us-east-1
# Default output: json
```

### 4. Verify Your Email in SES
```bash
# Verify your email address
aws ses verify-email-identity --email-address YOUR_EMAIL@gmail.com

# Check your email and click the verification link
```

### 5. Deploy the Email Service
```bash
cd ~/workspace/git/ai/ai-kindlemint-engine/landing-pages/sudoku-for-seniors
./deploy-email-service.sh
```

### 6. Update Your App
After deployment, you'll see:
```
endpoints:
  POST - https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/send-email
```

Add this to your `.env.local`:
```
NEXT_PUBLIC_AWS_EMAIL_ENDPOINT=https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/send-email
```

### 7. Restart Your App
```bash
npm run dev
```

## That's it! 

Your emails will now send automatically when people sign up.

## Costs:
- First 1 MILLION Lambda requests: FREE
- First 62,000 emails: FREE
- After that: $0.10 per 1,000 emails

## To Send From Your Domain (Optional):
1. Go to AWS SES → Verified Identities
2. Add your domain
3. Add the DNS records they provide
4. Update `SENDER_EMAIL` in serverless.yml