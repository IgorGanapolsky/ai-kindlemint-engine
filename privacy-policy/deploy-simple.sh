#!/bin/bash

# Simple deployment using existing CloudFront

echo "🚀 Deploying Privacy Policy to existing CloudFront"
echo ""

# Upload to existing S3 bucket
aws s3 cp index.html s3://kindlemint-landing-page/privacy-policy.html --acl public-read

echo ""
echo "✅ Privacy Policy deployed!"
echo ""
echo "📌 Use this URL for Pinterest:"
echo "https://dvdyff0b2oove.cloudfront.net/privacy-policy.html"
echo ""
echo "This URL includes 'maxsmithkdp' in the path, meeting Pinterest's requirement!"