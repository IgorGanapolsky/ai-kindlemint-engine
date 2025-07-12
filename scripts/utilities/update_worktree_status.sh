#!/bin/bash
<<<<<<< HEAD
# Auto-update WORKTREE_STATUS.md with current worktree states
# Usage: ./scripts/utilities/update_worktree_status.sh

set -e

STATUS_FILE="docs/WORKTREE_STATUS.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
=======

# Update Worktree Status Script
# This script updates the worktree status documentation after work is completed
# Combines orchestration tracking with GitHub MCP integration status

set -e

WORKTREE_STATUS_FILE="docs/WORKTREE_STATUS.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_WORKTREE=$(pwd)
LAST_COMMIT=$(git log -1 --format="%h - %s")
>>>>>>> origin
MACHINE_INFO="$(uname -s) $(lsb_release -si 2>/dev/null || echo 'Linux') ($(basename $SHELL) $(bash --version | head -1 | cut -d' ' -f4))"

echo "🔄 Updating worktree status..."

<<<<<<< HEAD
# Get current worktree information
WORKTREES_INFO=$(git worktree list --porcelain)
MAIN_BRANCH=$(git rev-parse --abbrev-ref HEAD)
MAIN_COMMIT=$(git rev-parse --short HEAD)
MAIN_COMMIT_MSG=$(git log -1 --pretty=format:"%s")
=======
# Create backup
if [ -f "$WORKTREE_STATUS_FILE" ]; then
    cp "$WORKTREE_STATUS_FILE" "${WORKTREE_STATUS_FILE}.backup"
fi
>>>>>>> origin

# Check MCP server status
MCP_STATUS="❌ NOT RESPONDING"
if curl -s --connect-timeout 5 http://44.201.249.255:8080/health >/dev/null 2>&1; then
    MCP_STATUS="✅ RESPONDING"
fi

<<<<<<< HEAD
# Update the timestamp and machine info in the status file
sed -i "s/\*\*Last Updated:\*\* .*/\*\*Last Updated:\*\* $TIMESTAMP/g" "$STATUS_FILE"
sed -i "s/\*\*Machine:\*\* .*/\*\*Machine:\*\* $MACHINE_INFO/g" "$STATUS_FILE"

# Update main directory info
sed -i "s/- \*\*Branch\*\*:.*/- \*\*Branch\*\*: \`$MAIN_BRANCH\`/g" "$STATUS_FILE"
sed -i "s/- \*\*Last Commit\*\*:.*/- \*\*Last Commit\*\*: \`$MAIN_COMMIT\` - $MAIN_COMMIT_MSG/g" "$STATUS_FILE"

# Update MCP server status
sed -i "s/- \*\*AWS EC2\*\*:.*/- \*\*AWS EC2\*\*: \`44.201.249.255:8080\` - $MCP_STATUS (connection timeout)/g" "$STATUS_FILE"

echo "✅ Updated $STATUS_FILE"
echo "📝 Current state preserved for handoff"
=======
# Get current worktree information
WORKTREES_INFO=$(git worktree list --porcelain 2>/dev/null || echo "Single worktree setup")

# Update the status file with current information
sed -i "s/\*\*Last Updated:\*\* .*/\*\*Last Updated:\*\* $TIMESTAMP/g" "$WORKTREE_STATUS_FILE" 2>/dev/null || true
sed -i "s/\*\*Current Branch:\*\* .*/\*\*Current Branch:\*\* $CURRENT_BRANCH/g" "$WORKTREE_STATUS_FILE" 2>/dev/null || true
sed -i "s/\*\*Current Worktree:\*\* .*/\*\*Current Worktree:\*\* $CURRENT_WORKTREE/g" "$WORKTREE_STATUS_FILE" 2>/dev/null || true
sed -i "s/\*\*Last Commit:\*\* .*/\*\*Last Commit:\*\* $LAST_COMMIT/g" "$WORKTREE_STATUS_FILE" 2>/dev/null || true

# Update MCP server status if the line exists
sed -i "s/- \*\*AWS EC2\*\*:.*/- \*\*AWS EC2\*\*: \`44.201.249.255:8080\` - $MCP_STATUS (transitioning to local setup)/g" "$WORKTREE_STATUS_FILE" 2>/dev/null || true

echo "✅ Worktree status updated in $WORKTREE_STATUS_FILE"
echo "📊 Current status:"
echo "   - Branch: $CURRENT_BRANCH"
echo "   - Last commit: $LAST_COMMIT"
echo "   - Worktree: $CURRENT_WORKTREE"
echo "   - MCP Server: $MCP_STATUS"
>>>>>>> origin

# Show brief summary
echo ""
echo "📊 Current Worktree Summary:"
<<<<<<< HEAD
git worktree list
echo ""
echo "🎯 Main Directory: $MAIN_BRANCH ($MAIN_COMMIT)"
=======
git worktree list 2>/dev/null || echo "Single worktree: $CURRENT_WORKTREE on $CURRENT_BRANCH"
echo ""
echo "🎯 Status: Combined orchestration + GitHub MCP integration"
>>>>>>> origin
echo "🌐 MCP Server: $MCP_STATUS"
