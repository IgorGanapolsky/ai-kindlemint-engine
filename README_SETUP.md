# AI KindleMint Engine - Complete Setup Guide

## Quick Start (15 Minutes)

### Step 1: Deploy to Replit
1. Fork this repository to your Replit account
2. The system will automatically install dependencies
3. Your Mission Control is ready to run

### Step 2: Configure API Keys
Add these secrets in Replit's Secrets tab:

**Required:**
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://aistudio.google.com)

**Optional (for real KDP publishing):**
- `KDP_EMAIL` - Your Amazon KDP login email
- `KDP_PASSWORD` - Your Amazon KDP password
- `GMAIL_USER` - Gmail for notifications
- `GMAIL_APP_PASSWORD` - Gmail app password
- `NOTIFICATION_EMAIL` - Email to receive notifications

### Step 3: Test Your First Book
```bash
python mission_control.py "My First AI Book"
```

Watch as the system generates:
- Complete book outline
- 7 full chapters
- Marketing strategy
- Blog posts
- Social media content
- KDP-ready .kpf file

**Generation time: ~2 minutes**

### Step 4: Start Automation Server
Click "Run" in Replit to start the webhook server.

Your automation endpoints will be live at:
- `https://your-replit-url.replit.app/run` - Generate books
- `https://your-replit-url.replit.app/publish` - Publish to KDP
- `https://your-replit-url.replit.app/status` - Check system status

## Advanced Configuration

### External Automation with Gumloop
1. Copy the `gumloop_config.yaml` settings
2. Create new Gumloop workflow
3. Set your Replit URL as webhook endpoint
4. Configure weekly book generation schedule

### Real KDP Publishing
1. Add KDP credentials to Replit secrets
2. Install Playwright browsers: `playwright install`
3. Test with: `python scripts/publish_to_kdp.py output/book.kpf`

### Email Notifications
1. Enable 2FA on Gmail
2. Generate app password
3. Add `GMAIL_USER` and `GMAIL_APP_PASSWORD` secrets
4. Receive notifications when books are published

## File Structure

```
mission_control/
├── mission_control.py          # Main orchestrator
├── webhook_server.py           # Automation server
├── start.sh                    # Quick launch script
├── publish_kdp.sh             # Publishing automation
├── agents/
│   ├── cto_agent.py           # Content creation
│   ├── cmo_agent.py           # Marketing
│   └── cfo_agent.py           # Analytics
├── scripts/
│   └── publish_to_kdp.py      # KDP automation
├── utils/
│   ├── file_manager.py        # File operations
│   └── logger.py              # Logging system
└── output/                    # Generated content
    ├── books/                 # Book manuscripts
    ├── marketing/             # Marketing content
    ├── logs/                  # Analytics
    └── *.kpf                  # KDP files
```

## Usage Examples

### Generate Single Book
```bash
python mission_control.py "Space Adventure for Kids"
```

### Run Specific Agent
```bash
python mission_control.py --agent cto "Mystery Story"
python mission_control.py --agent cmo "Educational Book"
```

### Check System Status
```bash
python mission_control.py --summary
```

### Webhook Triggers
```bash
# Generate book via API
curl -X POST https://your-url.replit.app/run \
  -H "Content-Type: application/json" \
  -d '{"topic": "Pirate Adventure"}'

# Publish latest book
curl -X POST https://your-url.replit.app/publish

# Check status
curl https://your-url.replit.app/status
```

## Monetization Strategies

### 1. Kindle Direct Publishing
- Upload .kpf files directly to Amazon KDP
- Price books at $2.99-$9.99
- Target: 70% royalty rate
- Expected: $2-7 per book sale

### 2. Content Marketing
- Use blog posts for SEO traffic
- Build email list with free books
- Upsell premium content
- Affiliate marketing opportunities

### 3. Social Media Growth
- Automated posting schedules
- Engagement content ready
- Build author platform
- Cross-promote multiple books

### 4. White Label Services
- Offer book creation services
- Package as done-for-you solution
- Target: $500-2000 per book project
- Scale with automation

## Troubleshooting

### Common Issues

**"ModuleNotFoundError"**
- Run: `pip install -r requirements.txt`

**"API Key Invalid"**
- Check Replit secrets configuration
- Verify key format and permissions

**"No .kpf files found"**
- Ensure CTO agent completes successfully
- Check output directory permissions

**"Webhook not responding"**
- Verify Replit domain is active
- Check port 5000 configuration

### Performance Optimization

**Faster Generation:**
- Use shorter book topics
- Reduce chapter count in prompts
- Optimize API rate limits

**Better Content Quality:**
- Provide detailed topic descriptions
- Use specific age ranges
- Include educational themes

**Higher Success Rates:**
- Monitor mission logs
- Track API usage
- Regular system health checks

## Support Resources

### Included Documentation
- Video walkthrough (link provided after purchase)
- Troubleshooting guide
- Best practices document
- Revenue optimization tips

### Community Access
- Private Discord server
- Monthly Q&A sessions
- Success story sharing
- Feature request discussions

### Direct Support
- Email support for 30 days
- Response time: 24-48 hours
- Setup assistance included
- Custom configuration help

## Legal & Compliance

### Content Rights
- All generated content is yours to use
- No attribution required
- Commercial use permitted
- Full publishing rights included

### Platform Compliance
- Amazon KDP terms compliant
- Content quality standards met
- No prohibited content generation
- Safe for commercial publishing

### Privacy & Security
- API keys stored securely
- No content sharing with third parties
- Local file processing
- GDPR compliant operations

---

**Need Help?** Contact support at: iganapolsky@gmail.com

**System Status:** All workflows operational
**Last Updated:** June 2025
**Version:** 1.0.0