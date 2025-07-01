#!/bin/bash

# Setup GitHub App for PR Orchestrator
# This script helps create and configure a dedicated GitHub App for PR orchestration

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🤖 GitHub App Setup for PR Orchestrator${NC}"
echo "============================================"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Repository details
OWNER="${GITHUB_OWNER:-IgorGanapolsky}"
REPO="${GITHUB_REPO:-ai-kindlemint-engine}"

echo -e "${BLUE}📋 Configuration:${NC}"
echo "Repository: ${OWNER}/${REPO}"
echo ""

# App configuration
APP_NAME="pr-orchestrator-${REPO}"
APP_DESCRIPTION="Automated PR management and merge orchestration for ${REPO}"

# Create app manifest
cat > github-app-manifest.json <<EOF
{
  "name": "${APP_NAME}",
  "description": "${APP_DESCRIPTION}",
  "url": "https://github.com/${OWNER}/${REPO}",
  "public": false,
  "default_permissions": {
    "actions": "read",
    "checks": "write",
    "contents": "write",
    "issues": "write",
    "metadata": "read",
    "pull_requests": "write",
    "statuses": "write"
  },
  "default_events": [
    "pull_request",
    "pull_request_review",
    "issue_comment",
    "check_run",
    "check_suite",
    "workflow_run"
  ],
  "webhook_active": true,
  "webhook_events": [
    "pull_request",
    "pull_request_review",
    "issue_comment"
  ]
}
EOF

echo -e "${YELLOW}📝 GitHub App Manifest created${NC}"
echo ""
echo -e "${BLUE}🔧 Manual Setup Instructions:${NC}"
echo ""
echo "1. Go to: https://github.com/settings/apps/new"
echo ""
echo "2. Fill in the following details:"
echo "   - GitHub App name: ${APP_NAME}"
echo "   - Description: ${APP_DESCRIPTION}"
echo "   - Homepage URL: https://github.com/${OWNER}/${REPO}"
echo ""
echo "3. Repository permissions (set to 'Read & Write'):"
echo "   ✓ Actions (Read)"
echo "   ✓ Checks"
echo "   ✓ Contents"
echo "   ✓ Issues"
echo "   ✓ Pull requests"
echo "   ✓ Commit statuses"
echo ""
echo "4. Subscribe to events:"
echo "   ✓ Pull request"
echo "   ✓ Pull request review"
echo "   ✓ Issue comment"
echo "   ✓ Check run"
echo "   ✓ Check suite"
echo "   ✓ Workflow run"
echo ""
echo "5. Where can this GitHub App be installed?"
echo "   ○ Only on this account"
echo ""
echo "6. Click 'Create GitHub App'"
echo ""
echo -e "${YELLOW}🔐 After creating the app:${NC}"
echo ""
echo "1. Generate a private key and save it securely"
echo "2. Note down the App ID and Installation ID"
echo "3. Install the app on your repository"
echo ""
echo "4. Add these secrets to your repository:"
echo "   gh secret set PR_ORCHESTRATOR_APP_ID --body=\"<YOUR_APP_ID>\""
echo "   gh secret set PR_ORCHESTRATOR_APP_PRIVATE_KEY < path/to/private-key.pem"
echo "   gh secret set PR_ORCHESTRATOR_INSTALLATION_ID --body=\"<YOUR_INSTALLATION_ID>\""
echo ""
echo "5. Update your workflow to use the app for authentication:"
echo ""
cat > pr-orchestrator-auth-example.yml <<'EOF'
      - name: Generate App Token
        id: app-token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ secrets.PR_ORCHESTRATOR_APP_ID }}
          private-key: ${{ secrets.PR_ORCHESTRATOR_APP_PRIVATE_KEY }}
          
      - name: Use App Token
        env:
          GITHUB_TOKEN: ${{ steps.app-token.outputs.token }}
        run: |
          # Your orchestrator commands here
          gh pr merge ...
EOF

echo -e "${GREEN}✅ Setup instructions complete!${NC}"
echo ""
echo "Example authentication code saved to: pr-orchestrator-auth-example.yml"
echo ""
echo -e "${BLUE}🚀 Benefits of using a dedicated GitHub App:${NC}"
echo "  • Bypass branch protection rules for automated merges"
echo "  • Fine-grained permissions control"
echo "  • Better audit trail and security"
echo "  • Rate limit improvements"
echo "  • Webhook event handling"
echo ""
echo -e "${YELLOW}⚡ Next steps:${NC}"
echo "1. Follow the manual setup instructions above"
echo "2. Update .github/workflows/pr-orchestrator.yml to use app authentication"
echo "3. Update scripts/setup_branch_protection_with_orchestrator.sh with app name"
echo "4. Test the orchestrator with a sample PR"

# Cleanup
rm -f github-app-manifest.json