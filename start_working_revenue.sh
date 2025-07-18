#!/bin/bash

echo "🚀 Starting Working Revenue Generator for Sudoku Business"
echo "============================================================"

# Activate virtual environment and load environment variables
source venv/bin/activate
source .env
export $(cat .env | xargs)

# Make script executable
chmod +x scripts/working_revenue_generator.py

# Start the working revenue generator
echo "💰 Starting revenue generation..."
python3 scripts/working_revenue_generator.py continuous

echo "✅ Revenue generator started successfully!" 