#!/bin/bash

echo "🚀 Deploying Pay-Per-Crawl System to Vercel"
echo "=========================================="
echo ""

# Check if logged in to Vercel
if ! vercel whoami &>/dev/null; then
    echo "📝 Please log in to Vercel first:"
    vercel login
fi

echo "🔧 Pre-deployment checks..."

# Verify build works
echo "📦 Building project..."
npm run build || { echo "❌ Build failed!"; exit 1; }

echo ""
echo "✅ Build successful!"
echo ""

# Show what will be deployed
echo "📋 Deployment includes:"
echo "  ✓ AI Crawler Detection Middleware"
echo "  ✓ Pay-Per-Crawl Demo Page (/pay-per-crawl-demo)"
echo "  ✓ Analytics API (/api/crawler-analytics)"
echo "  ✓ Monetization robots.txt"
echo ""

# Deploy to production
echo "🚀 Deploying to production..."
vercel --prod

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📊 Next Steps:"
echo "1. Test human view: curl https://your-app.vercel.app/pay-per-crawl-demo"
echo "2. Test AI crawler: curl -H 'User-Agent: GPTBot' https://your-app.vercel.app/pay-per-crawl-demo"
echo "3. Check analytics: https://your-app.vercel.app/api/crawler-analytics"
echo ""
echo "💰 Start earning from AI crawlers!"