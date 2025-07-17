#!/bin/bash
# Deploy revenue-generating content to S3 (using existing bucket)

# These files will generate revenue through SEO
aws s3 cp seo_free-large-print-sudoku-pdf.html s3://your-existing-bucket/puzzles/free-sudoku/index.html --content-type "text/html"
aws s3 cp seo_printable-puzzles-for-dementia-patients.html s3://your-existing-bucket/puzzles/dementia/index.html --content-type "text/html"
aws s3 cp seo_brain-games-for-seniors-printable.html s3://your-existing-bucket/puzzles/brain-games/index.html --content-type "text/html"
aws s3 cp direct_sales_page.html s3://your-existing-bucket/puzzles/sale/index.html --content-type "text/html"

# Make them public
aws s3api put-object-acl --bucket your-existing-bucket --key puzzles/free-sudoku/index.html --acl public-read
aws s3api put-object-acl --bucket your-existing-bucket --key puzzles/dementia/index.html --acl public-read
aws s3api put-object-acl --bucket your-existing-bucket --key puzzles/brain-games/index.html --acl public-read
aws s3api put-object-acl --bucket your-existing-bucket --key puzzles/sale/index.html --acl public-read

echo "✅ Revenue pages deployed to AWS!"
echo "These will start generating organic traffic and sales"
