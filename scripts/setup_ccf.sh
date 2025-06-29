#!/bin/bash
# Setup script for Claude Code Flow integration
# This script helps set up ccf for the KindleMint Engine project

set -e

echo "🚀 Setting up Claude Code Flow for KindleMint Engine"
echo "===================================================="

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "❌ pipx not found. Installing pipx first..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    echo "✅ pipx installed. Please restart your terminal and run this script again."
    exit 0
fi

# Install claude-code-flow
echo "📦 Installing claude-code-flow..."
pipx install claude-code-flow || {
    echo "⚠️  Installation failed. Trying with pip..."
    pip install claude-code-flow
}

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  ANTHROPIC_API_KEY not found in environment"
    echo ""
    echo "To set up your API key:"
    echo "1. Get your key from https://console.anthropic.com/"
    echo "2. Add to your .env file:"
    echo "   echo 'ANTHROPIC_API_KEY=your_key_here' >> .env"
    echo "3. Source the environment:"
    echo "   source .env"
    echo ""
else
    echo "✅ API key found in environment"
fi

# Create useful aliases
echo ""
echo "📝 Creating useful aliases..."
cat << 'EOF' > ~/.kindlemint_ccf_aliases
# KindleMint CCF Aliases
alias ccf-review='ccf "Review these changes for code quality, potential bugs, and KindleMint best practices"'
alias ccf-commit='ccf "Generate a conventional commit message for these changes"'
alias ccf-test='ccf "Review my test cases. Are there any edge cases Im missing?"'
alias ccf-qa='ccf "Review these QA validator changes. Check for edge cases and false positives"'
alias ccf-puzzle='ccf "Review this puzzle generation code for correctness and efficiency"'
alias ccf-help='ccf "Explain how this part of the KindleMint codebase works"'
EOF

echo ""
echo "To use these aliases, add to your shell config:"
echo "  echo 'source ~/.kindlemint_ccf_aliases' >> ~/.bashrc"
echo "  # or"
echo "  echo 'source ~/.kindlemint_ccf_aliases' >> ~/.zshrc"

# Test installation
echo ""
echo "🧪 Testing installation..."
if command -v ccf &> /dev/null; then
    echo "✅ ccf is installed and available"
    ccf --version 2>/dev/null || echo "Version check not supported"
else
    echo "❌ ccf not found in PATH. Please check installation."
    exit 1
fi

# Create example usage file
cat << 'EOF' > ccf_examples.md
# Quick CCF Examples for KindleMint Engine

## Before pushing puzzle generator changes:
ccf "Review my changes to crossword_engine_v2.py. Check for proper error handling and grid validation"

## After fixing a bug:
ccf "Generate a commit message. Context: Fixed issue where hardcover PDFs had incorrect margins"

## When stuck on implementation:
ccf "How should I implement S3 storage to replace Git LFS in this project?"

## For test coverage:
ccf "What test cases am I missing for the sudoku generator?"

## Quick code review:
ccf "Any issues with these changes?"
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Set your ANTHROPIC_API_KEY in .env"
echo "2. Source the aliases file"
echo "3. Try: ccf 'Explain the KindleMint project structure'"
echo ""
echo "See ccf_examples.md for more usage examples"
echo "Full guide at: docs/claude_code_flow_integration.md"
