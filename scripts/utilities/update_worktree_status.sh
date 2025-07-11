#!/bin/bash
# Auto-update WORKTREE_STATUS.md with current worktree states
# Usage: ./scripts/utilities/update_worktree_status.sh

set -e

STATUS_FILE="docs/WORKTREE_STATUS.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
MACHINE_INFO="$(uname -s) $(lsb_release -si 2>/dev/null || echo 'Linux') ($(basename $SHELL) $(bash --version | head -1 | cut -d' ' -f4))"

echo "🔄 Updating worktree status..."

# Get current worktree information
WORKTREES_INFO=$(git worktree list --porcelain)
MAIN_BRANCH=$(git rev-parse --abbrev-ref HEAD)
MAIN_COMMIT=$(git rev-parse --short HEAD)
MAIN_COMMIT_MSG=$(git log -1 --pretty=format:"%s")

# Check MCP server status
MCP_STATUS="❌ NOT RESPONDING"
if curl -s --connect-timeout 5 http://44.201.249.255:8080/health >/dev/null 2>&1; then
    MCP_STATUS="✅ RESPONDING"
fi

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

# Show brief summary
echo ""
echo "📊 Current Worktree Summary:"
git worktree list
echo ""
echo "🎯 Main Directory: $MAIN_BRANCH ($MAIN_COMMIT)"
echo "🌐 MCP Server: $MCP_STATUS"
