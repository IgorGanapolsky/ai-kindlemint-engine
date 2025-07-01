#!/bin/bash
# Emergency Cleanup Script for KindleMint

echo "🧹 Emergency Disk Space Cleanup for KindleMint"
echo "============================================="

PROJECT_ROOT="$(dirname "$(dirname "$0")")"

# Show current disk usage
echo "📊 Current Disk Usage:"
df -h /

# Clean up Python cache
echo -e "\n🗑️  Cleaning Python cache..."
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null
find "$PROJECT_ROOT" -name "*.pyo" -delete 2>/dev/null

# Clean up old logs (keep last 7 days)
echo -e "\n📜 Cleaning old logs..."
find "$PROJECT_ROOT/logs" -name "*.log" -mtime +7 -delete 2>/dev/null

# Clean up git objects
echo -e "\n🔧 Cleaning git repository..."
cd "$PROJECT_ROOT"
git gc --aggressive --prune=now

# Clean up node_modules if exists
if [ -d "$PROJECT_ROOT/node_modules" ]; then
    echo -e "\n📦 Removing node_modules..."
    rm -rf "$PROJECT_ROOT/node_modules"
fi

# Clean up old book generation artifacts
echo -e "\n📚 Cleaning old book artifacts..."
find "$PROJECT_ROOT/books" -name "*.pdf" -mtime +30 -delete 2>/dev/null
find "$PROJECT_ROOT/books" -name "*.epub" -mtime +30 -delete 2>/dev/null

# Clean up temp files
echo -e "\n🗑️  Cleaning temp files..."
find "$PROJECT_ROOT" -name ".DS_Store" -delete 2>/dev/null
find "$PROJECT_ROOT" -name "*.tmp" -delete 2>/dev/null

# Show results
echo -e "\n✅ Cleanup Complete!"
echo "📊 New Disk Usage:"
df -h /

# Calculate space saved
echo -e "\n💾 Space freed up!"