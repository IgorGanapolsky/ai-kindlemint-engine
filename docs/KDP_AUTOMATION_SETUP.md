# KDP Automation Engine Setup Guide

## 🚀 Quick Setup (3 steps)

### Step 1: Get API Keys

**Required APIs:**
1. **Helium 10** ($99/month): https://www.helium10.com/pricing
   - Sign up → Dashboard → API → Generate API Key
   
2. **Jungle Scout** ($49/month): https://www.junglescout.com/pricing  
   - Sign up → Settings → API → Create API Key

**Optional APIs:**
3. **Amazon Product API** (Free): https://webservices.amazon.com/paapi5/
   - Join Amazon Associates → Get API credentials

### Step 2: Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required fields in .env:**
```bash
HELIUM10_API_KEY=your_actual_key_here
JUNGLE_SCOUT_API_KEY=your_actual_key_here
KDP_EMAIL=your_kdp_email@example.com
KDP_PASSWORD=your_kdp_password
```

### Step 3: Run Automation

```bash
# Install dependencies
pip install selenium requests aiohttp

# Run niche discovery only (no publishing)
python src/kindlemint/automation/kdp_automation_engine.py --mode discover

# Run full automation (discover + publish)
python src/kindlemint/automation/kdp_automation_engine.py --mode full --max-books 1
```

## 💰 Cost Breakdown

- **Helium 10**: $99/month (keyword research)
- **Jungle Scout**: $49/month (sales estimates) 
- **Total**: $148/month for full automation

## 🆓 Free Alternative (Manual Mode)

If you don't want to pay for APIs, you can:

1. **Manual niche research**: Use free tools like Google Trends
2. **Use existing book templates**: Generate books with current system
3. **Manual KDP upload**: Skip browser automation

```bash
# Generate book with existing system
python scripts/generate_book.py

# Manual upload to KDP dashboard
```

## 🔧 Environment Variables

**Copy to your `.env` file:**

```bash
# Required for automation
HELIUM10_API_KEY=your_key_here
JUNGLE_SCOUT_API_KEY=your_key_here

# Required for KDP upload
KDP_EMAIL=your_kdp_email@example.com  
KDP_PASSWORD=your_kdp_password

# Optional
AMAZON_ACCESS_KEY=your_amazon_key
AMAZON_SECRET_KEY=your_amazon_secret
AMAZON_PARTNER_TAG=your_amazon_tag

# Browser settings
HEADLESS_BROWSER=true
```

## 🎯 Usage Examples

```bash
# Just discover profitable niches
python src/kindlemint/automation/kdp_automation_engine.py --mode discover

# Publish one book to top niche
python src/kindlemint/automation/kdp_automation_engine.py --mode publish

# Full automation: discover + publish 3 books
python src/kindlemint/automation/kdp_automation_engine.py --mode full --max-books 3

# Custom keywords
python src/kindlemint/automation/kdp_automation_engine.py --mode discover --keywords "sudoku" "crossword" "word search"
```

## ⚠️ Important Notes

1. **Chrome Driver**: Selenium requires Chrome browser installed
2. **Rate Limits**: System waits 5 minutes between uploads
3. **KDP Review**: Books need Amazon approval (24-72 hours)
4. **API Costs**: Monitor your API usage to avoid overages

## 🛠️ Troubleshooting

**Missing API Keys Error:**
```bash
❌ Automation failed: Missing required API keys: ['helium10_api_key']
```
→ Add the missing keys to your `.env` file

**Chrome Driver Error:**
```bash
❌ Chrome driver not found
```
→ Install Chrome browser: https://www.google.com/chrome/

**KDP Login Failed:**
```bash
❌ KDP login failed
```
→ Check KDP_EMAIL and KDP_PASSWORD in `.env`