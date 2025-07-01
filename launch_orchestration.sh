#!/bin/bash
# Launch script for KindleMint Orchestration System

echo "🚀 Starting KindleMint Performance Monitoring & Business Intelligence System"
echo "============================================================"
echo ""

# Check if required directories exist
if [ ! -d "books/performance_data" ]; then
    echo "📁 Creating performance data directory..."
    mkdir -p books/performance_data
fi

if [ ! -d "books/analytics_data" ]; then
    echo "📁 Creating analytics data directory..."
    mkdir -p books/analytics_data
fi

if [ ! -d "books/market_research" ]; then
    echo "📁 Creating market research directory..."
    mkdir -p books/market_research
fi

if [ ! -d "books/coordination_data" ]; then
    echo "📁 Creating coordination data directory..."
    mkdir -p books/coordination_data
fi

echo ""
echo "📊 Discovered Books Summary:"
echo "----------------------------"
# Quick check of active books
if [ -f "books/performance_data/active_books.json" ]; then
    book_count=$(cat books/performance_data/active_books.json | grep -c '"book_id"')
    echo "✓ Found $book_count books ready for monitoring"
else
    echo "⚠️  No active books file found yet - will auto-discover on startup"
fi

echo ""
echo "🤖 Starting Orchestration Agents:"
echo "---------------------------------"
echo "• KDP Performance Agent - Monitors book sales, BSR, reviews"
echo "• Business Analytics Agent - ROI calculations, financial reports"
echo "• Market Research Agent - Competitive analysis, market trends"
echo "• Automation Coordinator - Orchestrates all workflows"
echo ""
echo "⏰ Automated Workflows:"
echo "----------------------"
echo "• Hourly: Book performance monitoring"
echo "• Daily 2 AM: Comprehensive business analysis"
echo "• Weekly Sunday 3 AM: Deep market research"
echo "• Daily 11 PM: Executive summaries"
echo ""
echo "📝 Logs will be written to: orchestration_system.log"
echo ""
echo "Press Ctrl+C to stop the system"
echo "============================================================"
echo ""

# Launch the orchestration system
python -m kindlemint.orchestration_runner