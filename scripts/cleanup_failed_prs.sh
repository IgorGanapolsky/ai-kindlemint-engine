#!/bin/bash

# Cleanup Failed PRs Script
# Automatically closes failed test PRs and manages PR queue

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🧹 PR Queue Cleanup Script${NC}"
echo "============================="

# Check if gh CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub${NC}"
    exit 1
fi

# Get all open PRs
echo -e "${BLUE}📋 Fetching open PRs...${NC}"
prs=$(gh pr list --state open --json number,title,headRefName,author,labels,updatedAt --limit 50)

# Parse and categorize PRs
failed_test_prs=()
formatting_prs=()
dependency_prs=()
main_prs=()

echo "$prs" | jq -r '.[] | [.number, .title, .headRefName, .author.login] | @tsv' | while IFS=$'\t' read -r number title branch author; do
    # Check for failed test PRs (auto-generated)
    if [[ "$title" =~ ^"Add Tests for PR#"[0-9]+ ]] && [[ "$author" == "seer-by-sentry[bot]" ]]; then
        # Check if PR has failing checks
        checks=$(gh pr checks $number --json conclusion 2>/dev/null || echo "[]")
        failed_checks=$(echo "$checks" | jq '[.[] | select(.conclusion == "failure" or .conclusion == "cancelled")] | length')
        
        if [[ "$failed_checks" -gt 0 ]]; then
            failed_test_prs+=($number)
            echo -e "${RED}❌ Failed test PR #$number: $title${NC}"
        fi
    # Check for formatting/style PRs
    elif [[ "$title" =~ ^"style:" ]] || [[ "$title" =~ "format code" ]]; then
        formatting_prs+=($number)
        echo -e "${YELLOW}🎨 Formatting PR #$number: $title${NC}"
    # Check for dependency PRs
    elif [[ "$author" == "dependabot[bot]" ]] || [[ "$author" == "renovate[bot]" ]]; then
        dependency_prs+=($number)
        echo -e "${BLUE}📦 Dependency PR #$number: $title${NC}"
    else
        main_prs+=($number)
        echo -e "${GREEN}🚀 Main PR #$number: $title${NC}"
    fi
done

# Interactive cleanup
echo ""
echo -e "${YELLOW}🔍 Cleanup Options:${NC}"
echo "1. Close all failed test PRs (${#failed_test_prs[@]} found)"
echo "2. Auto-merge formatting PRs (${#formatting_prs[@]} found)"
echo "3. Review dependency PRs (${#dependency_prs[@]} found)"
echo "4. Show main PRs status (${#main_prs[@]} found)"
echo "5. Run automated cleanup (recommended)"
echo "6. Exit"

read -p "Choose option (1-6): " choice

case $choice in
    1)
        echo -e "${RED}🗑️  Closing failed test PRs...${NC}"
        for pr in "${failed_test_prs[@]}"; do
            echo "Closing PR #$pr"
            gh pr close $pr --comment "Closing failed auto-generated test PR. Tests will be handled in the main development workflow." --delete-branch
        done
        ;;
    2)
        echo -e "${YELLOW}🎨 Auto-merging formatting PRs...${NC}"
        for pr in "${formatting_prs[@]}"; do
            # Check if all checks pass
            if gh pr checks $pr --json conclusion | jq -e '[.[] | select(.conclusion != "success")] | length == 0' > /dev/null; then
                echo "Auto-merging formatting PR #$pr"
                gh pr merge $pr --auto --squash --delete-branch
            else
                echo "⚠️  PR #$pr has failing checks, skipping"
            fi
        done
        ;;
    3)
        echo -e "${BLUE}📦 Reviewing dependency PRs...${NC}"
        for pr in "${dependency_prs[@]}"; do
            gh pr view $pr
            read -p "Merge PR #$pr? (y/n): " merge_choice
            if [[ "$merge_choice" == "y" ]]; then
                gh pr merge $pr --auto --squash --delete-branch
            fi
        done
        ;;
    4)
        echo -e "${GREEN}🚀 Main PRs:${NC}"
        for pr in "${main_prs[@]}"; do
            gh pr view $pr --json number,title,author,labels,mergeable,reviewDecision
        done
        ;;
    5)
        echo -e "${GREEN}🤖 Running automated cleanup...${NC}"
        
        # Close failed test PRs
        for pr in "${failed_test_prs[@]}"; do
            echo "Auto-closing failed test PR #$pr"
            gh pr close $pr --comment "🤖 Auto-closing failed test PR. Main development workflow handles testing." --delete-branch
        done
        
        # Auto-merge safe formatting PRs
        for pr in "${formatting_prs[@]}"; do
            if gh pr checks $pr --json conclusion | jq -e '[.[] | select(.conclusion != "success")] | length == 0' > /dev/null; then
                echo "Auto-merging safe formatting PR #$pr"
                gh pr merge $pr --auto --squash --delete-branch
            fi
        done
        
        echo -e "${GREEN}✅ Automated cleanup complete!${NC}"
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ PR cleanup complete!${NC}"
echo ""
echo -e "${BLUE}📊 Current PR status:${NC}"
gh pr list --state open