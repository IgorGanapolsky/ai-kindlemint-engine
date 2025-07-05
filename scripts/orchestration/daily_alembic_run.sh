#!/bin/bash
# Daily Alembic Causal AI Run
# Add this to your daily orchestration routine or crontab

echo "🧪 Running Daily Alembic Causal AI Analysis"
echo "=========================================="
date

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run Alembic orchestration
echo "⚡ Starting Alembic components..."
python scripts/run_alembic_orchestration.py

# Check if successful
if [ $? -eq 0 ]; then
    echo "✅ Alembic orchestration completed successfully"
    
    # Run CEO dashboard with Alembic insights
    echo "📊 Generating CEO dashboard with causal insights..."
    python scripts/orchestration/ceo_dashboard.py --alembic-insights
else
    echo "❌ Alembic orchestration failed"
    exit 1
fi

echo "✨ Daily Alembic run complete!"