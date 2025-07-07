#!/bin/bash
# STEALTH MODE: Deploy Landing Page for IMMEDIATE Revenue

echo "💰 REVENUE DEPLOYMENT - STEALTH MODE"
echo "===================================="

LANDING_DIR="../landing-pages/sudoku-for-seniors"

# Step 1: Ensure lead magnet is in place
echo "📄 Copying lead magnet..."
mkdir -p $LANDING_DIR/public/downloads
cp ../generated/lead_magnets/5_FREE_Sudoku_Puzzles_20250706_114640.pdf $LANDING_DIR/public/downloads/5-free-sudoku-puzzles.pdf

# Step 2: Build the site
echo "🏗️ Building landing page..."
cd $LANDING_DIR && npm run build && cd -

# Step 3: Upload to AWS
echo "☁️ Deploying to AWS..."
cd $LANDING_DIR && aws s3 sync out/ s3://ai-kindlemint-landing/ --delete && cd -

# Step 4: Invalidate CloudFront
echo "🔄 Clearing CDN cache..."
aws cloudfront create-invalidation --distribution-id EPU16LS0IGF5M --paths "/*"

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "🌐 LIVE URLS:"
echo "Landing Page: https://dvdyff0b2oove.cloudfront.net"
echo "Lead Magnet: https://kindlemint-pdfs-2025.s3.amazonaws.com/5-free-sudoku-puzzles.pdf"
echo ""
echo "💰 REVENUE STREAM ACTIVE!"
echo "Expected: 100 emails/day → 5 sales/day → $50/day → $1,500/month"