#!/bin/bash
# IMMEDIATE DEPLOYMENT SCRIPT
# Uses your existing credentials to deploy V3 Zero-Touch Engine RIGHT NOW

set -e

echo "🚀 DEPLOYING V3 ZERO-TOUCH ENGINE WITH YOUR CREDENTIALS"

# Set your actual credentials here before running
export OPENAI_API_KEY="${OPENAI_API_KEY:-YOUR-OPENAI-API-KEY}"
export KDP_EMAIL="${KDP_EMAIL:-YOUR-KDP-EMAIL}"
export KDP_PASSWORD="${KDP_PASSWORD:-YOUR-KDP-PASSWORD}"

# YOU NEED TO SET YOUR SLACK WEBHOOK URL
if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "⚠️  SLACK_WEBHOOK_URL not set!"
    echo "   Get it from: https://api.slack.com/messaging/webhooks"
    echo "   Then run: export SLACK_WEBHOOK_URL='your-webhook-url'"
    echo "   And run this script again"
    exit 1
fi

echo "✅ Using OpenAI API key: ${OPENAI_API_KEY:0:20}..."
echo "✅ Using KDP email: $KDP_EMAIL"
echo "✅ Using Slack webhook: ${SLACK_WEBHOOK_URL:0:50}..."

# Deploy V3 Zero-Touch Engine
echo "🚀 Deploying V3 Zero-Touch Publishing Engine..."
cd infrastructure
chmod +x deploy-v3.sh
./deploy-v3.sh

echo ""
echo "🎉 V3 ZERO-TOUCH ENGINE DEPLOYMENT COMPLETE!"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Test the system: Run a manual book generation"
echo "2. Set up Slack webhook if you haven't already"  
echo "3. Get Buffer and Amazon Ads credentials for promotion pipeline"
echo "4. Deploy promotion pipeline: ./infrastructure/deploy-promotion-pipeline.sh"
echo ""
echo "💰 YOUR AUTONOMOUS PUBLISHING ENGINE IS NOW LIVE!"