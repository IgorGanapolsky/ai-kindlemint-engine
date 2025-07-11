# GitHub ANTHROPIC_API_KEY Setup Guide

## Quick Setup (2 minutes)

### 1. Get your Anthropic API Key
- Visit: https://console.anthropic.com/settings/keys
- Click "Create Key"
- Copy the key (starts with `sk-ant-api03-`)

### 2. Add to GitHub Repository Secrets
1. Go to your repository: https://github.com/IgorGanapolsky/ai-kindlemint-engine
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Secret: Paste your API key
6. Click **Add secret**

### 3. Test Claude Code Action
Create a comment on any PR or issue with:
```
@claude help me fix this issue
```

## What This Enables

✅ **Automated PR Reviews**: Claude analyzes and suggests improvements
✅ **Issue Resolution**: Ask Claude to implement fixes directly
✅ **Code Generation**: Request new features via comments
✅ **CI Fix Automation**: Claude can fix failing tests automatically

## Usage Examples

### On Pull Requests:
```
@claude review this PR and suggest improvements
@claude fix the failing tests
@claude add error handling to this function
```

### On Issues:
```
@claude implement this feature
@claude help me understand this error
@claude create a solution for this problem
```

## Security Notes
- The API key is encrypted and only accessible during workflow runs
- Never commit API keys to code
- Rotate keys periodically for security

## Troubleshooting
- Check Actions tab for workflow runs
- Ensure ANTHROPIC_API_KEY is set correctly
- Verify @claude is mentioned in comments

---
Once configured, Claude will automatically respond to mentions in PRs and issues!