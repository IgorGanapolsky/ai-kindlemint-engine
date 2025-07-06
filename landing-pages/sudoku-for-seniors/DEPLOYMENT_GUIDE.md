# 🚀 Deployment Guide - Sudoku for Seniors Landing Page

## Quick Deploy to Vercel (Recommended)

### 1. Prerequisites
- [ ] Vercel account (free at vercel.com)
- [ ] ConvertKit account ($29/month)
- [ ] Google Analytics account (free)
- [ ] Facebook Business account (free)
- [ ] Domain name (optional, can use Vercel subdomain)

### 2. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to landing page
cd landing-pages/sudoku-for-seniors

# Install dependencies
npm install

# Deploy
vercel
```

Follow prompts:
- Select "Create new project"
- Name: `sudoku-for-seniors`
- Framework: Next.js
- Build command: `npm run build`
- Output directory: `.next`

### 3. Environment Variables

In Vercel Dashboard > Settings > Environment Variables, add:

```
CONVERTKIT_API_KEY=your_api_key_here
CONVERTKIT_FORM_ID=your_form_id_here
GA_MEASUREMENT_ID=G-XXXXXXXXXX
FB_PIXEL_ID=XXXXXXXXXXXXXXXXX
```

### 4. ConvertKit Setup

1. **Create Form**:
   - Login to ConvertKit
   - Forms > New Form > "Sudoku Lead Magnet"
   - Copy Form ID

2. **Create Automation**:
   - Automations > New Automation
   - Trigger: "Joins Form" (Sudoku Lead Magnet)
   - Action: "Send Email" with lead magnet download link

3. **Upload Lead Magnet**:
   - Use ConvertKit's file hosting or upload to:
     - Dropbox
     - Google Drive (public link)
     - Your Vercel deployment (`/downloads/`)

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

1. **Vercel Dashboard** > Settings > Domains
2. Add domain
3. Update DNS records:
   ```
   A Record: @ → 76.76.21.21
   CNAME: www → cname.vercel-dns.com
   ```

### 8. Post-Deployment Checklist

- [ ] Test email capture form
- [ ] Verify lead magnet delivery
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

# Add your API keys to .env.local

# Run development server
npm run dev

# Open http://localhost:3000
```

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
- Email subscribers (ConvertKit)
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
- Check ConvertKit API key
- Verify form ID matches
- Check automation is active

### Analytics not tracking
- Verify IDs in env variables
- Check ad blockers
- Use GA DebugView

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
- Vercel status: status.vercel.com
- ConvertKit status: status.convertkit.com
- Debug locally first

**Remember**: The goal is 6,000 email subscribers for $300/day revenue!