#!/bin/bash
# Start continuous PR monitoring with auto-fix

echo "🚀 Starting GitHub PR Monitor & Auto-Fixer"
echo "=========================================="
echo ""
echo "This will continuously:"
echo "  ✓ Monitor all open PRs"
echo "  ✓ Detect CI failures"
echo "  ✓ Automatically fix issues"
echo "  ✓ Trigger fix workflows"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN not set!"
    echo "Please run: export GITHUB_TOKEN='your-github-pat'"
    exit 1
fi

# Start monitoring (check every 5 minutes)
python3 scripts/github_mcp_orchestrator.py monitor --interval 300