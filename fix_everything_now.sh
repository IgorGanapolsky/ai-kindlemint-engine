#!/bin/bash
# FIX EVERYTHING NOW - GET TO MONEY FAST!

echo "🚨 AGGRESSIVE FIXES FOR IMMEDIATE REVENUE"
echo "========================================"

echo ""
echo "📌 STEP 1: BUY A DOMAIN (5 minutes)"
echo "Go to: https://www.namecheap.com"
echo "Search for these domains:"
echo "  - sudokuforseniors.com"
echo "  - seniorsudoku.com"
echo "  - largeprintpuzzles.com"
echo ""
echo "💰 Cost: $8.88/year (worth it for SEO!)"
echo ""

echo "📌 STEP 2: POINT DOMAIN TO CLOUDFRONT"
echo "In Namecheap DNS settings, add:"
echo "  Type: CNAME"
echo "  Host: www"
echo "  Value: dvdyff0b2oove.cloudfront.net"
echo ""

echo "📌 STEP 3: CREATE GUMROAD PRODUCTS NOW"
echo "Opening Gumroad..."
open "https://gumroad.com/signup"
echo ""
echo "Create these products:"
echo "1. FREE: 5 Sudoku Puzzles (Price: $0)"
echo "2. PAID: 100 Puzzle Pack (Price: $4.99)"
echo "3. PAID: Mega Bundle 500 Puzzles (Price: $19.99)"
echo ""

echo "📌 STEP 4: BUILD & DEPLOY LANDING PAGE"
cd landing-pages/sudoku-for-seniors
npm run build
echo "✅ Landing page built with auto-download fix!"
echo ""

echo "📌 STEP 5: DEPLOY TO S3"
aws s3 sync out/ s3://ai-kindlemint-landing/ --delete
aws cloudfront create-invalidation --distribution-id E3ANWS8X2YJF1V --paths "/*"
echo "✅ Deployed with immediate download + upsell!"
echo ""

echo "📌 STEP 6: TEST THE MONEY FLOW"
echo "1. Visit your landing page"
echo "2. Submit form"
echo "3. Verify auto-download works"
echo "4. See upsell page"
echo "5. Click upsell → Goes to Gumroad"
echo ""

echo "💰 EXPECTED REVENUE:"
echo "100 visitors → 50 signups → 5 sales = $25/day"
echo "Scale to 1000 visitors = $250/day = $7,500/month"
echo ""

echo "🎯 YOUR TODO LIST:"
echo "[ ] Buy domain on Namecheap (5 min)"
echo "[ ] Create 3 Gumroad products (10 min)"  
echo "[ ] Update Gumroad link in SimpleEmailCapture.tsx (2 min)"
echo "[ ] Run this script to deploy (5 min)"
echo "[ ] Post to Reddit/Facebook (10 min)"
echo ""
echo "TOTAL TIME: 32 minutes to revenue!"
echo ""
echo "⚡ STOP READING. START DOING. MONEY IS WAITING!"