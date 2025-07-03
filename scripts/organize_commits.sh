#!/bin/bash
# Organize commits for the messy project

echo "🧹 Organizing project commits..."
echo "================================"

# Function to stage and commit files
commit_group() {
    local message="$1"
    shift
    local files=("$@")
    
    if [ ${#files[@]} -gt 0 ]; then
        echo "📦 Staging files for: $message"
        for file in "${files[@]}"; do
            if [ -f "$file" ]; then
                git add "$file"
            fi
        done
        
        # Show what will be committed
        echo "Files to commit:"
        git status --short | grep "^A"
        
        echo "Commit message: $message"
        read -p "Proceed with commit? (y/n): " confirm
        
        if [ "$confirm" = "y" ]; then
            git commit -m "$message"
            echo "✅ Committed!"
        else
            git reset
            echo "❌ Skipped, files unstaged"
        fi
        echo
    fi
}

# Group 1: Configuration files
echo "📁 Group 1: Configuration Files"
config_files=(
    "ci_analysis_enhanced.json" 
    "ci_failures_enhanced.json"
    "pre-commit-output.txt"
    "lambda/deployment/lambda-execution-role.json"
    "lambda/deployment/orchestration-policy.json"
)
commit_group "config: Add configuration and deployment files" "${config_files[@]}"

# Group 2: Test files
echo "📁 Group 2: Test Files"
test_files=(
    "tests/unit/test_agent_types.py"
    "tests/unit/test_base_validator.py"
    "tests/unit/test_simple_coverage.py"
    "tests/unit/test_utils_config.py"
)
commit_group "test: Add unit test files for coverage improvement" "${test_files[@]}"

# Group 3: Lambda/Infrastructure files
echo "📁 Group 3: Lambda Infrastructure"
lambda_files=(
    "lambda/alert-orchestration-full.zip"
    "lambda/ci-orchestration-full.zip"
    "lambda/package_lambdas.sh"
    "lambda/requirements.txt"
)
commit_group "feat: Add Lambda deployment packages and scripts" "${lambda_files[@]}"

# Group 4: Scripts and tools
echo "📁 Group 4: Scripts and Tools"
script_files=(
    "scripts/hygiene_cleanup.py"
    "scripts/organize_commits.sh"
    "scripts/ci_orchestration/ci_monitor_enhanced.py"
    "scripts/ci_orchestration/ci_orchestrator_enhanced.py"
)
commit_group "feat: Add orchestration and cleanup scripts" "${script_files[@]}"

# Group 5: Agent implementations
echo "📁 Group 5: Agent Implementations"
agent_files=(
    "src/kindlemint/agents/pdf_layout_agent.py"
    "src/kindlemint/agents/puzzle_generator_agent.py"
    "src/kindlemint/agents/puzzle_validator_agent.py"
    "src/kindlemint/agents/code_hygiene_orchestrator.py"
)
commit_group "feat: Add specialized agent implementations" "${agent_files[@]}"

# Group 7: Marketing module
echo "📁 Group 7: Marketing Module"
marketing_files=(
    "kindlemint/marketing/"
)
commit_group "feat: Add marketing module" "${marketing_files[@]}"

# Group 8: Temporary files
echo "📁 Group 8: Temporary Files"
temp_files=(
    "temp_puzzle_image.png"
)
# Don't commit these, just list them
echo "⚠️  Found temporary files that should be deleted:"
for file in "${temp_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   - $file"
    fi
done

echo
echo "✅ Commit organization complete!"
echo
echo "📊 Final status:"
git status --short | wc -l | xargs echo "   Remaining untracked files:"
echo
echo "💡 Next steps:"
echo "   1. Review remaining untracked files"
echo "   2. Update .gitignore as needed" 
echo "   3. Run: python scripts/hygiene_cleanup.py --clean"
echo "   4. Consider squashing related commits if needed"