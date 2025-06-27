# 🚀 KindleMint Engine - AI-Powered KDP Book Generator

**A tool for generating puzzle book content for Amazon KDP publishing.**

[![GitHub Actions](https://github.com/IgorGanapolsky/ai-kindlemint-engine/workflows/Production%20QA/badge.svg)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions)
[![Market Research](https://img.shields.io/badge/Market%20Research-Daily-brightgreen)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions/workflows/market_research.yml)

## 🎯 What This Project Does

KindleMint Engine is an open-source tool that helps generate puzzle book content (crosswords, sudoku, word searches) that can be formatted for Amazon KDP publishing. 

**Important**: This is a content generation tool. Publishing to KDP and any resulting sales are the user's responsibility.

## 🛠️ Current Features

### ✅ Implemented
- **Crossword Engine v3** - Generates 15×15 crossword puzzles with themed clues
- **Sudoku Generator** - Creates puzzles with verified unique solutions  
- **Word Search Generator** - Themed word search puzzles
- **PDF Generation** - Creates print-ready interior PDFs
- **Quality Validation** - Automated checks for puzzle validity
- **Market Research** - Scrapes Reddit for trending puzzle topics

### 🚧 In Development
- Cover design automation
- Batch book generation
- Sales tracking integration

### ❌ Not Implemented
- Automated KDP publishing (against KDP ToS)
- Revenue tracking API (KDP doesn't provide one)
- Guaranteed sales or revenue

## 💻 Getting Started

```bash
# Clone the repository
git clone https://github.com/IgorGanapolsky/ai-kindlemint-engine.git
cd ai-kindlemint-engine

# Install dependencies
pip install -r requirements.txt

# Generate a sample crossword book
python scripts/quick_start.py --type crossword --volume 1
```

## 📊 Market Research

The tool includes automated market research that analyzes Reddit for trending puzzle topics. View the latest report:

[View Market Research Report →](data/market-insights/market-insights.md)

## ⚠️ Important Disclaimers

1. **No Revenue Guarantees**: This tool generates content. Sales success depends on many factors including marketing, pricing, competition, and market demand.

2. **Publishing Responsibility**: Users are responsible for:
   - Following Amazon KDP's terms of service
   - Ensuring content quality
   - Marketing their books
   - Managing customer service

3. **Costs**: While the tool is free, publishing involves costs:
   - KDP printing costs
   - Marketing expenses
   - Potential API costs (Claude, DALL-E for covers)
   - Your time and effort

## 🤝 Contributing

This is an open-source project. Contributions are welcome! Please:
- Be honest about capabilities and limitations
- Test your code thoroughly
- Follow the existing code style
- Update documentation accurately

## 📈 Project Status

This project is under active development. Current focus:
- Improving puzzle generation quality
- Adding more puzzle types
- Streamlining the workflow
- Better documentation

## 🐛 Known Issues

- Crossword generation can be slow for complex themes
- Cover generation requires manual DALL-E usage
- No automated publishing (by design - KDP ToS)

## 📄 License

MIT License - Use at your own risk

## 🙏 Acknowledgments

Built with:
- Python
- ReportLab for PDF generation
- GitHub Actions for automation
- Community contributions

---

**Remember**: Success in self-publishing requires effort, market research, quality content, and often some luck. This tool is just one part of the puzzle (pun intended).