#!/bin/bash

echo "🤖 Cloudflare Pay-Per-Crawl Setup Script"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Prerequisites:${NC}"
echo "1. Cloudflare account (free tier is fine)"
echo "2. Your domain added to Cloudflare"
echo "3. API token from Cloudflare dashboard"
echo ""

echo -e "${YELLOW}🚀 Step 1: Sign up for Pay-Per-Crawl${NC}"
echo "Visit: https://www.cloudflare.com/paypercrawl-signup/"
echo "Press Enter when you've signed up..."
read

echo -e "${YELLOW}🔧 Step 2: Install dependencies${NC}"
cd landing-pages/sudoku-for-seniors
npm install @cloudflare/paypercrawl-js

echo -e "${YELLOW}🔑 Step 3: Configure environment variables${NC}"
echo "Add these to your .env.local file:"
echo ""
echo "CLOUDFLARE_API_TOKEN=your_token_here"
echo "CLOUDFLARE_ZONE_ID=your_zone_id_here"
echo "PAYPERCRAWL_ENABLED=true"
echo ""

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    cat > .env.local << EOF
# Cloudflare Pay-Per-Crawl Configuration
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ZONE_ID=
PAYPERCRAWL_ENABLED=true
NEXT_PUBLIC_PAYPERCRAWL_ENABLED=true

# Pricing Configuration (in USD)
PAYPERCRAWL_PRICE_BASIC=0.05
PAYPERCRAWL_PRICE_PREMIUM=0.25
EOF
    echo -e "${GREEN}✅ Created .env.local file${NC}"
else
    echo -e "${YELLOW}⚠️  .env.local already exists - please add the variables manually${NC}"
fi

echo -e "${YELLOW}📝 Step 4: Configure Cloudflare Rules${NC}"
echo "In Cloudflare Dashboard > Your Domain > Rules > Page Rules:"
echo ""
echo "1. Create rule: *.ai-kindlemint-engine.com/*"
echo "   - Enable Pay-Per-Crawl"
echo "   - Set pricing tier"
echo ""

echo -e "${YELLOW}🧪 Step 5: Test the implementation${NC}"
echo "1. Start your dev server: npm run dev"
echo "2. Visit: http://localhost:3000/pay-per-crawl-demo"
echo "3. Test with crawler user agent:"
echo ""
echo "   curl -H 'User-Agent: GPTBot' http://localhost:3000/pay-per-crawl-demo"
echo ""

echo -e "${YELLOW}📊 Step 6: Monitor earnings${NC}"
echo "Check analytics at: http://localhost:3000/api/crawler-analytics"
echo ""

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Deploy to production"
echo "2. Update all book preview pages with PayPerCrawlContent component"
echo "3. Monitor crawler traffic and optimize pricing"
echo "4. Count passive income! 💰"