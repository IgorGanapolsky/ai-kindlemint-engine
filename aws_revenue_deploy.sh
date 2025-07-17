#!/bin/bash
# AWS Revenue Deployment - Uses your existing AWS resources

# Set credentials from environment (never hardcode)
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}"
export AWS_DEFAULT_REGION="us-east-1"

# Find your existing S3 bucket
BUCKET=$(aws s3 ls | grep -E "cloudfront|static|web" | head -1 | awk '{print $3}')
if [ -z "$BUCKET" ]; then
    BUCKET=$(aws s3 ls | head -1 | awk '{print $3}')
fi

echo "Using bucket: $BUCKET"

# Deploy revenue-generating pages
echo "📦 Deploying SEO money pages..."
aws s3 cp seo_free-large-print-sudoku-pdf.html s3://$BUCKET/puzzles/free-sudoku/index.html --content-type "text/html" --cache-control "max-age=3600"
aws s3 cp seo_printable-puzzles-for-dementia-patients.html s3://$BUCKET/puzzles/dementia/index.html --content-type "text/html" --cache-control "max-age=3600"
aws s3 cp seo_brain-games-for-seniors-printable.html s3://$BUCKET/puzzles/brain-games/index.html --content-type "text/html" --cache-control "max-age=3600"
aws s3 cp direct_sales_page.html s3://$BUCKET/puzzles/sale/index.html --content-type "text/html" --cache-control "max-age=3600"

# Deploy generated content
for file in generated_content/*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .md)
        # Convert markdown to HTML
        echo "<html><body>" > temp.html
        cat "$file" >> temp.html
        echo "<p><a href='https://dvdyff0b2oove.cloudfront.net'>Get Free Puzzles</a></p></body></html>" >> temp.html
        aws s3 cp temp.html s3://$BUCKET/content/$filename.html --content-type "text/html" --cache-control "max-age=3600"
        rm temp.html
    fi
done

# Create sitemap for SEO
cat > sitemap.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://dvdyff0b2oove.cloudfront.net/puzzles/free-sudoku/</loc></url>
  <url><loc>https://dvdyff0b2oove.cloudfront.net/puzzles/dementia/</loc></url>
  <url><loc>https://dvdyff0b2oove.cloudfront.net/puzzles/brain-games/</loc></url>
  <url><loc>https://dvdyff0b2oove.cloudfront.net/puzzles/sale/</loc></url>
</urlset>
EOF

aws s3 cp sitemap.xml s3://$BUCKET/sitemap.xml --content-type "application/xml"

# Invalidate CloudFront cache for immediate updates
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, '$BUCKET')].Id" --output text | head -1)
if [ ! -z "$DISTRIBUTION_ID" ]; then
    aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
    echo "✅ CloudFront cache invalidated"
fi

echo "✅ Revenue pages deployed!"
echo "🔗 Live URLs:"
echo "- https://dvdyff0b2oove.cloudfront.net/puzzles/free-sudoku/"
echo "- https://dvdyff0b2oove.cloudfront.net/puzzles/dementia/"
echo "- https://dvdyff0b2oove.cloudfront.net/puzzles/brain-games/"
echo "- https://dvdyff0b2oove.cloudfront.net/puzzles/sale/"
