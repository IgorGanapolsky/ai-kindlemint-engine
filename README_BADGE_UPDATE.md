# README Badge Update Instructions

## Current Badge Section (lines 5-13):
```markdown
[![Tests](https://github.com/IgorGanapolsky/ai-kindlemint-engine/workflows/Tests/badge.svg)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions/workflows/tests.yml)
[![GitHub Forks](https://img.shields.io/github/forks/IgorGanapolsky/ai-kindlemint-engine)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/network)
...
```

## Updated Badge Section (add after Tests badge):
```markdown
[![Tests](https://github.com/IgorGanapolsky/ai-kindlemint-engine/workflows/Tests/badge.svg)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine/graph/badge.svg)](https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=coverage)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
[![GitHub Forks](https://img.shields.io/github/forks/IgorGanapolsky/ai-kindlemint-engine)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/network)
...
```

## Note on Codecov Badge Token
The Codecov badge URL might need a token parameter if your repository is private. You can find this in:
1. Codecov Dashboard → Settings → Badge
2. Copy the markdown code provided there

For public repositories, the badge usually works without the token parameter.
