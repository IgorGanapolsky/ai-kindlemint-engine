# SonarCloud Badge Restoration Commands

## Replace the commented lines in README.md with:

```markdown
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
```

## Trigger SonarCloud Analysis

Run this command to trigger the analysis:
```bash
git push origin main
```

The SonarCloud workflow will run automatically and populate the badges with real data.

## Verification

1. Check workflow runs: https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions
2. View SonarCloud dashboard: https://sonarcloud.io/project/overview?id=IgorGanapolsky_ai-kindlemint-engine
3. Verify badges display correctly in README
