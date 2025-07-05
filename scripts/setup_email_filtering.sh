#!/bin/bash
# Script to help configure email filtering for GitHub bot notifications

echo "🔇 GitHub Bot Email Filter Setup"
echo "================================"
echo ""
echo "This script will help you stop bot email spam from your GitHub repository."
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Please install it first:"
    echo "   brew install gh"
    exit 1
fi

echo "📧 Step 1: GitHub Notification Settings"
echo "---------------------------------------"
echo "Opening GitHub notification settings in your browser..."
echo ""

# Open GitHub notification settings
open "https://github.com/settings/notifications" 2>/dev/null || \
xdg-open "https://github.com/settings/notifications" 2>/dev/null || \
echo "Please visit: https://github.com/settings/notifications"

echo "⚙️  Recommended settings:"
echo "  1. Under 'Actions':"
echo "     - UNCHECK 'Failed workflows only'"
echo "     - UNCHECK 'Send notifications for workflow runs'"
echo "  2. Under 'Watching':"
echo "     - Change to 'Participating and @mentions' (not 'All Activity')"
echo ""
echo "Press Enter when done..."
read

echo ""
echo "📧 Step 2: Repository Watch Settings"
echo "------------------------------------"
echo "Opening repository watch settings..."
echo ""

# Open repository watch settings
open "https://github.com/IgorGanapolsky/ai-kindlemint-engine/subscription" 2>/dev/null || \
xdg-open "https://github.com/IgorGanapolsky/ai-kindlemint-engine/subscription" 2>/dev/null || \
echo "Please visit: https://github.com/IgorGanapolsky/ai-kindlemint-engine/subscription"

echo "⚙️  Recommended: Choose 'Custom' and select only:"
echo "  - Issues (assigned, created, or mentioned)"
echo "  - Pull requests (assigned, created, or mentioned)"
echo "  - Releases"
echo ""
echo "Press Enter when done..."
read

echo ""
echo "🤖 Step 3: Bot-Specific Settings"
echo "---------------------------------"

# Add notification suppression to CodeRabbit config
if [ -f ".coderabbit.yml" ]; then
    echo "Adding email suppression to CodeRabbit config..."
    if ! grep -q "notifications:" .coderabbit.yml; then
        echo "" >> .coderabbit.yml
        echo "# Email notification settings" >> .coderabbit.yml
        echo "notifications:" >> .coderabbit.yml
        echo "  email: false" >> .coderabbit.yml
        echo "✅ CodeRabbit email notifications disabled"
    else
        echo "⚠️  CodeRabbit notifications section already exists"
    fi
else
    echo "⚠️  No .coderabbit.yml found"
fi

echo ""
echo "📱 Step 4: Gmail Filter (Optional)"
echo "----------------------------------"
echo "To create a Gmail filter that auto-archives bot emails:"
echo ""
echo "1. Go to Gmail Settings → Filters → Create new filter"
echo "2. In 'From' field, enter:"
echo "   *bot*@users.noreply.github.com OR github-actions@github.com"
echo "3. Click 'Create filter'"
echo "4. Check:"
echo "   - Skip the Inbox (Archive it)"
echo "   - Apply label: 'GitHub/Bots'"
echo "   - Also apply to matching conversations"
echo "5. Create filter"
echo ""

echo "✅ Setup Complete!"
echo ""
echo "You should now receive significantly fewer bot emails."
echo "You'll still get notifications for:"
echo "- Direct @mentions"
echo "- Issues/PRs assigned to you"
echo "- Your own comments and actions"
echo ""
echo "📖 For more details, see: docs/STOP_BOT_EMAILS.md"