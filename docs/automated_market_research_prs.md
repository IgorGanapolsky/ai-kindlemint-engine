# Automated Market Research PR System

## Overview

The automated market research PR system eliminates manual review of daily market research reports by using AI-driven decision making to analyze opportunities and trigger content generation automatically.

## How It Works

### 1. Daily Market Research Generation
- Automated scripts run daily to analyze market trends
- Results are compiled into:
  - `market_analysis.csv` - Raw market data
  - `summary.json` - Processed insights with opportunity scores
  - `report.md` - Human-readable report
- A PR is automatically created with these files

### 2. Automated PR Analysis
When a market research PR is created, the system:

1. **Analyzes Opportunities**
   - Calculates opportunity scores based on:
     - Market size (30% weight)
     - Competition level (30% weight)
     - Market trend (20% weight)
     - Profit margin (20% weight)
   - Filters opportunities with score >= 0.7

2. **Makes Decisions**
   - **Auto-merge** if:
     - At least 3 viable opportunities found
     - Top opportunity score >= 0.8
     - Rising market trends detected
   - **Request manual review** if criteria not met

3. **Executes Actions**
   - Creates content generation tasks for selected niches
   - Triggers content generation swarm
   - Auto-merges the PR
   - Updates research database

## Components

### 1. Market Research Auto-Reviewer (`market_research_auto_reviewer.py`)
Main decision engine that:
- Analyzes market research files
- Calculates opportunity scores
- Selects top niches (max 5 per day)
- Creates content generation tasks

### 2. GitHub Actions Workflow (`auto_review_market_research.yml`)
Automation that:
- Triggers on market research PRs
- Runs the auto-reviewer
- Posts analysis comments
- Auto-merges if approved
- Triggers content generation

### 3. Claude-Flow Integration (`claude_flow_market_pr_handler.py`)
Advanced orchestration using Claude-Flow:
- Uses SPARC analyzer mode for deeper insights
- Coordinates multi-agent swarms
- Manages distributed content generation

### 4. End-to-End Pipeline (`market_to_publish_pipeline.py`)
Complete orchestration from market research to publishing:
- 7-stage pipeline
- Async execution
- Comprehensive error handling
- Result tracking

## Configuration

### Opportunity Scoring Thresholds
```python
min_opportunity_score = 0.7  # Minimum score to consider
max_niches_per_day = 5      # Maximum niches to pursue daily
```

### Market Criteria
```python
required_criteria = {
    'market_size': 1000,     # Minimum market size
    'competition': 'low',    # Maximum competition level
    'trend': 'rising'        # Required trend direction
}
```

## Usage

### Manual Execution
```bash
# Review a specific PR
python scripts/market_research_auto_reviewer.py --pr 123

# Run in fully automated mode
python scripts/market_research_auto_reviewer.py --auto

# Use Claude-Flow integration
python scripts/claude_flow_market_pr_handler.py 123
```

### Automated Execution
The system runs automatically via GitHub Actions when:
- A PR is created with market research files
- Manual workflow dispatch is triggered

### Full Pipeline Execution
```bash
# Run complete market-to-publish pipeline
python scripts/orchestration/market_to_publish_pipeline.py
```

## Decision Logic

### Auto-Merge Criteria
```
IF viable_niches >= 3 AND top_score >= 0.8:
    auto_merge = True
    selected_niches = top 5 opportunities
    create_content_tasks()
    merge_pr()
ELSE:
    request_manual_review()
```

### Opportunity Score Calculation
```
score = (market_size_score * 0.3) +
        (competition_score * 0.3) +
        (trend_score * 0.2) +
        (profitability_score * 0.2)
```

## Content Generation Tasks

When opportunities are selected, the system creates tasks with:
- Unique task ID
- Niche name and metrics
- Priority (high if score >= 0.9)
- Creation timestamp
- Status tracking

Tasks are saved to `tasks/content_generation_queue.json` for processing.

## Monitoring

### PR Comments
The system posts detailed analysis comments including:
- Decision reasoning
- Selected niches with scores
- Actions to be executed
- Manual review requirements (if applicable)

### Pipeline Results
Complete pipeline runs save results to:
```
pipeline_results/pipeline_run_YYYYMMDD_HHMMSS.json
```

## Benefits

1. **Time Savings**: Eliminates 30+ minutes of daily manual review
2. **Consistency**: Applies same criteria to every analysis
3. **Speed**: Launches content generation within minutes
4. **Scalability**: Can handle multiple market reports simultaneously
5. **Traceability**: Full audit trail of decisions and actions

## Future Enhancements

1. **Machine Learning**: Train on historical success data
2. **A/B Testing**: Test different scoring algorithms
3. **Market Feedback Loop**: Incorporate sales data into scoring
4. **Dynamic Thresholds**: Adjust criteria based on performance
5. **Multi-Channel**: Extend beyond KDP to other platforms
