#!/bin/bash
# Automated Business Startup Script

echo "🚀 Starting Automated Revenue Generator..."

# Activate virtual environment
source venv/bin/activate

# Load environment variables
source .env

# Start the orchestrator
python3 scripts/automated_business_orchestrator.py
