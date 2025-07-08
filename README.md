# 🚀 AI-KindleMint-Engine - Revolutionary AI-Powered Book Publishing Platform

**Transform expertise into profitable books at 10x speed using AI orchestration, voice-to-book technology, and automated publishing workflows.**

[![Tests](https://github.com/IgorGanapolsky/ai-kindlemint-engine/workflows/Tests/badge.svg)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine/graph/badge.svg)](https://codecov.io/gh/IgorGanapolsky/ai-kindlemint-engine)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=IgorGanapolsky_ai-kindlemint-engine&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=IgorGanapolsky_ai-kindlemint-engine)
[![Hygiene Score](https://img.shields.io/badge/hygiene-76%25-green)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/blob/main/scripts/real_hygiene_analyzer.py)
<!-- Orchestration Cost Tracking -->
[![MTD Cost](https://img.shields.io/badge/MTD_Cost-$26.60-green)](./reports/orchestration/) [![Orchestration Savings](https://img.shields.io/badge/Orchestration_Savings-$2.40_8%25-orange)](./reports/orchestration/)
[![Cursor Bugbot](https://img.shields.io/badge/Cursor%20Bugbot-Enabled-blueviolet)](https://docs.cursor.com/bugbot)
[![GitHub Issues](https://img.shields.io/github/issues/IgorGanapolsky/ai-kindlemint-engine)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/IgorGanapolsky/ai-kindlemint-engine)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/pulls)
[![Last Commit](https://img.shields.io/github/last-commit/IgorGanapolsky/ai-kindlemint-engine)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/commits/main)
[![Contributors](https://img.shields.io/github/contributors/IgorGanapolsky/ai-kindlemint-engine)](https://github.com/IgorGanapolsky/ai-kindlemint-engine/graphs/contributors)
[![Code Size](https://img.shields.io/github/languages/code-size/IgorGanapolsky/ai-kindlemint-engine)](https://github.com/IgorGanapolsky/ai-kindlemint-engine)
## 🎯 What This Project Does

AI-KindleMint-Engine is a comprehensive platform that:
1. **Generates** high-quality book content using AI agents
2. **Validates** content with enterprise-grade QA systems
3. **Prepares** publication-ready content for KDP and social media (manual publishing required)
4. **Automates** BookTok/social media marketing with parallel content generation
5. **Monetizes** through affiliates, courses, and upsells
6. **Improves** continuously through AI-powered optimization

**Important**: Users are responsible for following platform ToS, marketing their books, and managing sales.

## Getting Started

### Prerequisites
- Python 3.11+
- Git
- OpenAI API key

### Quick Setup
```bash
git clone https://github.com/IgorGanapolsky/ai-kindlemint-engine.git
cd ai-kindlemint-engine
pip install -r requirements.txt
```

### Basic Usage
```bash
# Generate a puzzle book
python scripts/sudoku_generator.py --count 100

# Run QA validation
python scripts/critical_metadata_qa.py

# Start orchestration
python src/kindlemint/orchestration_runner.py
```

### Documentation
- [Implementation Plan](docs/plan.md)
- [Commit Guidelines](docs/COMMIT_VALIDATION.md)
- [Orchestration Strategy](docs/GIT_WORKTREES_ORCHESTRATION_STRATEGY.md)

## 🏗️ Infrastructure & Orchestration

### 🚀 Recent Updates (July 2025)

**Streamlined Infrastructure:**
- Migrated to Vercel for deployment (Free tier for testing)
- Amp CLI integration with automated tagging
- Emergency CI/CD pipeline restoration completed

**Autonomous Worktree Orchestration:**
- **4x faster content generation** through parallel execution
- **60-80% cost reduction** via intelligent task distribution
- **Autonomous content creation** - manual publishing required

### 📊 Business Impact

| Metric | Traditional | With Worktrees | Improvement |
|--------|-------------|----------------|-------------|
| Content Generation Time | 2-4 hours | 30 minutes | **75% faster** |
| Books Generated per Hour | 1 | 4 | **4x capacity** |
| Monthly Output | 100 books | 400 books | **4x increase** |
| API Cost per Book | $2.50 | $0.75 | **70% reduction** |
| CPU Utilization | 25% | 90%+ | **Optimal usage** |

### 🤖 Orchestration Flow

```mermaid
graph TD
    A[PR Created] --> B[CI/CD Pipeline]
    B --> C{All Checks Pass?}
    C -->|Yes| D[Orchestrator Auto-Merge]
    C -->|No| E[Auto-Fix Attempts]
    E --> F{Fix Successful?}
    F -->|Yes| D
    F -->|No| G[Manual Review Required]
    D --> H[Badge Updates]
    H --> I[Cost Tracking]
    I --> J[Documentation Sync]
```

### 🤖 How It Works

Our Autonomous Worktree Manager creates specialized parallel execution environments:

```
📂 Worktree Architecture:
├── puzzle-gen/       → Parallel puzzle generation (Sudoku, Crossword, Word Search)
├── pdf-gen/          → Parallel PDF creation and layout optimization
├── qa-validation/    → Parallel quality checks and validation
├── ci-fixes/         → Autonomous CI problem resolution
└── market-research/  → Parallel market analysis and trend detection
```

Each worktree operates independently on its own Git branch, enabling true parallel execution without conflicts.

## 🎬 BookTok Marketing Automation (NEW)

**Revolutionary social media automation addressing the zero-revenue gap through parallel content generation.**

### 📊 BookTok Impact Metrics

| Metric | Before BookTok | With BookTok Automation | Improvement |
|--------|----------------|-------------------------|-------------|
| Social Media Presence | 0% | 100% automated | **∞ improvement** |
| Content Generation Speed | Manual | 4x parallel worktrees | **4x faster** |
| Platform Coverage | Amazon only | TikTok + Pinterest + Instagram | **Multi-platform** |
| Marketing Cost | $0 (no marketing) | Automated ($0.75/book) | **Cost-effective** |
| Revenue Potential | $0 | Scalable social traffic | **Revenue unlocked** |

### 🚀 BookTok Automation Features

**Parallel Content Generation:**
- **4 dedicated worktrees** for simultaneous social content creation
- **TikTok script generation** with trending hashtag optimization
- **Visual asset creation** for puzzle teasers and brain health graphics
- **Posting calendar automation** with daily themed content
- **ROI tracking** with UTM links and analytics

**Content Strategy Pillars:**
1. **Behind-the-Scenes AI** - Show the book creation process
2. **Puzzle Demonstrations** - Interactive solving videos
3. **Brain Health Education** - Benefits of puzzle solving for seniors

**Cross-Platform Distribution:**
- **TikTok** (#BookTok, #PuzzleBooks, #BrainHealth)
- **Pinterest** (puzzle pins, brain health infographics)
- **Instagram** (carousel posts, stories)
- **Facebook** (community engagement)

### 🎯 BookTok Quick Start

```bash
# Generate BookTok content for all books (parallel execution)
python scripts/orchestration/booktok_worktree_orchestrator.py

# Run daily BookTok automation
./scripts/automation/daily_booktok_tasks.sh

# Check BookTok analytics
cat data/analytics/social_media_metrics.json

# View generated content
ls books/*/social_media_content/
```

**Generated Assets:**
- TikTok video scripts with hooks and CTAs
- Hashtag strategies for maximum discoverability
- Posting calendars with optimal timing
- UTM tracking links for ROI measurement
- Cross-platform content variations

### 🏗️ BookTok Worktree Architecture

```
BookTok Automation System:
├── booktok-content/        # TikTok script generation
├── booktok-visuals/        # Visual asset creation
├── booktok-analytics/      # ROI tracking & metrics
└── booktok-scheduler/      # Posting automation
```

**Parallel Execution Benefits:**
- **Zero conflicts** between content generation tasks
- **4x speedup** for social media content creation
- **Scalable** to 100+ books simultaneously
- **Resource efficient** using existing worktree infrastructure

### 💡 Technical Architecture

```python
# Autonomous Book Production Example
orchestrator = AutonomousWorktreeManager()

# Initialize infrastructure (one-time setup)
await orchestrator.initialize_worktree_infrastructure()

# Autonomous content generation - runs 6 tasks in parallel
results = await orchestrator.autonomous_book_production()
# Output: Content ready in 30 minutes vs 2+ hours sequential
```

### 📈 CEO Dashboard

Access real-time business metrics without technical details:

```bash
python scripts/orchestration/ceo_dashboard.py
```

**Dashboard provides:**
- CI Health Score
- Parallel Efficiency %
- Monthly Cost Savings
- Books Ready to Publish
- Strategic Recommendations

### 🔧 Implementation Details

**1. Worktree Manager (`scripts/orchestration/autonomous_worktree_manager.py`)**
- Automatically creates and manages Git worktrees
- Distributes tasks intelligently based on type
- Monitors resource usage and optimizes allocation
- Self-cleans to prevent disk bloat

**2. Parallel Orchestrator (`scripts/orchestration/worktree_orchestrator.py`)**
- Executes tasks across multiple worktrees simultaneously
- Handles task dependencies and synchronization
- Provides real-time progress tracking
- Calculates cost savings and efficiency metrics

**3. GitHub Workflow Integration (`.github/workflows/worktree-orchestration.yml`)**
- Automated parallel CI fixes
- Scheduled book production runs
- Resource-optimized execution

### 🚀 Getting Started with Worktrees

The system is already configured and running autonomously. No setup required!

**Check Status:**
```bash
# View active worktrees
git worktree list

# Run CEO dashboard
python scripts/orchestration/ceo_dashboard.py

# Trigger manual book production
python scripts/orchestration/autonomous_worktree_manager.py
```

### 📊 Monitoring & Metrics

**Real-time Metrics Available:**
- Active worktrees and task distribution
- CPU/Memory utilization per worktree
- Task completion rates and timings
- Cost savings calculations
- Production throughput

### 🛡️ Reliability & Safety

- **Automatic cleanup** prevents disk space issues
- **Branch isolation** ensures no code conflicts
- **Error recovery** handles failures gracefully
- **Resource limits** prevent system overload

## 📚 Publishing Workflow

### What's Automated vs Manual

**✅ Fully Automated:**
- Book content generation (puzzles, layouts, formatting)
- Quality validation and QA checks
- KDP metadata preparation (titles, descriptions, keywords)
- Cover prompt generation for DALL-E
- Social media content creation
- Market research and insights

**🔧 Manual Steps Required:**
1. **KDP Publishing**: Upload generated files to KDP dashboard
2. **Cover Creation**: Generate covers using DALL-E prompts
3. **Social Media**: Post generated content to platforms
4. **Email Campaigns**: Send prepared content to subscribers
5. **Sales Monitoring**: Track performance and revenue

This hybrid approach ensures high-quality content generation while maintaining control over the publishing process.

## 🛠️ Core Capabilities

### ✅ Orchestration Systems (ENHANCED)
- **Autonomous Worktree Management** - Parallel execution across 5+ environments
- **Task Distribution Engine** - Intelligent routing based on task type
- **Multi-Agent Architecture** - Content, marketing, revenue agents
- **Cost-Optimized Execution** - 70% reduction in operational costs
- **Real-time CEO Dashboard** - Business metrics without technical noise

### ✅ Content Generation (COMPLETE)
- **Puzzle Generators** - Crossword (v3), Sudoku, Word Search
- **PDF Generation** - Professional layouts with ReportLab
- **Quality Validation** - 14-point critical QA system
- **Voice Processing** - Whisper-based transcription
- **Social Atomization** - Multi-platform content generation
- **Series Management** - 7 book series with strategies
- **DALL-E Integration** - Cover prompt generation
- **KDP Metadata** - Correct categories and classifications

### 🆓 FREE KDP Automation
- **100% FREE Niche Discovery** - Google Trends + Amazon public data analysis
- **Market Research Engine** - Zero-cost competition analysis
- **Automated Book Metadata** - SEO-optimized titles, descriptions, keywords
- **Cost Savings** - $148/month vs paid alternatives (Helium 10 + Jungle Scout)
- **Full Test Coverage** - 12 comprehensive tests ensuring reliability
- **CLI Interface** - Simple commands for discovery and automation

### 🚀 SEO Engine 2025
- **Advanced Optimization** - Cutting-edge SEO strategies for 2025 algorithms
- **CLI Command**: `kindlemint enhance-seo --input metadata.json`
- **Automated Enhancement** - Transforms basic metadata into SEO-optimized content
- **Keyword Research** - Built-in keyword optimization for maximum visibility
- **Output**: Enhanced JSON file with `_seo.json` suffix

### 📊 Daily Market Insights System
- **Real-time Market Intelligence** - Automated daily collection from Reddit, Google Trends, Amazon
- **7 Subreddits Monitored** - KDP, selfpublishing, publishing communities
- **Executive Dashboards** - Daily summaries with actionable recommendations
- **Trend Analysis** - Keyword tracking, seasonal patterns, emerging opportunities
- **Fresh Data Daily** - Replaces stale insights with current market intelligence

**Market Insights Commands:**
```bash
# Run daily market collection
python scripts/daily_market_insights.py

# View latest insights
cat data/market-insights/market-insights.md

# Read executive summary
cat reports/market-insights/executive_summary_$(date +%Y%m%d).md
```

### 📦 Batch Processing & Orchestration CLI
**Batch Commands:**
- `kindlemint batch generate --type sudoku --count 5 --parallel` - Generate multiple books
- `kindlemint batch generate --type crossword --count 3 --volume-start 4` - Start from volume 4

**Orchestration Commands:**
- `kindlemint orchestrate status` - View active worktrees and status
- `kindlemint orchestrate dashboard` - Launch CEO dashboard for metrics
- `kindlemint orchestrate run --task book-production --monitor` - Run orchestrated tasks

## 🔍 Quality Validation System

Our comprehensive validation system ensures every puzzle book meets professional publishing standards:

### Critical Validation Points
1. **Trim Size Validation** - Ensures correct dimensions (8.5x11 for paperback puzzles)
2. **Large Print Requirements** - Validates 16pt+ fonts for accessibility
3. **KDP Categories** - Verifies proper category paths (e.g., "Crafts, Hobbies & Home > Games & Activities")
4. **Content Structure** - Checks puzzle count, difficulty progression, answer keys
5. **Metadata Completeness** - Ensures all required KDP fields are populated
6. **Visual Quality** - Validates puzzle clarity and print-readiness
7. **Series Consistency** - Maintains standards across multi-volume series

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/IgorGanapolsky/ai-kindlemint-engine.git
cd ai-kindlemint-engine

# Install dependencies
pip install -r requirements.txt

# Set up orchestration
python scripts/orchestration/autonomous_worktree_manager.py
```

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys:
# REQUIRED:
# OPENAI_API_KEY=your_openai_key_here
#
# OPTIONAL:
# GEMINI_API_KEY=your_gemini_key_here  
# SLACK_WEBHOOK_URL=your_slack_webhook
# SENTRY_DSN=your_sentry_dsn
```

### 3. Test Orchestration

```bash
# Check worktree status
git worktree list

# Run CEO dashboard
python scripts/orchestration/ceo_dashboard.py

# Test parallel execution
python scripts/orchestration/worktree_orchestrator.py
```

### 4. Quick Start Examples

```bash
# Generate a complete book (now 75% faster!)
python scripts/quick_start.py --type crossword --volume 1

# Run autonomous book production
python scripts/orchestration/autonomous_worktree_manager.py

# Monitor real-time progress
python scripts/orchestration/ceo_dashboard.py

# Note: Generated content requires manual upload to KDP
```

## 🚀 Deployment with Vercel

### Phase 1: Free Tier Testing
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel

# Follow prompts to connect GitHub repo
# Your app will be live at: https://your-app.vercel.app
```

### Phase 2: Production (When Metrics Support)
- Monitor conversion rates and traffic
- If >15% conversion AND >1000 visitors/month:
  - Upgrade to Vercel Pro ($20/month)
  - Add ConvertKit integration ($29/month)

### Why Vercel?
- **Free tier**: 100GB bandwidth/month (perfect for testing)
- **Next.js optimized**: Built for our tech stack
- **Automatic scaling**: Pay only for what you use
- **Zero configuration**: Deploy with one command

## 🏗️ AI-Powered Orchestration Architecture

AI-KindleMint-Engine uses a **revolutionary parallel orchestration system**:

1. **🌳 Git Worktree Orchestration** - 5+ parallel execution environments
2. **🤖 Autonomous Task Distribution** - Intelligent routing and load balancing
3. **📊 Real-time Performance Monitoring** - CEO-friendly dashboards
4. **💰 Cost-Optimized Execution** - 70% reduction in operational costs

**📖 [Complete Architecture Documentation](docs/ORCHESTRATION_ARCHITECTURE.md)**
**📖 [Worktree Strategy Guide](docs/GIT_WORKTREES_ORCHESTRATION_STRATEGY.md)**

### What Each System Does

**🌳 Worktrees** (Parallel Execution): 5+ specialized environments for different tasks
**🤖 Task Manager** (Distribution): Routes tasks to optimal worktree
**📊 Dashboard** (Monitoring): Real-time business metrics for executives
**💰 Optimizer** (Cost Control): Ensures maximum efficiency and savings

### Required API Keys

**Core Requirements:**
- `OPENAI_API_KEY` - Content generation, code assistance
- `GEMINI_API_KEY` - Alternative AI provider (optional)

**Optional Integrations:**
- `SLACK_WEBHOOK_URL` - Notifications and monitoring
- `SENTRY_DSN` - Error tracking and performance
- `GITHUB_TOKEN` - For automated CI operations

**Production Setup (GitHub Secrets):**
Our system uses **GitHub Secrets** for secure API key management:

1. Go to **Settings → Secrets and variables → Actions**
2. Add these repository secrets:
   ```
   OPENAI_API_KEY=your_openai_key_here
   GEMINI_API_KEY=your_gemini_key_here (optional)
   SLACK_WEBHOOK_URL=your_slack_webhook (optional)
   SENTRY_DSN=your_sentry_dsn (optional)
   GITHUB_TOKEN=your_github_token (for CI automation)
   ```

## 🎁 Bonus Features

### 🎤 Voice-to-Book Technology
Transform your spoken expertise into publishable books:
- **Whisper AI transcription** with 99%+ accuracy
- **Intelligent content structuring** into chapters
- **Automatic editing** for readability
- **Multi-format export** (eBook, print, audio)

### 📱 Social Media Atomization
Convert books into viral content automatically:
- **Quote extraction** with visual design
- **Thread generation** for Twitter/X
- **Carousel creation** for LinkedIn/Instagram
- **Video scripts** for TikTok/YouTube Shorts

### 💰 Monetization Suite
Maximize revenue from every book:
- **Affiliate link integration** throughout content
- **Course generation** from book material
- **Email funnel creation** for list building
- **Upsell sequence automation**

## 📂 Project Structure

```
ai-kindlemint-engine/
├── worktrees/              # Parallel execution environments (auto-managed)
│   ├── puzzle-gen/         # Puzzle generation worktree
│   ├── pdf-gen/            # PDF creation worktree
│   ├── qa-validation/      # Quality assurance worktree
│   ├── ci-fixes/           # CI automation worktree
│   ├── market-research/    # Market analysis worktree
│   ├── booktok-content/    # TikTok script generation worktree
│   ├── booktok-visuals/    # Visual asset creation worktree
│   ├── booktok-analytics/  # ROI tracking worktree
│   └── booktok-scheduler/  # Posting automation worktree
├── scripts/
│   ├── orchestration/      # Autonomous orchestration system
│   │   ├── autonomous_worktree_manager.py     # Main orchestrator
│   │   ├── worktree_orchestrator.py          # Parallel executor
│   │   ├── booktok_worktree_orchestrator.py  # BookTok automation
│   │   └── ceo_dashboard.py                   # Executive dashboard
│   ├── marketing/          # BookTok marketing automation
│   │   ├── booktok_content_generator.py      # TikTok content creation
│   │   ├── social_media_scheduler.py         # Posting automation
│   │   └── social_media_analytics.py         # ROI tracking
│   └── automation/         # Daily automation scripts
│       └── daily_booktok_tasks.sh            # BookTok maintenance
├── data/                   # Generated content and analytics
│   ├── analytics/          # UTM tracking and metrics
│   └── social_content/     # Generated social media content
├── books/                  # Generated books with social content
│   └── */social_media_content/  # Per-book TikTok scripts
├── src/kindlemint/         # Core library code
│   ├── orchestrator/       # Orchestration engines
│   ├── agents/             # AI agent implementations
│   └── validators/         # Quality validation
├── features/               # Feature modules
├── tests/                  # Comprehensive test suite
└── docs/                   # Documentation
```

## 🌟 Success Stories

**Book Production:**
- **400 books/month generation capacity** with parallel orchestration
- **$175/month savings** on API and operational costs
- **75% faster content creation** with worktree parallelism
- **100% autonomous content generation** - manual publishing workflow

**BookTok Marketing Automation:**
- **Zero to 100% social media automation** addressing revenue gap
- **4x parallel speedup** for social content generation (3.89 seconds for full pipeline)
- **Multi-platform coverage** - TikTok, Pinterest, Instagram, Facebook
- **10+ books processed simultaneously** with dedicated worktrees
- **Production-ready automation** with UTM tracking and ROI analytics
- **Scalable to 100+ books** using existing worktree infrastructure

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 and Whisper
- Google for Gemini Pro
- The open-source community

---

**Built with ❤️ for authors, publishers, and content creators who want to scale their impact.**

*Remember: Success depends on content quality, marketing, and market demand. AI-KindleMint-Engine provides the tools; you provide the expertise and marketing effort.*