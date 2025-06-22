# AI KindleMint Engine - Daily Book Production Factory

🏭 **Daily Book Series Generator for Amazon KDP Publishing**

## 🚀 Quick Start

1. **Generate Today's Series**:
   ```bash
   python scripts/run_daily_production.py
   ```

2. **Find Your Content**:
   - Location: `output/daily_production/YYYYMMDD/`
   - Complete manuscripts, cover prompts, publishing guides included

3. **Publish**:
   - Create covers using provided prompts
   - Follow step-by-step KDP publishing guides
   - Set up Amazon advertising campaigns

## 📚 What Gets Generated Daily

- **Puzzle Books**: Crosswords, Sudoku, Word Search
- **Activity Books**: Adult Coloring, Kids Activities  
- **Journals**: Gratitude, Goal Setting, Travel

Each series includes:
- ✅ Complete manuscripts with professional content
- ✅ Cover design prompts (DALL-E, Midjourney, Canva)
- ✅ Step-by-step KDP publishing guides
- ✅ Marketing strategies and ad campaigns
- ✅ Revenue projections

## 🤖 Automation

- **Manual**: Run `python scripts/run_daily_production.py` daily
- **Automated**: GitHub Actions runs daily at 9 AM UTC
- **Output**: Organized in `output/daily_production/` by date

## 💰 Revenue Potential

- Each series: 3-8 volumes at $5.99-$9.99 each
- Target: 100 sales per month per volume
- Projected: $2,000-$7,000+ monthly revenue per series
- Strategy: Publish daily → Build catalog → Scale successful series

## 🎯 Focus

This system generates professional book content daily. You focus on:
1. Creating covers
2. Publishing on KDP
3. Marketing and advertising
4. Scaling what works

**Stop building. Start publishing. Make money.**

## 📁 Project Structure

```
ai-kindlemint-engine/
├── scripts/
│   ├── daily_series_generator.py    # Core series generator
│   └── run_daily_production.py      # Daily automation runner
├── .github/workflows/
│   └── daily_production.yml         # GitHub Actions automation
├── kindlemint/                      # Core libraries
├── output/
│   └── daily_production/            # Generated content by date
├── .env                            # API keys and configuration
└── requirements.txt                # Python dependencies
```

## ⚙️ Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   - Copy `.env.example` to `.env`
   - Add your `OPENAI_API_KEY`

3. **Run Daily Production**:
   ```bash
   python scripts/run_daily_production.py
   ```

## 🎯 Business Model

1. **Daily Content Generation**: Automated series creation
2. **Manual Publishing**: Focus on covers and KDP publishing
3. **Revenue Optimization**: Track sales, scale winners
4. **Catalog Building**: Compound growth through daily publishing

**The fastest path from automation to revenue.**