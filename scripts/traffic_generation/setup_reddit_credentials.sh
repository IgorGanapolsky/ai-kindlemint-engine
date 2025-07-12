#!/bin/bash
# Secure Reddit Credentials Setup
# Run this script to set up your Reddit API credentials securely

echo "🔐 Reddit API Credentials Setup"
echo "================================"
echo ""
echo "This script will help you set up Reddit API credentials securely."
echo "Get your credentials at: https://www.reddit.com/prefs/apps"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    touch .env
fi

echo "Please enter your Reddit API credentials:"
echo ""

read -p "Reddit Client ID: " REDDIT_CLIENT_ID
read -p "Reddit Username: " REDDIT_USERNAME
read -s -p "Reddit Password: " REDDIT_PASSWORD
echo ""
read -s -p "Reddit Client Secret: " REDDIT_CLIENT_SECRET
echo ""

# Append to .env file
echo "" >> .env
echo "# Reddit API Credentials" >> .env
echo "export REDDIT_CLIENT_ID=\"$REDDIT_CLIENT_ID\"" >> .env
echo "export REDDIT_CLIENT_SECRET=\"$REDDIT_CLIENT_SECRET\"" >> .env
echo "export REDDIT_USERNAME=\"$REDDIT_USERNAME\"" >> .env
echo "export REDDIT_PASSWORD=\"$REDDIT_PASSWORD\"" >> .env

echo ""
echo "✅ Credentials saved to .env file"
echo ""
echo "To use these credentials, run:"
echo "source .env"
echo ""
echo "⚠️  IMPORTANT: Never commit the .env file to git!"
echo "Add .env to your .gitignore file."

# Check if .env is in .gitignore
if ! grep -q "\.env" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "✅ Added .env to .gitignore"
fi

echo ""
echo "🚀 You can now run the traffic generation system securely!"