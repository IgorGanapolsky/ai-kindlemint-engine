#!/bin/bash

echo "🚀 Deploying AWS Email Service..."

# Check if serverless is installed
if ! command -v serverless &> /dev/null
then
    echo "Installing Serverless Framework..."
    npm install -g serverless
fi

# Navigate to lambda directory
cd aws-email-lambda

# Initialize npm if needed
if [ ! -f "package.json" ]; then
    npm init -y
    npm install aws-sdk
fi

# Deploy to AWS
echo "Deploying to AWS Lambda..."
serverless deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Copy the API endpoint URL from above"
echo "2. Add it to .env.local as NEXT_PUBLIC_AWS_EMAIL_ENDPOINT"
echo "3. Verify your email in AWS SES console"
echo "4. Restart the Next.js server"