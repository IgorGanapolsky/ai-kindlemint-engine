#!/bin/bash
# Setup automated code hygiene for ai-kindlemint-engine

set -e

echo "🧹 Setting up Automated Code Hygiene..."
echo "======================================="

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip install pre-commit
fi

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/git-hooks/pre-commit-hygiene.py
chmod +x agents/code_hygiene_orchestrator.py

# Run initial hygiene check
echo "🔍 Running initial hygiene analysis..."
python agents/code_hygiene_orchestrator.py analyze

# Enable GitHub Action
echo "✅ GitHub Action 'automated-hygiene-enforcement.yml' has been created"
echo "   It will run on all pull requests to enforce hygiene standards"

# Create git alias for manual hygiene check
git config alias.hygiene '!python agents/code_hygiene_orchestrator.py analyze'
git config alias.clean-hygiene '!python agents/code_hygiene_orchestrator.py clean --interactive'

echo ""
echo "✅ Hygiene automation setup complete!"
echo ""
echo "📋 What's been configured:"
echo "   - Pre-commit hooks for local hygiene checks"
echo "   - GitHub Action for PR hygiene enforcement"
echo "   - Hygiene rules in config/hygiene_rules.json"
echo "   - Git aliases: 'git hygiene' and 'git clean-hygiene'"
echo ""
echo "🚀 Next steps:"
echo "   1. Commit these changes"
echo "   2. Push to trigger the GitHub Action"
echo "   3. Pre-commit hooks will run automatically on each commit"
echo ""
echo "💡 Tips:"
echo "   - Run 'git hygiene' to manually check hygiene"
echo "   - Run 'git clean-hygiene' to interactively fix issues"
echo "   - Configure rules in config/hygiene_rules.json"
echo "   - Skip hooks with 'git commit --no-verify' (use sparingly!)"