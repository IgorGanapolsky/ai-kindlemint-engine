#!/bin/bash
# AWS Setup for V3 Deployment

echo "🔧 AWS SETUP FOR V3 DEPLOYMENT"
echo ""
echo "You need to configure AWS CLI with your credentials."
echo ""
echo "Choose your setup method:"
echo ""
echo "1. AWS SSO (if you have SSO setup)"
echo "2. AWS Access Keys (recommended for personal accounts)"
echo "3. AWS Profile (if you already have profiles)"
echo ""
read -p "Enter your choice (1, 2, or 3): " choice

case $choice in
    1)
        echo "🔐 Setting up AWS SSO..."
        aws sso login
        ;;
    2)
        echo "🔑 Setting up AWS Access Keys..."
        echo ""
        echo "You'll need:"
        echo "- AWS Access Key ID"
        echo "- AWS Secret Access Key"
        echo "- Default region (recommend: us-east-1)"
        echo ""
        aws configure
        ;;
    3)
        echo "📋 Available AWS profiles:"
        aws configure list-profiles
        echo ""
        read -p "Enter profile name to use: " profile_name
        export AWS_PROFILE=$profile_name
        echo "Using profile: $profile_name"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🧪 Testing AWS connection..."
aws sts get-caller-identity

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ AWS connection successful!"
    echo ""
    echo "🚀 Ready to deploy V3 Zero-Touch Engine!"
    echo ""
    echo "Run this command to deploy:"
    echo "cd infrastructure && ./deploy-v3.sh"
else
    echo ""
    echo "❌ AWS connection failed. Please check your credentials."
fi