# AWS Migration Checklist

## ✅ Completed
- [x] Create S3 bucket for website hosting (ai-kindlemint-landing)
- [x] Create S3 bucket for PDF hosting (kindlemint-pdfs-2025)
- [x] Configure buckets for public access
- [x] Upload landing page to S3
- [x] Test S3 website works

## 🔄 In Progress
- [ ] Create proper PDF with actual Sudoku puzzles (current is empty)
- [ ] Set up CloudFront for HTTPS
- [ ] Update DNS to point to CloudFront

## ❌ To Do
- [ ] Remove all Vercel configurations from repo
- [ ] Delete Vercel project
- [ ] Update all documentation to reference AWS URLs
- [ ] Set up GitHub Actions for AWS deployment
- [ ] Create deployment script for S3
- [ ] Set up monitoring with CloudWatch

## 🚨 Critical Issues
1. **PDF is empty** - only 2 pages, no actual puzzles
2. **No HTTPS** - showing "Not Secure" warning
3. **Domain still on Vercel** - need DNS update

## 💵 Cost Estimate (Monthly)
- S3 Storage: $0.00 (under 5GB free tier)
- S3 Requests: $0.00 (under 20k free tier)
- CloudFront: $0.00 (under 1TB free tier)
- Route 53: $0.50 (not free)
- **Total: $0.50/month**

## 🔧 Next Steps
1. Create real PDF with 5 Sudoku puzzles
2. Set up CloudFront distribution
3. Update Route 53/DNS
4. Remove Vercel completely