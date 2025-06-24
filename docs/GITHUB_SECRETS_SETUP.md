# GitHub Secrets Setup Guide

This guide explains how to configure the required GitHub secrets for the KindleMint Engine automation workflows.

## Required Secrets

### 1. `SERPAPI_API_KEY` (Required for Market Research)
- **Purpose**: Fetches Amazon product data and competitor analysis
- **Get it from**: https://serpapi.com/
- **Pricing**: Free tier includes 100 searches/month
- **Setup**:
  1. Sign up at https://serpapi.com/users/sign_up
  2. Get your API key from https://serpapi.com/manage-api-key
  3. Add to GitHub: Settings → Secrets → Actions → New repository secret
  4. Name: `SERPAPI_API_KEY`
  5. Value: Your API key

### 2. `SENTRY_DSN` (Optional but Recommended)
- **Purpose**: Error tracking and monitoring
- **Get it from**: https://sentry.io/
- **Pricing**: Free tier includes 5k errors/month
- **Setup**:
  1. Sign up at https://sentry.io/signup/
  2. Create a new project (Python)
  3. Copy the DSN from project settings
  4. Add to GitHub: Settings → Secrets → Actions → New repository secret
  5. Name: `SENTRY_DSN`
  6. Value: Your DSN (format: `https://xxx@xxx.ingest.sentry.io/xxx`)

### 3. `SLACK_WEBHOOK_URL` (Optional)
- **Purpose**: Sends market research summaries to Slack
- **Get it from**: Your Slack workspace
- **Setup**:
  1. Go to https://api.slack.com/apps
  2. Create a new app → From scratch
  3. Add "Incoming Webhooks" feature
  4. Create webhook for your channel
  5. Add to GitHub: Settings → Secrets → Actions → New repository secret
  6. Name: `SLACK_WEBHOOK_URL`
  7. Value: Your webhook URL

## How to Add Secrets

1. Navigate to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**
5. Enter the secret name and value
6. Click **Add secret**

## Verifying Secrets

To verify secrets are properly configured:

1. Go to **Actions** tab
2. Click **Market Research Automation** workflow
3. Click **Run workflow** → **Run workflow**
4. Check the logs for successful API connections

## Security Best Practices

1. **Never commit secrets to code**
   - Use environment variables
   - Use `.env` files locally (add to `.gitignore`)

2. **Rotate keys regularly**
   - Update keys every 90 days
   - Remove unused keys

3. **Use least privilege**
   - Only grant necessary permissions
   - Use read-only keys where possible

## Troubleshooting

### "SERPAPI_API_KEY not found"
- Ensure the secret name is exactly `SERPAPI_API_KEY` (case-sensitive)
- Check you're in the correct repository
- Verify the secret has no extra spaces

### "Rate limit exceeded"
- SerpAPI free tier: 100 searches/month
- Consider upgrading or reducing search frequency
- The workflow includes retry logic with backoff

### "Sentry not initialized"
- This is a warning, not an error
- The workflow continues without error tracking
- Add `SENTRY_DSN` to enable monitoring

## Local Development

For local testing, create a `.env` file:

```bash
# .env (add to .gitignore)
SERPAPI_API_KEY=your_key_here
SENTRY_DSN=your_dsn_here
SLACK_WEBHOOK_URL=your_webhook_here
```

Then load in Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Workflow Triggers

The market research workflow runs:
- **Automatically**: Daily at 2 AM UTC
- **Manually**: Actions → Market Research Automation → Run workflow

## Cost Estimates

- **SerpAPI**: 
  - Free: 100 searches/month
  - Business: $50/month for 5,000 searches
  - Each workflow run uses ~10-20 searches

- **Sentry**:
  - Free: 5,000 errors/month
  - Team: $26/month for 50,000 errors

- **GitHub Actions**:
  - Free: 2,000 minutes/month
  - Each workflow run: ~5 minutes

## Next Steps

After setting up secrets:
1. Run the workflow manually to test
2. Check the pull request created with market insights
3. Review the `/research/YYYY-MM-DD/` folder for CSV data
4. Monitor Sentry dashboard for any errors

## Support

- **SerpAPI docs**: https://serpapi.com/search-api
- **Sentry docs**: https://docs.sentry.io/
- **GitHub Actions docs**: https://docs.github.com/en/actions