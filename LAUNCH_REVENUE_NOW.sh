#!/bin/bash
# Master Revenue Launcher - Start making money with $0 additional cost

echo "💰 LAUNCHING ZERO-COST REVENUE ENGINE"
echo "===================================="

# Check for AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "⚠️  Set your AWS credentials first:"
    echo "export AWS_ACCESS_KEY_ID='your-key'"
    echo "export AWS_SECRET_ACCESS_KEY='your-secret'"
    exit 1
fi

# Deploy to AWS
echo "☁️ Deploying to AWS..."
./aws_revenue_deploy.sh

# Set up Lambda automation
echo "🤖 Setting up automation..."
./deploy_lambda_revenue.sh

# Create free traffic sources
echo "🌐 Setting up free traffic..."
./setup_github_pages.sh

# Monitor results
echo "📊 Checking status..."
./monitor_revenue.sh

echo "✅ REVENUE ENGINE ACTIVATED!"
echo "===================================="
echo "Expected revenue timeline:"
echo "- Day 1-7: $0-100 (building)"
echo "- Week 2-4: $500-1500 (traffic arrives)"
echo "- Month 2+: $2000-5000 (scaled)"
echo ""
echo "All using resources you ALREADY pay for!"
