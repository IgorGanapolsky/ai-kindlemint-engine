#!/bin/bash
# Emergency Workflow Cleanup Script
# Created by CTO to stop orchestration death spiral

echo "🚨 EMERGENCY WORKFLOW CLEANUP INITIATED"
echo "========================================="

# List of problematic workflows to disable
WORKFLOWS_TO_DISABLE=(
    "Autonomous AI Review Bot Handler"
    "AI Development Team - Intelligent PR Review & Merge System"
    "Intelligent PR Fixer & Merger"
    "Staged PR Orchestrator - Enterprise Security Model"
    "Aggressive PR Merger - Force Merge All PRs"
    "Auto Review Market Research"
    "Autonomous CodeRabbit Handler"
)

# Cancel all running workflows first
echo "📍 Step 1: Cancelling all running workflows..."
gh run list --status in_progress --json databaseId -q '.[].databaseId' | while read run_id; do
    echo "   Cancelling run $run_id..."
    gh run cancel $run_id 2>/dev/null || true
done

# Disable problematic workflows
echo -e "\n📍 Step 2: Disabling problematic workflows..."
for workflow in "${WORKFLOWS_TO_DISABLE[@]}"; do
    echo "   Disabling: $workflow"
    gh workflow disable "$workflow" 2>/dev/null || echo "   ⚠️  Already disabled or not found"
done

# Show remaining active workflows
echo -e "\n📍 Step 3: Remaining active workflows:"
gh workflow list | grep -E "active|enabled" | awk '{print "   ✓", $1}'

# Count workflow runs
TOTAL_RUNS=$(gh run list --limit 1000 --json databaseId | jq '. | length')
echo -e "\n📊 Statistics:"
echo "   Total recent workflow runs: $TOTAL_RUNS"

echo -e "\n✅ CLEANUP COMPLETE!"
echo "   Next steps:"
echo "   1. Review remaining active workflows"
echo "   2. Re-enable workflows ONE AT A TIME"
echo "   3. Fix the issue_comment trigger loops"