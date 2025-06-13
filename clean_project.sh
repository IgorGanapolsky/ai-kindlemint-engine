#!/bin/bash

echo '🚀 Refactoring project layout...'

# Create target folders
mkdir -p lambda layers/openai layers/boto3 scripts automation onboarding .github/workflows

# Move source code
mv lambda_function.py lambda/handler.py
mv config.py lambda/
mv mission_control.py lambda/
mv package_requirements.txt lambda/requirements.txt

# Move build/deploy infra
mv build_layers.sh layers/
mv deploy_lambda.py scripts/

# Move automation scripts
mv start.sh automation/
mv stop_passive_income.sh automation/
mv start_passive_income.sh automation/

# Move onboarding/README documents
mv README_SETUP.md onboarding/
mv ONBOARDING_EMAIL.md onboarding/
mv README.md README.md  # Keep root README

echo '✅ Project structure updated.'
