#!/bin/bash

echo "🧹 Applying Code Hygiene Changes and Pushing to Main"
echo "==================================================="

# Make sure we're on main branch
echo "📌 Checking current branch..."
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "⚠️ Not on main branch. Switching to main..."
    git checkout main
    git pull origin main
fi

# Apply the changes to configuration files
echo "📝 Updating configuration files..."
mkdir -p config
mkdir -p .github/workflows

# Run the hygiene orchestrator
echo "🧹 Running hygiene analysis..."
python agents/code_hygiene_orchestrator.py analyze

echo "🧹 Running hygiene cleanup..."
python agents/code_hygiene_orchestrator.py clean --force

# Commit and push changes
echo "💾 Committing changes..."
git add .
git commit -m "🧹 Code hygiene: Cleanup repository structure

- Enable code hygiene orchestrator
- Update configuration
- Clean root directory
- Organize scripts and artifacts
- Setup automated weekly cleanup"

echo "🚀 Pushing to main..."
git push origin main

echo "✅ Done! Code hygiene changes applied and pushed to main."