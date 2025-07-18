#!/bin/bash
# AWS Configuration Template
# DO NOT commit actual credentials to git!

# Set AWS credentials (replace with your actual credentials)
# aws configure set aws_access_key_id YOUR_ACCESS_KEY_ID
# aws configure set aws_secret_access_key YOUR_SECRET_ACCESS_KEY

# Set default region
aws configure set default.region us-east-1

echo "AWS configuration template created."
echo "Please edit this file with your actual credentials and rename to aws_config.sh"
echo "IMPORTANT: Never commit actual credentials to git!" 