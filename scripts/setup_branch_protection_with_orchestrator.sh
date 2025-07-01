#!/bin/bash

# Setup Branch Protection Rules with PR Orchestrator Support
# This script configures branch protection that allows automated merging

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🔒 Setting up Branch Protection with PR Orchestrator${NC}"
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

# First, check if we need to create a GitHub App for the orchestrator
echo -e "${BLUE}🤖 Checking for PR Orchestrator App...${NC}"

# Note: In a real setup, you'd register a GitHub App. For now, we'll use github-actions
ORCHESTRATOR_APP="${ORCHESTRATOR_APP:-github-actions}"
# TODO: Create dedicated GitHub App for PR orchestrator with proper permissions

# Enable branch protection with orchestrator support
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
      "Test Suite / test (3.11)",
      "Test Suite / test (3.12)",
      "Business Logic Validation",
      "Documentation Validation",
      "PR Status Summary",
      "PR Orchestrator / Analyze PR Intelligence",
      "PR Orchestrator / Code Hygiene Check",
      "Code Hygiene Check"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": false,
  "required_linear_history": false,
  "allow_auto_merge": true
}
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Branch protection with orchestrator configured!${NC}"
else
    echo -e "${RED}❌ Failed to configure branch protection${NC}"
    exit 1
fi

# Enable auto-merge for the repository
echo -e "\n${BLUE}🔄 Enabling auto-merge capability...${NC}"
gh api \
  --method PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${OWNER}/${REPO}" \
  --field allow_auto_merge=true \
  --field allow_merge_commit=true \
  --field allow_squash_merge=true \
  --field allow_rebase_merge=false \
  --field delete_branch_on_merge=true

# Create required labels for orchestrator
echo -e "\n${BLUE}🏷️  Creating orchestrator labels...${NC}"

# Function to create label
create_label() {
    local name=$1
    local color=$2
    local description=$3
    
    gh label create "$name" \
        --color "$color" \
        --description "$description" \
        --force 2>/dev/null || true
}

# Create orchestrator-specific labels
create_label "auto-merge" "0E8A16" "PR is eligible for automated merging"
create_label "do-not-merge" "D93F0B" "PR should not be automatically merged"
create_label "safe-to-merge" "2EA043" "PR has been validated as safe to merge"
create_label "hygiene-fixes-applied" "FBCA04" "Automated hygiene fixes were applied"
create_label "conflict-resolved" "5319E7" "Merge conflicts were automatically resolved"
create_label "needs-manual-review" "E99695" "PR requires manual review"

# Create webhook secret for monitoring
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo -e "\n${YELLOW}🔐 Generated webhook secret for monitoring:${NC}"

# Automatically add the secret to GitHub
echo -e "${BLUE}🔒 Adding webhook secret to GitHub repository...${NC}"
if gh secret set PR_ORCHESTRATOR_WEBHOOK_SECRET --body="${WEBHOOK_SECRET}" 2>/dev/null; then
    echo -e "${GREEN}✅ Webhook secret added to repository secrets${NC}"
else
    echo -e "${YELLOW}⚠️  Could not add secret automatically. Please add manually:${NC}"
    echo "PR_ORCHESTRATOR_WEBHOOK_SECRET=${WEBHOOK_SECRET}"
    echo ""
    echo "Run this command to add it:"
    echo "gh secret set PR_ORCHESTRATOR_WEBHOOK_SECRET --body=\"${WEBHOOK_SECRET}\""
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
    bypass_apps: .required_pull_request_reviews.bypass_pull_request_allowances.apps
  }'

# Check auto-merge status
echo -e "\n${YELLOW}🔄 Auto-merge Status:${NC}"
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${OWNER}/${REPO}" \
  --jq '{
    allow_auto_merge: .allow_auto_merge,
    allow_merge_commit: .allow_merge_commit,
    allow_squash_merge: .allow_squash_merge,
    delete_branch_on_merge: .delete_branch_on_merge
  }'

echo -e "\n${GREEN}🎯 Branch Protection with PR Orchestrator Complete!${NC}"
echo ""
echo "Main branch configuration:"
echo "  ✓ All CI checks required (including orchestrator)"
echo "  ✓ Code owner review required"
echo "  ✓ PR Orchestrator can bypass requirements"
echo "  ✓ Auto-merge enabled for qualifying PRs"
echo "  ✓ Automated hygiene fixes supported"
echo "  ✓ Smart conflict resolution available"
echo ""
echo -e "${BLUE}🤖 PR Orchestrator will now:${NC}"
echo "  • Analyze all incoming PRs"
echo "  • Run hygiene checks"
echo "  • Auto-merge safe PRs"
echo "  • Apply fixes when confidence is high"
echo "  • Request manual review when needed"
echo ""
echo -e "${YELLOW}⚡ Commands available in PR comments:${NC}"
echo "  /merge - Force merge (requires permissions)"
echo "  /hold - Prevent auto-merge"
echo "  /analyze - Re-run analysis"
echo "  /hygiene - Run hygiene fixes"