# AI KindleMint Engine - Enhanced Documentation

![Build Status](https://img.shields.io/badge/build-passing-green)
![Tests](https://img.shields.io/badge/tests-implemented-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The AI KindleMint Engine is a semi-automated system for generating high-quality puzzle books for Amazon KDP. It streamlines the content creation process, reducing book production time from days to hours while ensuring professional quality and KDP compliance.

### What It Does
- **Generates** crossword, Sudoku, and word search puzzles with configurable difficulty
- **Creates** print-ready PDFs with proper formatting and embedded fonts
- **Validates** content quality through comprehensive QA checks
- **Researches** market opportunities via automated competitor analysis
- **Produces** both paperback and hardcover formats

### What It Doesn't Do
- Does NOT automatically upload to KDP (requires manual upload due to CAPTCHA)
- Does NOT track sales automatically (requires manual export from KDP dashboard)
- Does NOT generate cover images (requires DALL-E or designer input)

## ✨ Features

### 📚 Puzzle Generation
- **Crossword Engine v2**: Creates 15×15 grids with real words and themed clues
- **Sudoku Generator**: Produces valid puzzles with unique solutions
- **Word Search Creator**: Generates grids with customizable word lists

### 🔍 Quality Assurance
- **Enhanced QA Validator v2**: Content-first validation ensuring:
  - All puzzle answers are real dictionary words
  - Solutions are properly filled (150+ letters for crosswords)
  - No duplicate or placeholder clues
  - Proper grid connectivity and intersections

### 📊 Market Research
- Daily automated analysis via GitHub Actions
- Competitor tracking and opportunity identification
- Generates actionable reports as pull requests

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- Git
- pip package manager

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/IgorGanapolsky/ai-kindlemint-engine.git
   cd ai-kindlemint-engine
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python run_tests.py --unit  # Run unit tests to verify setup
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Market Research API (required for automated research)
SERPAPI_API_KEY=your_serpapi_key_here

# Error Tracking (optional)
SENTRY_DSN=your_sentry_dsn_here

# Slack Notifications (optional)
SLACK_WEBHOOK_URL=your_slack_webhook_here
```

### GitHub Secrets

For GitHub Actions to work properly, add these secrets to your repository:
- `SERPAPI_API_KEY` - Required for market research workflow
- `SENTRY_DSN` - Optional for error tracking
- `SLACK_WEBHOOK_URL` - Optional for notifications

## 📖 Usage

### Generate Crossword Puzzles

```bash
# Basic usage - generates 50 mixed-difficulty puzzles
python scripts/crossword_engine_v2.py --output books/my_crossword_book

# Advanced options
python scripts/crossword_engine_v2.py \
  --output books/my_crossword_book \
  --count 30 \
  --difficulty medium \
  --grid-size 15
```

**Parameters:**
- `--output`: Output directory for generated puzzles (required)
- `--count`: Number of puzzles to generate (default: 50)
- `--difficulty`: Puzzle difficulty - easy/medium/hard/mixed (default: mixed)
- `--grid-size`: Grid dimensions (default: 15x15)

### Generate Sudoku Puzzles

```bash
# Generate 25 medium difficulty Sudoku puzzles
python scripts/sudoku_generator.py \
  --output books/my_sudoku_book \
  --count 25 \
  --difficulty medium
```

### Generate Word Search Puzzles

```bash
# Generate word search with custom word list
python scripts/word_search_generator.py \
  --output books/my_wordsearch_book \
  --count 20 \
  --grid-size 20 \
  --words-file themes/animals.txt
```

### Create Book Interior PDF

```bash
# After generating puzzles, create the book interior
python scripts/book_layout_bot.py \
  --puzzles-dir books/my_crossword_book/puzzles \
  --output books/my_crossword_book/interior.pdf \
  --title "Amazing Crosswords Volume 1"
```

### Validate Book Quality

```bash
# Run comprehensive QA validation
python scripts/comprehensive_qa_validator.py books/my_crossword_book

# Run enhanced content validation
python scripts/enhanced_qa_validator_v2.py books/my_crossword_book
```

### Create Hardcover Package

```bash
# First create a config file (see templates/hardcover/production_docs/book_config_template.json)
python scripts/hardcover/create_hardcover_package.py books/my_book/hardcover_config.json
```

## 🧪 Testing

The project includes comprehensive unit and integration tests.

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Suites
```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Specific test file
python -m unittest tests.unit.test_crossword_engine
```

### Test Coverage
- **Unit Tests**: Cover puzzle generators, validators, and core utilities
- **Integration Tests**: Test end-to-end book generation pipeline
- **QA Tests**: Validate that generated content meets quality standards

## 📁 Project Structure

```
ai-kindlemint-engine/
├── scripts/                    # Main executable scripts
│   ├── crossword_engine_v2.py # Crossword generator
│   ├── sudoku_generator.py    # Sudoku generator
│   ├── word_search_generator.py # Word search generator
│   ├── book_layout_bot.py     # PDF interior creator
│   ├── enhanced_qa_validator_v2.py # Content validator
│   ├── comprehensive_qa_validator.py # Full QA suite
│   └── puzzle_validators.py   # Validation utilities
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── templates/                 # Book and cover templates
├── books/                     # Generated books output
│   └── active_production/     # Current book projects
├── .github/workflows/         # GitHub Actions
│   ├── book_qa_validation.yml
│   ├── debug_market_research.yml
│   └── production_qa.yml
├── requirements.txt           # Python dependencies
├── run_tests.py              # Test runner
└── README.md                 # This file
```

## 📚 API Reference

### CrosswordEngineV2

```python
from scripts.crossword_engine_v2 import CrosswordEngineV2

# Initialize engine
engine = CrosswordEngineV2(
    output_dir="path/to/output",
    puzzle_count=50,
    difficulty="mixed",
    grid_size=15
)

# Generate puzzles
puzzles = engine.generate_puzzles()
```

### Validators

```python
from scripts.puzzle_validators import validate_crossword_solutions_in_pdf

# Validate PDF solutions
success, stats = validate_crossword_solutions_in_pdf(Path("book.pdf"))
if not success:
    print(f"Validation failed: {stats['empty_solutions']} empty solutions found")
```

## 🤝 Contributing

We welcome contributions! Areas where help is needed:

1. **Additional Puzzle Types**
   - Cryptic crosswords
   - Logic puzzles
   - Number puzzles

2. **Enhanced Features**
   - Better theme generation
   - Improved difficulty algorithms
   - Multi-language support

3. **Infrastructure**
   - AWS deployment templates
   - Docker containerization
   - Performance optimizations

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`python run_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure you're in the project root and virtual environment is activated
cd ai-kindlemint-engine
source venv/bin/activate
```

**GitHub Actions Failing**
- Check that all required secrets are set in repository settings
- Ensure you're using the latest action versions (v4)

**QA Validation Failures**
- Run `python scripts/enhanced_qa_validator_v2.py` locally
- Check the generated report for specific issues
- Common problems: empty solutions, placeholder clues, missing metadata

**PDF Generation Issues**
```bash
# Install required system fonts
# macOS:
brew install font-liberation

# Ubuntu/Debian:
sudo apt-get install fonts-liberation
```

### Getting Help

1. Check existing [GitHub Issues](https://github.com/IgorGanapolsky/ai-kindlemint-engine/issues)
2. Read the test files for usage examples
3. Create a new issue with:
   - Python version (`python --version`)
   - Full error traceback
   - Steps to reproduce

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This documentation reflects the enhanced state of the project after implementing comprehensive testing, improved documentation, and pinned dependencies. For historical context, see [README_ORIGINAL.md](README_ORIGINAL.md).