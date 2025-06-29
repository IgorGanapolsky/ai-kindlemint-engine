#!/bin/bash
# KindleMint Engine - Environment Setup Script
# This script sets up the Python environment and installs all dependencies

echo "🚀 KindleMint Engine - Environment Setup"
echo "========================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Verify critical dependencies
echo ""
echo "🔍 Verifying critical dependencies..."
python3 -c "import PyPDF2; print('✓ PyPDF2 installed')"
python3 -c "import fitz; print('✓ PyMuPDF installed')"
python3 -c "import reportlab; print('✓ ReportLab installed')"
python3 -c "import PIL; print('✓ Pillow installed')"
python3 -c "import sentry_sdk; print('✓ Sentry SDK installed')"

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test the batch processor, run:"
echo "  python scripts/batch_processor.py config/test_batch.json"
