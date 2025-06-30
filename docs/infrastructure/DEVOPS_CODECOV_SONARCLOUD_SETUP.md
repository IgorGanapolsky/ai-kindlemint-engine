# 🚀 DevOps Setup Guide: Codecov & SonarCloud Implementation

## 📋 Executive Summary

This guide provides step-by-step instructions to configure Codecov and SonarCloud for the `ai-kindlemint-engine` repository. Both services will provide code coverage and quality metrics with proper badge integration.

---

## 🎯 Codecov Setup

### Step 1: Create Codecov Account & Import Repository

1. **Go to [codecov.io](https://codecov.io)**
2. **Sign in with GitHub** (use the same account that owns the repository)
3. **Authorize Codecov** to access your GitHub repositories
4. **Find and activate** `IgorGanapolsky/ai-kindlemint-engine` from the repository list
5. **Copy the upload token** - You'll see it after activation (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### Step 2: Add Codecov Token to GitHub Secrets

1. **Navigate to your repository** on GitHub: `https://github.com/IgorGanapolsky/ai-kindlemint-engine`
2. **Go to Settings** → **Secrets and variables** → **Actions**
3. **Click "New repository secret"**
4. **Add the secret:**
   - Name: `CODECOV_TOKEN`
   - Value: [paste the token from Codecov]
5. **Click "Add secret"**

### Step 3: Verify Codecov Integration

The integration is already configured in `.github/workflows/tests.yml`. To verify:

1. **Make a small change** to any Python file
2. **Push to main** or create a PR
3. **Check the Actions tab** - the test workflow should upload coverage
4. **Visit your Codecov dashboard** to see the coverage report

---

## 🔍 SonarCloud Setup

### Step 1: Create SonarCloud Account & Import Project

1. **Go to [sonarcloud.io](https://sonarcloud.io)**
2. **Sign in with GitHub**
3. **Click "+ Analyze new project"**
4. **Select your GitHub organization** (or personal account)
5. **Choose** `ai-kindlemint-engine` from the repository list
6. **Click "Set Up"**

### Step 2: Configure SonarCloud Project

1. **Choose "With GitHub Actions"** as the analysis method
2. **Note your project information:**
   - Organization Key: `igorganapolsky` (or your org name)
   - Project Key: `IgorGanapolsky_ai-kindlemint-engine`
3. **Generate a new token:**
   - Click "Generate a token"
   - Name it: `GitHub Actions`
   - Copy the token (format: `sqp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### Step 3: Add SonarCloud Token to GitHub Secrets

1. **Go back to GitHub repository settings**
2. **Navigate to Settings** → **Secrets and variables** → **Actions**
3. **Click "New repository secret"**
4. **Add the secret:**
   - Name: `SONAR_TOKEN`
   - Value: [paste the token from SonarCloud]
5. **Click "Add secret"**

### Step 4: Verify SonarCloud Configuration

The `sonar-project.properties` file is already correctly configured. The key settings match:
- `sonar.projectKey=IgorGanapolsky_ai-kindlemint-engine`
- `sonar.organization=igorganapolsky`

---

## 🏷️ Add Badges to README

After both services are configured, add these badges to your README.md right after the Tests badge (line 5):

```markdown
[![Tests](https://github.com/IgorGanapolsky/ai-kindlemint-engine/workflows/Tests/badge.svg)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine/graph/badge.svg?token=YOUR_CODECOV_TOKEN)](https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=coverage)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
```

Note: Replace `YOUR_CODECOV_TOKEN` with the actual token from your Codecov settings page.

---

## ✅ Implementation Checklist

### Codecov Setup
- [ ] Create Codecov account and sign in with GitHub
- [ ] Import/activate the `ai-kindlemint-engine` repository
- [ ] Copy the Codecov upload token
- [ ] Add `CODECOV_TOKEN` to GitHub repository secrets
- [ ] Push a commit to trigger the workflow
- [ ] Verify coverage upload in Codecov dashboard
- [ ] Add Codecov badge to README.md

### SonarCloud Setup
- [ ] Create SonarCloud account and sign in with GitHub
- [ ] Import the `ai-kindlemint-engine` project
- [ ] Verify organization and project keys match `sonar-project.properties`
- [ ] Generate SonarCloud token for GitHub Actions
- [ ] Add `SONAR_TOKEN` to GitHub repository secrets
- [ ] Push a commit to trigger the SonarCloud workflow
- [ ] Verify analysis appears in SonarCloud dashboard
- [ ] Add SonarCloud badges to README.md

### Final Verification
- [ ] Both workflows run successfully on push/PR
- [ ] Codecov shows coverage percentage
- [ ] SonarCloud shows code quality metrics
- [ ] All badges display correctly in README
- [ ] No "not configured" messages on badges

---

## 🔧 Troubleshooting

### Codecov Issues
- **No coverage data**: Ensure `coverage.xml` is generated in tests
- **Token error**: Verify `CODECOV_TOKEN` secret is set correctly
- **Badge shows "unknown"**: Wait for first successful upload

### SonarCloud Issues
- **Authentication failed**: Check `SONAR_TOKEN` secret
- **Project not found**: Verify project/organization keys in `sonar-project.properties`
- **No analysis**: Ensure the workflow triggers on file changes in `src/`, `scripts/`, or `tests/`

### Quick Debug Commands
```bash
# Test coverage generation locally
python -m pytest tests/ --cov=src/kindlemint --cov-report=xml

# Check if coverage.xml exists
ls -la coverage.xml

# Validate sonar-project.properties
cat sonar-project.properties
```

---

## 📞 Support Resources

- **Codecov Documentation**: https://docs.codecov.io/docs
- **SonarCloud Documentation**: https://docs.sonarcloud.io/
- **GitHub Actions Secrets**: https://docs.github.com/en/actions/security-guides/encrypted-secrets

---

## 🎉 Success Criteria

You'll know the setup is complete when:
1. Push/PR triggers both Codecov and SonarCloud analysis
2. Badges show actual metrics (not "unknown" or "not configured")
3. Dashboards are accessible at:
   - Codecov: `https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine`
   - SonarCloud: `https://sonarcloud.io/project/overview?id=IgorGanapolsky_ai-kindlemint-engine`

---

*Last updated: June 2025*
