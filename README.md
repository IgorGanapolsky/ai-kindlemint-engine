# 📘 AI Kindlemint Engine

[![Deploy Lambda](https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions/workflows/deploy.yml/badge.svg)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Slack](https://img.shields.io/badge/slack-channel-blue?logo=slack)](https://hooks.slack.com/services/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)

🚀 Vision

Build an automated AI-powered publishing engine that generates, formats, and uploads professional Kindle books with
minimal human input. The goal is to:
• Produce short, high-quality books using GPT-based agents
• Deploy them to Amazon KDP for passive income
• Achieve $500/month profit with zero manual maintenance

This project follows Greg McKeown’s Essentialism principle: remove everything non-essential, automate what matters, and
focus on outcomes.

⸻

📦 Business Plan (Essentialism Aligned)

Phase Goal Deliverables
1 Ship 1 book to KDP End-to-end deployment to Amazon KDP
2 Automate book generation Title generator, GPT agent, formatter
3 Automate uploading Scripted or API-based KDP uploader
4 Revenue validation 3 books published + $1+ revenue milestone
5 Scale to passive income machine Weekly autopublishing pipeline

⸻

🧱 Architecture

├── agents/ # GPT-4o based role agents (CTO, CMO, Publisher)
├── automation/ # Scripts to automate deployment and KDP uploads
├── lambda/ # Lambda handler + control modules
├── layers/ # Python packages bundled for Lambda (OpenAI, Boto3, etc)
├── lambda_code/ # Minimal Lambda function code
├── lambda_layer/ # Directory used to build layers
├── scripts/ # One-off Python scripts (publishing, KDP conversion)
├── onboarding/ # Client-facing onboarding documents
├── utils/ # Email, file, and Sheets helpers
├── output/ # Generated sample book artifacts
├── .github/workflows/ # GitHub Actions automation (CI/CD to Lambda)

⸻

✅ Automation & Deployment

1. Build Lambda Layers

bash layers/build_layers.sh

2. Deploy Function to AWS

python scripts/deploy_lambda.py

3. Auto-deploy via GitHub Actions

Push to main → Triggers:
• Lambda layer rebuild
• Zip Lambda code
• Upload to S3
• Lambda update from S3

⸻

📊 Metrics We Track
• ⏱ Time to deploy book
• 📚 Number of books published
• 💸 Total sales and royalties
• 🧠 Agent success rate
• ⚠️ Errors in KDP upload process

⸻

🛠️ Stack
• Python 3.11
• OpenAI GPT-4o
• AWS Lambda + S3
• Amazon KDP
• GitHub Actions

⸻

🧑‍💻 Local Setup

git clone https://github.com/IgorGanapolsky/ai-kindlemint-engine.git
cd ai-kindlemint-engine
python3 -m venv venv
source venv/bin/activate
pip install -r lambda/requirements.txt

⸻

💡 Inspiration

This is a lean, shipping-focused AI SaaS experiment. Its mission is to automate digital income generation and prove
that:

A solopreneur with GPT + Lambda + GitHub Actions can generate real cash in under 30 days.

Let’s execute.
