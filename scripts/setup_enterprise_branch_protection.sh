#!/bin/bash

# Enterprise Branch Protection Setup
# Implements CTO-approved 3-tier branch protection strategy

set -e

echo "🏗️ Setting up Enterprise Branch Protection Strategy..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository information
REPO="IgorGanapolsky/ai-kindlemint-engine"

echo -e "${BLUE}📋 Repository: $REPO${NC}"

# setup_branch_protection configures GitHub branch protection rules for a specified branch and protection level using the GitHub CLI.
#
# Applies tailored protection settings for "executive", "technical", or "automated" levels, enforcing status checks, review requirements, and permissions according to enterprise policy.
setup_branch_protection() {
    local branch=$1
    local protection_level=$2
    
    echo -e "${YELLOW}🔒 Setting up protection for branch: $branch (Level: $protection_level)${NC}"
    
    case $protection_level in
        "executive")
            # Main branch - Maximum protection
            gh api repos/$REPO/branches/$branch/protection \
                --method PUT \
                --field required_status_checks='{"strict":true,"contexts":["Quick Validation Checks","Code Quality Checks","Test Suite / test (3.11)","Test Suite / test (3.12)","Business Logic Validation","Documentation Validation","Executive Security Review","Staged PR Orchestrator / Execute Main Branch Workflow"]}' \
                --field enforce_admins=true \
                --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":2}' \
                --field restrictions='{"users":["IgorGanapolsky"],"teams":[],"apps":[]}' \
                --field required_conversation_resolution=true \
                --field allow_force_pushes=false \
                --field allow_deletions=false \
                --field block_creations=false
            ;;
            
        "technical")
            # Staging branch - Technical lead approval
            gh api repos/$REPO/branches/$branch/protection \
                --method PUT \
                --field required_status_checks='{"strict":true,"contexts":["Quick Validation Checks","Code Quality Checks","Test Suite / test (3.11)","Test Suite / test (3.12)","Staged PR Orchestrator / Execute Staging Branch Workflow"]}' \
                --field enforce_admins=false \
                --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
                --field required_conversation_resolution=true \
                --field allow_force_pushes=false \
                --field allow_deletions=false
            ;;
            
        "automated")
            # Develop branch - Automated with safety checks
            gh api repos/$REPO/branches/$branch/protection \
                --method PUT \
                --field required_status_checks='{"strict":true,"contexts":["Quick Validation Checks","Code Quality Checks","Staged PR Orchestrator / Execute Develop Branch Workflow"]}' \
                --field enforce_admins=false \
                --field required_pull_request_reviews='{"dismiss_stale_reviews":false,"require_code_owner_reviews":false,"required_approving_review_count":0}' \
                --field required_conversation_resolution=false \
                --field allow_force_pushes=false \
                --field allow_deletions=true
            ;;
    esac
    
    echo -e "${GREEN}✅ Branch protection configured for: $branch${NC}"
}

# Setup branch protections
echo -e "${BLUE}🔐 Configuring Enterprise Branch Protection...${NC}"

setup_branch_protection "main" "executive"
setup_branch_protection "staging" "technical" 
setup_branch_protection "develop" "automated"

# Setup default branch policies
echo -e "${YELLOW}📝 Configuring repository policies...${NC}"

# Set develop as default branch for new PRs
gh api repos/$REPO \
    --method PATCH \
    --field default_branch="develop"

echo -e "${GREEN}✅ Default branch set to 'develop'${NC}"

# Create branch protection bypass for emergencies
echo -e "${YELLOW}🚨 Setting up emergency bypass procedures...${NC}"

# Create emergency team (if it doesn't exist)
gh api orgs/IgorGanapolsky/teams \
    --method POST \
    --field name="emergency-response" \
    --field description="Emergency bypass team for critical hotfixes" \
    --field privacy="closed" || echo "Emergency team may already exist"

echo -e "${GREEN}✅ Enterprise Branch Protection Setup Complete!${NC}"

echo -e "${BLUE}📊 Branch Protection Summary:${NC}"
echo -e "  ${RED}🔒 main${NC}     - Executive approval (2 reviews, admin enforcement)"
echo -e "  ${YELLOW}🔧 staging${NC}  - Technical approval (1 review, status checks)"
echo -e "  ${GREEN}🤖 develop${NC}  - Automated merge (status checks only)"

echo -e "${BLUE}🎯 PR Routing Guidelines:${NC}"
echo -e "  • Bot PRs (style, deps) → ${GREEN}develop${NC}"
echo -e "  • Features & tests → ${YELLOW}staging${NC}"
echo -e "  • Releases & hotfixes → ${RED}main${NC} (executive approval)"

echo -e "${GREEN}🚀 Ready for enterprise-grade PR orchestration!${NC}"