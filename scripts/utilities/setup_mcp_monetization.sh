#!/bin/bash
# Setup script for Kindlemint MCP Monetization
set -e

echo "🚀 Setting up Kindlemint MCP Monetization System"
echo "================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "🐍 Python version: $python_version"

# Install MCP dependencies
echo "📦 Installing MCP dependencies..."
pip install -r requirements_mcp.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p books/mcp_generated
mkdir -p books/lead_magnets
mkdir -p data/monetization
mkdir -p logs

# Setup monetization system
echo "💰 Setting up monetization..."
python3 monetization_setup.py

# Test MCP server (in background)
echo "🧪 Testing MCP server..."
python3 mcp_server.py &
SERVER_PID=$!
sleep 3

# Kill test server
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🔧 Next Steps:"
echo "1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'"
echo "2. Start the MCP server: python3 mcp_server.py"
echo "3. In another terminal, run the host: python3 mcp_host_app.py"
echo "4. Try: 'Create a Sudoku book with 50 medium puzzles called Brain Teasers Vol 1'"
echo ""
echo "💰 Monetization:"
echo "1. Setup Gumroad products using data/monetization/setup_info.json"
echo "2. Configure Stripe webhooks for subscription billing"
echo "3. Deploy to a VPS for public access"
echo ""
echo "📊 Agent Marketplace Deployment:"
echo "1. Package as Docker container"
echo "2. Submit to aiagentstore.ai, Windsurf, etc."
echo "3. Market on Reddit, YouTube, IndieHackers"
echo ""
echo "🎯 Revenue Targets:"
echo "• Month 1: $500 (10 basic subscriptions)"
echo "• Month 2: $1,500 (20 basic + 10 pro)"  
echo "• Month 3: $3,000+ (40+ subscribers)"
echo ""
echo "Ready to make money with AI puzzle books! 🤖📚💰"