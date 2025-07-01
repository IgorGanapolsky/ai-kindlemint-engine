#!/bin/bash

# Setup Branch Protection Rules for Personal GitHub Repository
# This script is specifically for personal repos (not organization repos)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔒 Setting up Branch Protection Rules (Personal Repo)${NC}"
echo "====================================================="

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

# Enable branch protection for personal repository
# Note: Personal repos have limited options compared to org repos
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
  -f required_status_checks[strict]=true \
  -f required_status_checks[contexts][]="Quick Validation Checks" \
  -f required_status_checks[contexts][]="Code Quality Checks" \
  -f required_status_checks[contexts][]="Test Suite (3.11)" \
  -f required_status_checks[contexts][]="Test Suite (3.12)" \
  -f required_status_checks[contexts][]="Business Logic Validation" \
  -f required_status_checks[contexts][]="Documentation Validation" \
  -f required_status_checks[contexts][]="PR Status Summary" \
  -f enforce_admins=false \
  -f required_pull_request_reviews[required_approving_review_count]=1 \
  -f required_pull_request_reviews[dismiss_stale_reviews]=true \
  -f required_pull_request_reviews[require_code_owner_reviews]=true \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -f required_conversation_resolution=true

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Branch protection rules configured successfully!${NC}"
else
    echo -e "${RED}❌ Failed to configure branch protection${NC}"
    echo "Note: Some settings may not be available for personal repositories"
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
    required_conversation_resolution: .required_conversation_resolution,
    required_checks: .required_status_checks.contexts
  }'

echo -e "\n${GREEN}🎯 Branch Protection Configuration Complete!${NC}"
echo "Main branch now requires:"
echo "  ✓ All CI checks to pass"
echo "  ✓ At least 1 approving review"
echo "  ✓ Up-to-date with main before merging"
echo "  ✓ Conversation resolution"
echo "  ✓ No direct pushes (PRs only)"
echo ""
echo -e "${YELLOW}⚠️  Note:${NC} Some features like team restrictions are not available for personal repos"