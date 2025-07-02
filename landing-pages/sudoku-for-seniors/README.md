# Sudoku for Seniors 75+ Landing Page

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd landing-pages/sudoku-for-seniors
npm install
```

### 2. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env.local

# Edit .env.local with your actual values:
# - Leave ConvertKit blank for now (we'll add after signup)
# - Leave GA and FB Pixel blank for now
```

### 3. Run Development Server

```bash
npm run dev
```

Open http://localhost:3000 to see your landing page!

## 📝 Step-by-Step Deployment

### Step 1: Test Locally First
1. Make sure the page loads
2. Test the email form (it will error without ConvertKit, that's OK)
3. Check mobile responsiveness

### Step 2: Deploy to Vercel (Free)

```bash
# Install Vercel CLI if you haven't
npm i -g vercel

# Deploy (answer the prompts)
vercel

# Prompts:
# - Set up and deploy: Y
# - Which scope: (select your account)
# - Link to existing project: N
# - Project name: sudoku-for-seniors
# - Directory: ./ (current directory)
# - Override settings: N
```

You'll get a URL like: https://sudoku-for-seniors-abc123.vercel.app

### Step 3: ConvertKit Setup ($29/month)

1. **Sign up**: https://convertkit.com
2. **Create a Form**:
   - Forms → Create New → "Sudoku Lead Magnet"
   - Type: Inline
   - Save and get Form ID (in the URL or settings)
3. **Get API Key**:
   - Account Settings → Advanced → API Key
4. **Add to Vercel**:
   - Go to your Vercel dashboard
   - Select your project
   - Settings → Environment Variables
   - Add:
     - `CONVERTKIT_API_KEY` = your-api-key
     - `CONVERTKIT_FORM_ID` = your-form-id
   - Redeploy for changes to take effect

### Step 4: Upload Lead Magnet

The PDF is already generated at:
`public/downloads/5-free-sudoku-puzzles.pdf`

Options:
1. **Use Vercel hosting** (easiest):
   - It's already available at: your-site.vercel.app/downloads/5-free-sudoku-puzzles.pdf
2. **Upload to ConvertKit**:
   - In your form settings, add as "Incentive"
3. **Use Dropbox/Google Drive**:
   - Upload and get public link

### Step 5: Create Email Automation

In ConvertKit:
1. Automations → New Automation
2. Trigger: "Joins form: Sudoku Lead Magnet"
3. Add Email:
   - Subject: "Your FREE Sudoku Puzzles are here!"
   - Body: Include download link
   - Send immediately

## 🎯 First Week Goals

### Day 1: Deploy
- [ ] Get site live on Vercel
- [ ] ConvertKit connected
- [ ] Test email capture works

### Day 2-3: Traffic
- [ ] Join 5 Facebook groups
- [ ] Create Pinterest account
- [ ] Share first helpful post (no links yet)

### Day 4-7: Optimize
- [ ] Get first 10 subscribers
- [ ] Track conversion rate
- [ ] A/B test headline

## 🔧 Troubleshooting

### "Module not found" errors
```bash
rm -rf node_modules package-lock.json
npm install
```

### ConvertKit not working
- Check API key has no extra spaces
- Verify Form ID is correct
- Check Vercel logs for errors

### No traffic
- Don't share direct links in groups (spam)
- Provide value first, mention site naturally
- Use Pinterest for direct linking

## 📊 Success Metrics

| Day | Visitors | Subscribers | Conversion Rate |
|-----|----------|-------------|-----------------|
| 1   | 10       | 2           | 20%             |
| 3   | 50       | 12          | 24%             |
| 7   | 200      | 50          | 25%             |

## 🚀 Ready to Launch?

1. Run `npm run build` to check for errors
2. Deploy with `vercel --prod`
3. Share your live URL in ONE Facebook group
4. Watch the subscribers come in!

Remember: **Done is better than perfect**. Launch today, optimize tomorrow!

---

**Need help?** The landing page is designed to work even without all integrations. Get it live first, add features as you go!