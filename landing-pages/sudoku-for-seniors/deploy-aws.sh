#!/bin/bash
# AWS Deployment Script for Sudoku Landing Page

echo "🚀 Deploying to AWS S3 + CloudFront..."

# Build the static site
echo "📦 Building Next.js static site..."
npm run build

# Check if build succeeded
if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Upload to S3
echo "☁️ Uploading to S3..."
aws s3 sync out/ s3://ai-kindlemint-landing/ --delete

# Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
aws cloudfront create-invalidation --distribution-id EPU16LS0IGF5M --paths "/*"

echo "✅ Deployment complete!"
echo "🌐 Site available at: https://dvdyff0b2oove.cloudfront.net"
echo "📄 PDF available at: https://kindlemint-pdfs-2025.s3.amazonaws.com/5-free-sudoku-puzzles.pdf"