# 📋 Quick Setup Checklist: Codecov & SonarCloud

## 🎯 Codecov (5 minutes)
```
□ 1. Go to codecov.io → Sign in with GitHub
□ 2. Find & activate: IgorGanapolsky/ai-kindlemint-engine
□ 3. Copy the upload token (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
□ 4. GitHub → Settings → Secrets → Actions → New repository secret
     - Name: CODECOV_TOKEN
     - Value: [paste token]
□ 5. Push any code change to trigger workflow
□ 6. Check codecov.io dashboard for coverage report
```

## 🔍 SonarCloud (10 minutes)
```
□ 1. Go to sonarcloud.io → Sign in with GitHub
□ 2. Click "+ Analyze new project" → Select ai-kindlemint-engine
□ 3. Choose "With GitHub Actions" analysis method
□ 4. Generate token → Name: "GitHub Actions" → Copy token
□ 5. GitHub → Settings → Secrets → Actions → New repository secret
     - Name: SONAR_TOKEN
     - Value: [paste token]
□ 6. Push any code change to trigger workflow
□ 7. Check sonarcloud.io dashboard for analysis
```

## 🏷️ Add Badges to README.md
```
□ 1. Edit README.md after line 5 (after Tests badge)
□ 2. Add these badges:

[![codecov](https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)

□ 3. Replace YOUR_TOKEN with actual Codecov token
□ 4. Commit and push changes
```

## ✅ Verify Everything Works
```
□ Push triggers both workflows successfully
□ Codecov badge shows coverage percentage
□ SonarCloud badge shows "Passed" or quality status
□ No "unknown" or "not configured" on badges
```

## 🆘 Quick Fixes
- **Codecov not working?** → Check CODECOV_TOKEN secret spelling
- **SonarCloud not working?** → Check SONAR_TOKEN secret spelling
- **Badges show "unknown"?** → Wait 2-3 minutes after first push

## 📍 Dashboard URLs (bookmark these!)
- Codecov: https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine
- SonarCloud: https://sonarcloud.io/project/overview?id=IgorGanapolsky_ai-kindlemint-engine
