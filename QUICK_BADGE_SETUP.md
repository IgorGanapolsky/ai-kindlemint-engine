# 🚀 Quick Badge Setup - 5 Minutes

## Current Status
✅ **License**: Now showing MIT (forced GitHub to detect it)
✅ **Badges Added**: SonarCloud and Codecov badges are now in README
⚠️ **Services**: Need tokens to display actual data

## To Make Badges Work:

### 1. Codecov (2 minutes)
```bash
# Visit: https://app.codecov.io/gh
# Click: "Add new repository"
# Select: IgorGanapolsky/ai-kindlemint-engine
# Copy the token shown
```

Then add to GitHub:
- Go to: https://github.com/IgorGanapolsky/ai-kindlemint-engine/settings/secrets/actions
- Click: "New repository secret"
- Name: `CODECOV_TOKEN`
- Value: [paste token]

### 2. SonarCloud (3 minutes)
```bash
# Visit: https://sonarcloud.io/projects/create
# Select: "Import from GitHub"
# Choose: ai-kindlemint-engine
# Click: "Set up"
```

Then:
- Go to: Account → Security → Generate Token
- Name it: "GitHub Actions"
- Copy token

Add to GitHub:
- Same page as above
- Name: `SONAR_TOKEN`
- Value: [paste token]

## That's It!

Push any code change and badges will start showing real data.

### Verify It Works:
1. Make any small change to a Python file
2. Push to GitHub
3. Watch Actions tab - both workflows should run
4. Badges will update with real metrics

---
**Note**: If badges still show "unknown" after setup, they need the first successful workflow run to populate data.
