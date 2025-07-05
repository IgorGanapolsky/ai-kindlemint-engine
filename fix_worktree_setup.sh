#!/bin/bash
# Fix Worktree Setup for Claude Code Parallel Development

echo "🔧 Fixing Worktree Setup for Claude Code"
echo "========================================"

# Step 1: Free up main branch
echo "📂 Step 1: Freeing up main branch..."
if [ -d "worktrees/ci-fixes" ]; then
    cd worktrees/ci-fixes
    git add -A && git commit -m "checkpoint: saving work before worktree restructure" || true
    git push || true
    cd ../..
    
    git worktree remove worktrees/ci-fixes --force
    echo "✅ Main branch freed from worktree"
fi

# Step 2: Create a proper main worktree (but not lock main branch)
echo "📂 Step 2: Setting up accessible main workspace..."
git worktree add worktrees/main-dev main
echo "✅ Created main-dev worktree for main branch work"

# Step 3: Update all worktrees to latest
echo "📂 Step 3: Updating all worktrees to latest commits..."
for worktree in worktrees/*/; do
    if [ -d "$worktree" ]; then
        worktree_name=$(basename "$worktree")
        echo "  📋 Updating $worktree_name..."
        
        cd "$worktree"
        git fetch origin
        
        # Get the branch this worktree tracks
        branch=$(git branch --show-current)
        
        # Pull latest if tracking remote
        if git rev-parse --verify "origin/$branch" >/dev/null 2>&1; then
            git pull origin "$branch" || echo "    ⚠️ Could not pull $branch"
        fi
        
        cd - >/dev/null
        echo "    ✅ Updated $worktree_name"
    fi
done

# Step 4: Create Claude Code optimized structure
echo "📂 Step 4: Creating Claude Code optimized structure..."

# Create quick access symlinks
ln -sf worktrees/main-dev main-work 2>/dev/null || true
ln -sf worktrees/puzzle-gen puzzle-work 2>/dev/null || true
ln -sf worktrees/parallel-pdf pdf-work 2>/dev/null || true

echo "📋 Created quick access symlinks:"
echo "  • main-work/ → worktrees/main-dev/"
echo "  • puzzle-work/ → worktrees/puzzle-gen/"  
echo "  • pdf-work/ → worktrees/parallel-pdf/"

# Step 5: Update worktree orchestrator config
echo "📂 Step 5: Updating orchestrator configuration..."
cat > .claude/worktree-config.json << 'EOF'
{
  "parallel_development": true,
  "main_branch_accessible": true,
  "worktrees": {
    "main-dev": {
      "branch": "main",
      "purpose": "Main development and releases",
      "quick_access": "main-work/"
    },
    "puzzle-gen": {
      "branch": "worktree/puzzle-generation", 
      "purpose": "Puzzle generation features",
      "quick_access": "puzzle-work/"
    },
    "parallel-pdf": {
      "branch": "feature/parallel-pdf-generation",
      "purpose": "PDF generation optimization"
    },
    "parallel-puzzles": {
      "branch": "feature/parallel-puzzle-generation", 
      "purpose": "Puzzle generation parallelization"
    },
    "parallel-qa": {
      "branch": "feature/parallel-qa-validation",
      "purpose": "QA validation automation"
    }
  },
  "claude_code_optimized": true,
  "quick_switch_enabled": true,
  "parallel_safe": true
}
EOF

echo "✅ Created Claude Code optimized configuration"

# Step 6: Test the setup
echo "📂 Step 6: Testing the new setup..."
echo "Current directory access:"
echo "  📁 Main repo: $(pwd)"
echo "  📁 Main work: $(readlink -f main-work 2>/dev/null || echo 'not available')"
echo "  📁 Puzzle work: $(readlink -f puzzle-work 2>/dev/null || echo 'not available')"

echo ""
echo "🎯 Worktree Status Summary:"
git worktree list

echo ""
echo "✅ Worktree Setup Complete!"
echo ""
echo "🚀 Claude Code can now:"
echo "  • Work on main branch directly"
echo "  • Switch contexts seamlessly"  
echo "  • Use parallel worktrees efficiently"
echo "  • Access quick symlinks (main-work/, puzzle-work/, etc.)"
echo ""
echo "💡 Usage:"
echo "  cd main-work/     # Work on main branch"
echo "  cd puzzle-work/   # Work on puzzle features"
echo "  cd .              # Stay in main repo"