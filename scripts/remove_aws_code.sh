#!/bin/bash
# AWS Code Removal Script
# Removes all AWS-related code from the repository
# ========================================================

set -e

echo "=================================================="
echo "🧹 AWS CODE REMOVAL SCRIPT"
echo "This will remove all AWS-related code and files"
echo "=================================================="
echo ""

# Create backup directory for safety
BACKUP_DIR="aws_code_backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# safe_remove moves the specified file or directory to the backup directory if it exists, preserving it instead of deleting.
safe_remove() {
    local path=$1
    if [ -e "$path" ]; then
        echo "   Moving $path to backup..."
        mv "$path" "$BACKUP_DIR/" 2>/dev/null || true
    fi
}

echo ""
echo "1️⃣ Removing AWS Lambda directory..."
safe_remove "lambda"

echo ""
echo "2️⃣ Removing AWS deployment scripts..."
safe_remove "scripts/delete_monitoring_stacks.sh"
safe_remove "scripts/aws_status_checker.py"
safe_remove "scripts/delete_all_aws_resources.sh"

echo ""
echo "3️⃣ Removing AWS configuration files..."
safe_remove "config/aws_status.json"

echo ""
echo "4️⃣ Removing AWS agent functions..."
safe_remove "agents/ci_orchestration_function.py"
safe_remove "agents/alert_orchestration_function.py"
safe_remove "agents/v3_orchestrator.py"
safe_remove "agents/intelligent_v3_orchestrator.py"

echo ""
echo "5️⃣ Removing AWS documentation..."
safe_remove "docs/AWS_BUSINESS_STRATEGY.md"
safe_remove "MANUAL_AWS_DEPLOYMENT.md"

echo ""
echo "6️⃣ Removing AWS test files..."
safe_remove "tests/unit/test_aws_deployment.py"

echo ""
echo "7️⃣ Updating setup.py to remove boto3 dependency..."
if [ -f "setup.py" ]; then
    # Remove boto3 from dependencies
    sed -i.bak '/boto3/d' setup.py && rm setup.py.bak
    echo "   ✅ Removed boto3 from setup.py"
fi

echo ""
echo "8️⃣ Creating migration documentation..."
cat > "AWS_MIGRATION_COMPLETE.md" << 'EOF'
# AWS Migration Complete

## Migration Date
$(date +"%Y-%m-%d")

## What Changed
- Removed all AWS infrastructure to save $5-15/month ($60-180/year)
- Migrated to 100% free tools:
  - GitHub Actions (CI/CD)
  - Sentry (monitoring)
  - Slack (notifications)
  - Local Python scripts (processing)

## Removed Components
- 2 CloudFormation stacks
- 2 Lambda functions
- 2 DynamoDB tables
- 1 SNS topic
- All AWS-related code

## Current Architecture
The platform now runs entirely on:
- Local Python scripts for book generation
- GitHub Actions for automation
- Free tier services for monitoring

## Cost Savings
- Previous: $5-15/month for unused AWS services
- Current: $0/month
- Annual savings: $60-180

## Backup Location
All removed code has been backed up to: $BACKUP_DIR
EOF

echo ""
echo "=================================================="
echo "✅ AWS CODE REMOVAL COMPLETE!"
echo "=================================================="
echo ""
echo "📋 Summary:"
echo "   - All AWS code moved to: $BACKUP_DIR"
echo "   - boto3 removed from dependencies"
echo "   - Migration documentation created"
echo ""
echo "💰 You're now saving $60-180/year!"
echo ""
echo "🎯 Next steps:"
echo "1. Review and commit these changes"
echo "2. Delete the backup directory after confirming everything works"
echo "3. Focus on building great books, not managing infrastructure!"
echo ""