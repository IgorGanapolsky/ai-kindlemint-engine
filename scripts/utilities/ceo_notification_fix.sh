#!/bin/bash
# CEO Notification Fix Script
# Run this to stop the email spam

echo "🔕 CEO Notification Fix"
echo "======================"
echo ""
echo "📧 Step 1: Open this link in your browser:"
echo "https://github.com/settings/notifications"
echo ""
echo "🔧 Step 2: Under 'Actions', change to:"
echo "   [✓] Only notify for failed workflows"
echo "   [ ] Include your own updates"
echo ""
echo "📱 Step 3: Download GitHub Mobile App:"
echo "   - iOS: https://apps.apple.com/app/github/id1477376905"
echo "   - Android: https://play.google.com/store/apps/details?id=com.github.android"
echo ""
echo "🚀 Step 4: Your CTO is consolidating workflows now..."
echo ""

# Show current PR status
echo "Current CI Status for PR #126:"
gh pr checks 126 2>/dev/null | head -10 || echo "Unable to fetch status"

echo ""
echo "✅ Once you update settings, you'll only get ~2-3 emails per day instead of 50+"
echo ""
echo "Press Enter when you've updated your notification settings..."
read -r

echo "🎉 Great! Your inbox should be much quieter now."