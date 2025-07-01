#!/bin/bash

# Setup Branch Protection Rules for AI-KindleMint-Engine
# This script configures comprehensive branch protection for the main branch

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔒 Setting up Branch Protection Rules${NC}"
echo "================================================"

# Repository details
OWNER="IgorGanapolsky"
REPO="ai-kindlemint-engine"
BRANCH="main"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${YELLOW}📋 Configuring protection for branch: ${BRANCH}${NC}"

# Enable branch protection with all rules
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Quick Validation Checks",
      "Code Quality Checks",
      "Test Suite (3.11)",
      "Test Suite (3.12)",
      "Business Logic Validation",
      "Documentation Validation",
      "PR Status Summary"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "require_last_push_approval": true,
    "bypass_pull_request_allowances": {
      "users": [],
      "teams": [],
      "apps": []
    }
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": false,
  "required_linear_history": false
}
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Branch protection rules configured successfully!${NC}"
else
    echo -e "${RED}❌ Failed to configure branch protection${NC}"
    exit 1
fi

# Display current protection status
echo -e "\n${YELLOW}📊 Current Protection Status:${NC}"
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
  --jq '{
    required_reviews: .required_pull_request_reviews.required_approving_review_count,
    dismiss_stale_reviews: .required_pull_request_reviews.dismiss_stale_reviews,
    require_code_owner_reviews: .required_pull_request_reviews.require_code_owner_reviews,
    strict_status_checks: .required_status_checks.strict,
    enforce_admins: .enforce_admins,
    required_conversation_resolution: .required_conversation_resolution
  }'

echo -e "\n${GREEN}🎯 Branch Protection Configuration Complete!${NC}"
echo "Main branch now requires:"
echo "  ✓ All CI checks to pass"
echo "  ✓ Code owner review"
echo "  ✓ Up-to-date with main"
echo "  ✓ Conversation resolution"
echo "  ✓ No direct commits (even from admins)"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC} All future changes must go through PRs!"