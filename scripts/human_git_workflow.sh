#!/bin/bash
# Human Git Workflow - Quick commands for solo developer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to quick commit and push to main (human changes)
quick_push() {
    local message="$1"
    if [ -z "$message" ]; then
        print_error "Commit message required"
        echo "Usage: $0 quick-push \"your commit message\""
        exit 1
    fi
    
    print_status "Quick push to main (human workflow)..."
    
    # Check if we're on main
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        print_warning "Not on main branch. Switching to main..."
        git checkout main
        git pull origin main
    fi
    
    # Add, commit, push
    git add .
    git commit -m "👨‍💻 $message"
    git push origin main
    
    print_success "Pushed to main: $message"
}

# Function to create a feature branch for complex changes
feature_branch() {
    local branch_name="$1"
    local message="$2"
    
    if [ -z "$branch_name" ]; then
        print_error "Branch name required"
        echo "Usage: $0 feature-branch \"branch-name\" \"optional description\""
        exit 1
    fi
    
    print_status "Creating feature branch: $branch_name"
    
    # Ensure we're on latest main
    git checkout main
    git pull origin main
    
    # Create and switch to feature branch
    git checkout -b "feature/$branch_name"
    
    print_success "Created feature branch: feature/$branch_name"
    
    if [ -n "$message" ]; then
        echo "# Feature: $branch_name" > FEATURE_NOTES.md
        echo "" >> FEATURE_NOTES.md
        echo "$message" >> FEATURE_NOTES.md
        echo "" >> FEATURE_NOTES.md
        echo "## TODO:" >> FEATURE_NOTES.md
        echo "- [ ] Implement core functionality" >> FEATURE_NOTES.md
        echo "- [ ] Add tests" >> FEATURE_NOTES.md
        echo "- [ ] Update documentation" >> FEATURE_NOTES.md
        
        git add FEATURE_NOTES.md
        git commit -m "feat: Start $branch_name - $message"
        git push origin "feature/$branch_name"
        
        print_success "Pushed feature branch with notes"
    fi
}

# Function to finish feature and merge to main
finish_feature() {
    local message="$1"
    
    current_branch=$(git branch --show-current)
    if [[ ! "$current_branch" =~ ^feature/ ]]; then
        print_error "Not on a feature branch"
        exit 1
    fi
    
    if [ -z "$message" ]; then
        print_error "Merge message required"
        echo "Usage: $0 finish-feature \"completion message\""
        exit 1
    fi
    
    print_status "Finishing feature branch: $current_branch"
    
    # Final commit on feature branch
    git add .
    git commit -m "feat: Complete $current_branch - $message" || true
    git push origin "$current_branch"
    
    # Switch to main and merge
    git checkout main
    git pull origin main
    git merge "$current_branch" --no-ff -m "Merge $current_branch: $message"
    git push origin main
    
    # Clean up
    git branch -d "$current_branch"
    git push origin --delete "$current_branch"
    
    # Remove feature notes if exists
    if [ -f "FEATURE_NOTES.md" ]; then
        rm FEATURE_NOTES.md
        git add FEATURE_NOTES.md
        git commit -m "chore: Clean up feature notes"
        git push origin main
    fi
    
    print_success "Feature completed and merged to main"
}

# Function to check repository status
status_check() {
    print_status "Repository Status Check"
    echo
    
    # Git status
    echo -e "${BLUE}Git Status:${NC}"
    git status --short
    echo
    
    # Recent commits
    echo -e "${BLUE}Recent Commits:${NC}"
    git log --oneline -5
    echo
    
    # Branch protection status
    echo -e "${BLUE}Branch Protection:${NC}"
    gh api repos/:owner/:repo/branches/main/protection --jq '.required_status_checks.contexts[]' 2>/dev/null || echo "No protection rules found"
    echo
    
    # Open PRs
    echo -e "${BLUE}Open PRs:${NC}"
    gh pr list --state open || echo "No open PRs"
}

# Function to emergency rollback
emergency_rollback() {
    local commits="${1:-1}"
    
    print_warning "EMERGENCY ROLLBACK - Rolling back $commits commit(s)"
    read -p "Are you sure? This will reset main branch. (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        git checkout main
        git reset --hard "HEAD~$commits"
        git push origin main --force-with-lease
        print_success "Rolled back $commits commit(s)"
    else
        print_status "Rollback cancelled"
    fi
}

# Main command dispatcher
case "$1" in
    "quick-push"|"qp")
        quick_push "$2"
        ;;
    "feature-branch"|"fb")
        feature_branch "$2" "$3"
        ;;
    "finish-feature"|"ff")
        finish_feature "$2"
        ;;
    "status"|"st")
        status_check
        ;;
    "rollback"|"rb")
        emergency_rollback "$2"
        ;;
    *)
        echo "Human Git Workflow Helper"
        echo
        echo "Commands:"
        echo "  quick-push (qp) \"message\"     - Quick commit and push to main"
        echo "  feature-branch (fb) \"name\"    - Create feature branch"
        echo "  finish-feature (ff) \"message\" - Merge feature to main"
        echo "  status (st)                    - Check repository status"
        echo "  rollback (rb) [commits]        - Emergency rollback"
        echo
        echo "Examples:"
        echo "  $0 quick-push \"fix: update documentation\""
        echo "  $0 feature-branch \"payment-system\" \"Add Stripe integration\""
        echo "  $0 finish-feature \"Payment system complete\""
        echo "  $0 status"
        exit 1
        ;;
esac
