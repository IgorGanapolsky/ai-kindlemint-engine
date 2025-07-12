#!/bin/bash

echo "🚀 Traffic Generation Setup Script"
echo "================================="
echo ""
echo "This script will help you set up the traffic generation system"
echo "to drive 1000+ daily visitors to your landing page."
echo ""
echo "📋 Prerequisites:"
echo "1. Reddit account and API credentials"
echo "2. Pinterest developer account"
echo "3. Facebook account and Chrome browser"
echo ""

# Check if config files exist
if [ ! -f "reddit_config.json" ]; then
    echo "📝 Creating reddit_config.json from template..."
    cp reddit_config.json.template reddit_config.json
    echo "   ✅ Please edit reddit_config.json with your credentials"
    echo "   👉 Get Reddit API at: https://www.reddit.com/prefs/apps"
    echo ""
fi

if [ ! -f "pinterest_config.json" ]; then
    echo "📝 Creating pinterest_config.json from template..."
    cp pinterest_config.json.template pinterest_config.json
    echo "   ✅ Please edit pinterest_config.json with your credentials"
    echo "   👉 Get Pinterest API at: https://developers.pinterest.com/"
    echo ""
fi

if [ ! -f "facebook_config.json" ]; then
    echo "📝 Creating facebook_config.json from template..."
    cp facebook_config.json.template facebook_config.json
    echo "   ✅ Please edit facebook_config.json with your Chrome profile path"
    echo "   👉 Find path at: chrome://version/ -> Profile Path"
    echo ""
fi

if [ ! -f "traffic_orchestrator_config.json" ]; then
    echo "📝 Creating traffic_orchestrator_config.json from template..."
    cp traffic_orchestrator_config.json.template traffic_orchestrator_config.json
    echo "   ✅ Configuration ready with default schedule"
    echo ""
fi

echo "🎯 Revenue Goal: $300/day"
echo "📊 Traffic Target: 1000 visitors/day"
echo "🌐 Landing Page: https://dvdyff0b2oove.cloudfront.net"
echo ""
echo "⚠️  IMPORTANT ACTIONS:"
echo "1. Update Gumroad price from $14.99 to $4.99"
echo "2. Configure all API credentials in the config files"
echo "3. Test each component individually before running orchestrator"
echo ""
echo "📚 Next Steps:"
echo "1. Edit all config files with your credentials"
echo "2. Test Reddit: python3 reddit_organic_poster.py"
echo "3. Test Pinterest: python3 pinterest_pin_scheduler.py"
echo "4. Test Facebook: python3 facebook_group_engager.py"
echo "5. Run full system: python3 traffic_orchestrator.py"
echo ""
echo "💡 Monitor email captures with:"
echo 'JSON.parse(localStorage.getItem("sudoku_subscribers"))'
echo ""
echo "Good luck reaching $300/day! 🚀"