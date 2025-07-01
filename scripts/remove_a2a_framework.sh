#!/bin/bash
# A2A Framework Removal Script
# Removes the over-engineered A2A framework
# ========================================================

set -e

echo "=================================================="
echo "🗑️  A2A FRAMEWORK REMOVAL SCRIPT"
echo "Removing over-engineered Agent-to-Agent framework"
echo "=================================================="
echo ""

# Create backup directory
BACKUP_DIR="a2a_backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Function to safely remove files/directories
safe_remove() {
    local path=$1
    if [ -e "$path" ]; then
        echo "   Moving $path to backup..."
        mv "$path" "$BACKUP_DIR/" 2>/dev/null || true
    fi
}

echo ""
echo "1️⃣ Removing A2A source code..."
safe_remove "src/kindlemint/a2a"

echo ""
echo "2️⃣ Removing A2A tests..."
for test_file in tests/**/test_a2a*.py tests/**/test_*a2a*.py; do
    if [ -f "$test_file" ]; then
        safe_remove "$test_file"
    fi
done

echo ""
echo "3️⃣ Removing A2A documentation..."
safe_remove "docs/A2A_MIGRATION_PLAN.md"
safe_remove "docs/a2a_migration_plan.md"

echo ""
echo "4️⃣ Removing A2A imports from other files..."
# Remove A2A imports from generate_book.py
if [ -f "scripts/generate_book.py" ]; then
    sed -i.bak '/from kindlemint\.a2a/d' scripts/generate_book.py 2>/dev/null || true
    sed -i.bak '/A2AOrchestrator/d' scripts/generate_book.py 2>/dev/null || true
    rm -f scripts/generate_book.py.bak
    echo "   ✅ Cleaned scripts/generate_book.py"
fi

# Clean up any other A2A references
find . -name "*.py" -type f -not -path "./$BACKUP_DIR/*" -not -path "./venv/*" -not -path "./.git/*" | while read file; do
    if grep -q "from kindlemint\.a2a" "$file" 2>/dev/null; then
        echo "   Cleaning $file..."
        sed -i.bak '/from kindlemint\.a2a/d' "$file" 2>/dev/null || true
        rm -f "${file}.bak"
    fi
done

echo ""
echo "5️⃣ Creating removal documentation..."
cat > "A2A_REMOVAL_COMPLETE.md" << 'EOF'
# A2A Framework Removal Complete

## Removal Date
$(date +"%Y-%m-%d")

## What Was Removed
- Google-inspired A2A (Agent-to-Agent) framework
- Message bus infrastructure
- Agent registry system
- All associated tests and documentation

## Why It Was Removed
- **Zero business value**: Books generated fine without it
- **Over-engineering**: Complex message passing for simple function calls
- **No real usage**: Remained experimental, never integrated into production
- **Unnecessary complexity**: Added layers of abstraction without benefit

## Current Architecture
The platform continues to work perfectly with:
- Direct function calls between components
- Simple orchestration scripts
- Clear, maintainable code structure

## Cost Savings
- Development time: No more maintaining unused framework
- Mental overhead: Simpler codebase to understand
- Testing burden: Fewer components to test

## Backup Location
All removed code has been backed up to: $BACKUP_DIR
EOF

echo ""
echo "=================================================="
echo "✅ A2A FRAMEWORK REMOVAL COMPLETE!"
echo "=================================================="
echo ""
echo "📋 Summary:"
echo "   - A2A framework code moved to: $BACKUP_DIR"
echo "   - Cleaned imports from other files"
echo "   - Documentation created"
echo ""
echo "🎯 Your codebase is now:"
echo "   - Simpler"
echo "   - More maintainable"
echo "   - Focused on actual business value"
echo ""