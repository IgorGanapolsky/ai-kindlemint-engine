#!/bin/bash

echo "🧹 Running Aggressive Root Directory Cleanup"
echo "==========================================="

# Make the script executable
chmod +x scripts/aggressive_root_cleanup.py

# Run the aggressive cleanup
python scripts/aggressive_root_cleanup.py

# Commit the changes
echo "💾 Committing changes..."
git add .
git commit -m "🧹 Aggressive root directory cleanup

- Moved Python scripts to scripts/utilities
- Moved shell scripts to scripts/utilities
- Moved HTML files to docs/templates
- Moved Markdown files to docs/checklists
- Moved config files to config directory
- Organized key files in config/keys"

echo "✅ Done! Root directory has been aggressively cleaned up."
echo "🚀 To push these changes, run: git push origin main"