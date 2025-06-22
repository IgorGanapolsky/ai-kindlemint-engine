# ECR Lifecycle Policy Setup

## Overview
Automated cleanup policy to keep ECR costs within AWS Free Tier limits (500 MB storage/month).

## Files Created
- `ecr-lifecycle-policy.json` - Lifecycle policy configuration
- `apply-ecr-lifecycle-policy.sh` - Script to apply policy to ECR repository

## Policy Rules
1. **Untagged images**: Deleted after 1 day
2. **Tagged images**: Keep only last 10 versions  
3. **Tagged images**: Deleted after 30 days

## Setup Instructions

### 1. Ensure AWS Authentication
```bash
aws sso login
```

### 2. Create ECR Repository (if needed)
```bash
# Option A: Create repository directly
aws ecr create-repository --repository-name kindlemint-v3-kdp-publisher --region us-east-1

# Option B: Use existing deployment script (creates repo if needed)
./infrastructure/deploy-v3.sh
```

### 3. Apply Lifecycle Policy
```bash
./infrastructure/apply-ecr-lifecycle-policy.sh
```

## Cost Impact
- **Before**: Unlimited image storage (potential costs)
- **After**: Maximum ~30 days of images + 10 versions
- **Free Tier**: 500 MB storage/month for 12 months

## Monitoring
Check repository status:
```bash
aws ecr describe-images --repository-name kindlemint-v3-kdp-publisher --region us-east-1
```

## Next Steps
1. Run `aws sso login` to authenticate
2. Execute `./infrastructure/apply-ecr-lifecycle-policy.sh`
3. Monitor ECR usage in AWS Console → Free Tier dashboard