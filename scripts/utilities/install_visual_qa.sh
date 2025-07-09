#!/bin/bash
# Install Visual QA Dependencies

echo "🔧 Installing Visual QA dependencies..."

# Check OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📱 macOS detected"
    
    # Install poppler for pdf2image
    if ! command -v pdftocairo &> /dev/null; then
        echo "Installing poppler-utils..."
        brew install poppler
    fi
    
    # Install tesseract for OCR
    if ! command -v tesseract &> /dev/null; then
        echo "Installing tesseract..."
        brew install tesseract
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linux detected"
    
    # Update package list
    sudo apt-get update
    
    # Install dependencies
    sudo apt-get install -y \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-eng \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1
fi

# Install Python packages
echo "📦 Installing Python packages..."
pip install -r requirements-visual-qa.txt

echo "✅ Visual QA dependencies installed!"
echo ""
echo "You can now run:"
echo "  python test_visual_qa.py"
echo "  kindlemint validate <pdf_file>"
echo "  kindlemint compare-pdfs <pdf1> <pdf2>"