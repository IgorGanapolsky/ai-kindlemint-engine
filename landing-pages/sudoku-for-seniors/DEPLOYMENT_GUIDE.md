# 🚀 Deployment Guide - Sudoku for Seniors Landing Page

## Quick Deploy to AWS (Recommended)

### 1. Prerequisites
- [ ] AWS account (free tier eligible)
- [ ] Web3Forms account (free - 250 emails/month)
- [ ] Google Analytics account (free)
- [ ] Facebook Business account (free)
- [ ] Domain name (optional, can use CloudFront subdomain)

### 2. Deploy to AWS S3 + CloudFront

```bash
# Navigate to landing page
cd landing-pages/sudoku-for-seniors

# Install dependencies
npm install

# Build the static site
npm run build

# Upload to S3
aws s3 sync out/ s3://ai-kindlemint-landing/ --delete

# CloudFront URL will be available at:
# https://dvdyff0b2oove.cloudfront.net
```

### 3. Email Integration (Web3Forms)

Already configured with:
- **API Key**: 64ecaccd-8852-423b-a8a4-4ccd74b0f1a7
- **Free Tier**: 250 submissions/month
- **No additional setup needed**

### 4. PDF Hosting

Lead magnet already hosted at:
- **S3 URL**: https://kindlemint-pdfs-2025.s3.amazonaws.com/5-free-sudoku-puzzles.pdf
- **8 pages** with actual puzzles and solutions
- **No configuration needed**

### 5. Google Analytics Setup

1. Create new property: "Sudoku for Seniors"
2. Get Measurement ID (G-XXXXXXXXXX)
3. Add to environment variables
4. Verify in Real-Time reports

### 6. Facebook Pixel Setup

1. Business Manager > Events Manager
2. Create new Pixel: "Sudoku Landing Page"
3. Copy Pixel ID
4. Add to environment variables

### 7. Domain Configuration (Optional)

For custom domain (e.g., SudokuFor75Plus.com):

1. **Route 53** > Create Hosted Zone
2. Update DNS records:
   ```
   A Record: @ → CloudFront Distribution
   CNAME: www → CloudFront Domain
   ```

### 8. Post-Deployment Checklist

- [ ] Test email capture form
- [ ] Verify PDF download works
- [ ] Check Google Analytics tracking
- [ ] Verify Facebook Pixel fires
- [ ] Test on mobile devices
- [ ] Check page load speed (target < 3s)

## Local Development

```bash
# Install dependencies
npm install

# Create .env.local (copy from .env.example)
cp .env.example .env.local

# Run development server
npm run dev

# Open http://localhost:3000
```

## AWS Infrastructure

### S3 Buckets
- **Website**: ai-kindlemint-landing (static hosting)
- **PDFs**: kindlemint-pdfs-2025 (public read)

### CloudFront
- **Distribution**: EPU16LS0IGF5M
- **Domain**: https://dvdyff0b2oove.cloudfront.net
- **HTTPS**: Enabled
- **Cache**: Default settings

### Cost (Monthly)
- **S3**: $0.00 (free tier)
- **CloudFront**: $0.00 (free tier)
- **Route 53**: $0.50 (if using custom domain)
- **Total**: $0.00 - $0.50

## Traffic Generation (Week 1)

### Facebook Groups
1. Join 10 senior/puzzle groups
2. Share free puzzle weekly (not direct link)
3. Build relationships first

### Pinterest
1. Create account: "Large Print Puzzles"
2. Create boards:
   - "Brain Games for Seniors"
   - "Large Print Sudoku"
   - "Mental Exercise 75+"
3. Pin 5x daily with landing page link

### Reddit
- r/sudoku (150k members)
- r/puzzles (300k members)
- Share tips, not links

## Monitoring & Optimization

### Daily Checks
- Email subscribers (Web3Forms dashboard)
- Traffic (Google Analytics)
- Conversion rate (target: 25%+)

### Weekly Optimization
- A/B test headlines
- Try different lead magnet titles
- Test button colors/text

### Success Metrics
- Week 1: 50 subscribers
- Week 2: 150 subscribers
- Week 3: 300 subscribers
- Week 4: 500 subscribers

## Troubleshooting

### Emails not sending
- Check Web3Forms dashboard
- Verify API key matches
- Check spam folders

### PDF not downloading
- Verify S3 bucket policy
- Check CloudFront distribution
- Test direct S3 URL

### Low conversion rate
- Simplify form (fewer fields)
- Stronger headline
- Add urgency/scarcity

## Next Steps After Launch

1. **Week 1**: Focus on organic traffic
2. **Week 2**: Start Facebook ads ($5/day)
3. **Week 3**: Create email sequence
4. **Week 4**: Launch bundle offer

---

**Support**: If issues arise, check:
- AWS status: status.aws.amazon.com
- CloudFront logs in CloudWatch
- Debug locally first

**Remember**: The goal is 6,000 email subscribers for $300/day revenue!