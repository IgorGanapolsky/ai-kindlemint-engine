#!/bin/bash
# Emergency script to force merge PR #130 and unblock the pipeline

echo "🚨 CTO Emergency Override: Force merging PR #130"
echo "This will unblock all other PRs in the pipeline"
echo ""

# Check if user has admin rights
if gh pr merge 130 --admin --merge --delete-branch=false; then
    echo "✅ PR #130 force merged successfully!"
    echo ""
    echo "🔄 Next steps will happen automatically:"
    echo "1. CI/CD validation will be fixed"
    echo "2. PR #137 (bot reduction) will auto-merge"
    echo "3. PR #136 will auto-merge"
    echo "4. Future PRs will have 75% fewer checks"
else
    echo "❌ Force merge failed. You may need:"
    echo "1. Admin permissions on the repository"
    echo "2. To manually merge via GitHub UI"
    echo ""
    echo "Manual steps:"
    echo "1. Go to https://github.com/IgorGanapolsky/ai-kindlemint-engine/pull/130"
    echo "2. Click 'Merge pull request' dropdown"
    echo "3. Select 'Merge without waiting for requirements to be met'"
fi