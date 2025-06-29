# Python Environment Setup Guide

## Quick Start (2 minutes)

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script
./setup_environment.sh
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Option 3: Force Install (System-wide)
```bash
# If you have permission issues
pip install --break-system-packages PyPDF2 PyMuPDF reportlab
```

## Verifying Installation

After setup, verify critical dependencies:

```bash
python3 -c "import PyPDF2; print('✓ PyPDF2 installed')"
python3 -c "import fitz; print('✓ PyMuPDF installed')"
python3 -c "import reportlab; print('✓ ReportLab installed')"
```

## Testing the Setup

Run a test batch:
```bash
python scripts/batch_processor.py config/test_batch.json
```

## Common Issues

### ModuleNotFoundError
- **Cause**: Dependencies not installed
- **Fix**: Run `pip install -r requirements.txt`

### Permission Denied
- **Cause**: System Python restrictions
- **Fix**: Use virtual environment or `--break-system-packages` flag

### ImportError with PyMuPDF
- **Cause**: PyMuPDF installs as `fitz` module
- **Fix**: Import as `import fitz` not `import pymupdf`

## Dependencies Overview

### Critical (Required)
- **PyPDF2**: PDF manipulation and QA checks
- **PyMuPDF**: Advanced PDF processing
- **ReportLab**: PDF creation
- **Pillow**: Image processing

### Monitoring (Recommended)
- **sentry-sdk**: Error tracking
- **requests**: Slack notifications

### Optional (Enhancement)
- **pandas**: Data analysis
- **matplotlib**: Visualization
- **tqdm**: Progress bars
