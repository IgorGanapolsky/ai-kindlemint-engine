#!/bin/bash
# Emergency cleanup script for all worktrees

echo "🧹 Emergency Worktree Cleanup"
echo "============================="

# Count total uncommitted files
TOTAL_UNCOMMITTED=0

for worktree in worktrees/*; do
    if [ -d "$worktree" ]; then
        echo ""
        echo "📁 Processing $worktree..."
        cd "$worktree"
        
        # Count uncommitted files
        UNCOMMITTED=$(git status --porcelain | wc -l)
        TOTAL_UNCOMMITTED=$((TOTAL_UNCOMMITTED + UNCOMMITTED))
        
        if [ $UNCOMMITTED -gt 0 ]; then
            echo "  ⚠️  Found $UNCOMMITTED uncommitted files"
            
            # Show first few files
            echo "  First 5 files:"
            git status --porcelain | head -5 | sed 's/^/    /'
            
            # Stash all changes
            echo "  📦 Stashing all changes..."
            git stash push -m "Emergency cleanup $(date +%Y%m%d_%H%M%S)" --include-untracked
            
            # Clean up any remaining files
            git clean -fd
            
            echo "  ✅ Worktree cleaned"
        else
            echo "  ✅ Already clean"
        fi
        
        cd - >/dev/null
    fi
done

echo ""
echo "🎯 Summary:"
echo "  - Total uncommitted files found: $TOTAL_UNCOMMITTED"
echo "  - All changes have been stashed (recoverable)"
echo "  - Worktrees are now clean"
echo ""
echo "💡 To recover stashed changes later:"
echo "  cd worktrees/<name> && git stash list"
echo ""
echo "✅ Cleanup complete!"