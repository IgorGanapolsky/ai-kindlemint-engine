# AI KindleMint Engine

![Build Status](https://img.shields.io/badge/build-passing-green)
![KDP Integration](https://img.shields.io/badge/KDP-manual-yellow)
![AWS Deploy](https://img.shields.io/badge/AWS-not_deployed-red)
![Revenue](https://img.shields.io/badge/revenue-manual_tracking-orange)

## 🎯 Honest Project Status

**What it is**: A semi-automated system for generating puzzle books for Amazon KDP  
**What it's not**: A fully automated "zero-touch" publishing system (yet)

> **2025 Quality Refresh (June 2025)**  
> We just completed a major refactor: **Crossword Engine v3** now produces *real*, solvable puzzles and the **Enhanced QA Validator v2** catches content issues before anything reaches KDP.  All references below have been updated accordingly.

## ✅ What Actually Works Today

### 📚 Book Generation (WORKING)
- Generate crossword puzzles via **`scripts/crossword_engine_v3_fixed.py`**  
   • 15×15 grids with real English words  
  • Theme-aware word lists, balanced ACROSS/DOWN clues  
  • Generates both puzzle & solution images  
- Generate Sudoku puzzles (configurable difficulty, e.g. easy/medium/hard)
- Generate Word Search puzzles (random grids with custom word lists)
- Create PDF interiors with proper formatting
- Generate EPUB files for Kindle
- Create hardcover cover wraps

```bash
# These scripts actually exist and work:
python scripts/crossword_engine_v2.py
python scripts/book_layout_bot.py
python scripts/cover_wrap_master.py
# Optional puzzle generators:
python scripts/sudoku_generator.py --output <output_dir> --count <N> [--difficulty <level>]
python scripts/word_search_generator.py --output <output_dir> --count <N> [--grid-size <size>] [--words-file <file>]
```

### 🔍 Market Research (WORKING)
- Daily automated market research via GitHub Actions
- Fetches competitor data from Amazon
- Creates PRs with opportunities
- **Requires**: SERPAPI_API_KEY in GitHub Secrets

### ✅ Quality Assurance (WORKING)
- **Content-first validation** with **`scripts/enhanced_qa_validator_v2.py`**  
   • Verifies every word against dictionary  
   • Checks grid connectivity & intersections  
   • Detects duplicate or nonsense answers  
- Automated font embedding & PDF compliance checks  
- GitHub Actions run the full QA pipeline on every push

## ❌ What Doesn't Exist (Despite Previous Claims)

### 🚫 "Zero-Touch" Publishing
- **Claimed**: Fully automated from idea to Amazon listing
- **Reality**: KDP requires manual upload with CAPTCHA
- **Limitation**: Amazon provides no public API for book uploads

### 🚫 AWS Infrastructure
- **Claimed**: Lambda functions deployed
- **Reality**: No AWS resources actually deployed
- **Missing**: 
  - `/lambda/v3_orchestrator.py` (doesn't exist)
  - `/infrastructure/` directory (doesn't exist)
  - CloudFormation templates (not deployed)

### 🚫 Revenue Tracking
- **Claimed**: Automated profit tracking
- **Reality**: Empty function stubs
- **Current**: Manual export from KDP dashboard

### 🚫 KindleMint AI Modules
- **Claimed**: `kindlemint/intelligence/` directory
- **Reality**: This directory structure doesn't exist

## 📊 Real Results

- **Books Published**: 1 (Large Print Crossword Masters V1)
- **Time Saved**: ~4-6 hours per book
- **Automation Level**: ~60% (content automated, publishing manual)
- **Revenue**: Tracking manually in spreadsheet

## 🛠️ Actual Tech Stack

```
Python 3.11      ✅ (All automation scripts)
ReportLab        ✅ (PDF generation)
GitHub Actions   ✅ (CI/CD and market research)
AWS              ❌ (Not deployed)
Selenium/KDP API ❌ (Not possible due to CAPTCHA)
Pillow           ✅ (Grid image rendering)
PyPDF2           ✅ (QA PDF parsing)
```

## 🚀 How to Actually Use This

### 1. Setup
```bash
git clone https://github.com/IgorGanapolsky/ai-kindlemint-engine.git
pip install -r requirements.txt
```

### 2. Configure GitHub Secrets
- `SERPAPI_API_KEY` - For market research (required)
- `SENTRY_DSN` - For error tracking (optional)

### 3. Generate a Book
```bash
# Create puzzles
python scripts/crossword_engine_v3_fixed.py --output books/new_puzzle_batch

# Create interior
python scripts/book_layout_bot.py

# Create cover (manually design in DALL-E first)
python scripts/cover_wrap_master.py

# (Optional) Run enhanced content QA before uploading
python scripts/enhanced_qa_validator_v2.py books/new_puzzle_batch
```

### 4. Manual Steps (Required)
1. Log into KDP Dashboard
2. Click "Create Paperback"
3. Upload interior PDF
4. Upload cover PDF
5. Set metadata, categories, pricing
6. Submit for review

## 📈 Realistic Roadmap

### Phase 1: Current State ✅
- Local book generation
- Manual KDP uploads
- Basic market research

### Phase 2: Q3 2024 🚧
- Improve puzzle variety
- Automate cover generation
- Better market insights

### Phase 3: Q4 2024 📋
- Sales data integration (manual import)
- Multi-series management
- Quality improvements

### Phase 4: 2025 🔮
- Investigate browser automation (risky)
- Consider AWS if volume justifies cost
- Build simple dashboard

## ⚠️ Current Limitations

1. **KDP Upload**: Must be done manually (no API exists)
2. **Sales Data**: Must export manually from KDP
3. **Cover Images**: Requires DALL-E or designer
4. **Costs**: No automated tracking of API usage
5. **Scale**: Works for ~5 books/week; further optimisation needed for 1/day

## 💡 Why Use This?

Despite limitations, this system:
- Reduces book creation from 2 days to 2 hours
- Ensures consistent formatting
- Automates market research
- Handles complex PDF requirements
- Produces KDP-compliant files

## 🤝 Contributing

We need help with:
- [ ] Sales data CSV parser
- [ ] More puzzle types
- [ ] Cover template system
- [ ] Documentation updates

Please be honest about capabilities in any PRs.

## 📝 License

MIT - Use at your own risk

---

**Note**: This README reflects actual capabilities as of June 2024. For the original vision, see [README_ORIGINAL.md](README_ORIGINAL.md). We believe in transparency over hype.
