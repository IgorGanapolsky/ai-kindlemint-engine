#!/bin/bash

echo "🚀 Deploying Max Smith KDP LLC Privacy Policy to CloudFront"
echo "=============================================="

# Create S3 bucket name
BUCKET_NAME="maxsmithkdp-privacy-policy"
REGION="us-east-1"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first"
    exit 1
fi

# Create S3 bucket
echo "📦 Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"

# Configure bucket for static website hosting
echo "🌐 Configuring static website hosting..."
aws s3 website s3://$BUCKET_NAME \
    --index-document index.html \
    --error-document error.html

# Upload privacy policy
echo "📤 Uploading privacy policy..."
aws s3 cp index.html s3://$BUCKET_NAME/index.html \
    --acl public-read \
    --content-type "text/html"

# Create bucket policy for public access
echo "🔓 Setting bucket policy..."
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json
rm bucket-policy.json

# Create CloudFront distribution
echo "☁️  Creating CloudFront distribution..."
DISTRIBUTION_CONFIG=$(cat <<EOF
{
    "CallerReference": "maxsmithkdp-privacy-$(date +%s)",
    "Comment": "Max Smith KDP LLC Privacy Policy",
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$BUCKET_NAME.s3-website-$REGION.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000
    },
    "Enabled": true
}
EOF
)

# Create distribution
DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config "$DISTRIBUTION_CONFIG" \
    --query 'Distribution.Id' \
    --output text 2>/dev/null || echo "Using existing distribution")

if [ "$DISTRIBUTION_ID" != "Using existing distribution" ]; then
    echo "✅ CloudFront distribution created: $DISTRIBUTION_ID"
    
    # Get CloudFront domain
    CLOUDFRONT_URL=$(aws cloudfront get-distribution \
        --id $DISTRIBUTION_ID \
        --query 'Distribution.DomainName' \
        --output text)
    
    echo ""
    echo "🎉 Privacy Policy deployed successfully!"
    echo "CloudFront URL: https://$CLOUDFRONT_URL"
    echo ""
    echo "📌 Use this URL for Pinterest:"
    echo "https://$CLOUDFRONT_URL"
else
    # Find existing distribution
    EXISTING_DIST=$(aws cloudfront list-distributions \
        --query "DistributionList.Items[?Comment=='Max Smith KDP LLC Privacy Policy'].{Id:Id,Domain:DomainName}" \
        --output json | jq -r '.[0]')
    
    if [ "$EXISTING_DIST" != "null" ]; then
        DIST_ID=$(echo $EXISTING_DIST | jq -r '.Id')
        DOMAIN=$(echo $EXISTING_DIST | jq -r '.Domain')
        echo ""
        echo "📌 Existing privacy policy found:"
        echo "https://$DOMAIN"
        
        # Invalidate cache to update content
        echo "🔄 Updating content..."
        aws cloudfront create-invalidation \
            --distribution-id $DIST_ID \
            --paths "/*" > /dev/null
    fi
fi

echo ""
echo "📝 Pinterest Setup Instructions:"
echo "1. Go to Pinterest Developer Dashboard"
echo "2. When asked for privacy policy URL, use the CloudFront URL above"
echo "3. Complete the API access request"
echo ""