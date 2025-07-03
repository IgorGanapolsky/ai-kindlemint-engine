# 📊 Worktree Orchestration Badge System

## Overview

The Orchestration Badge System provides real-time visibility into cost savings achieved through our parallel worktree execution strategy. This system replaces the generic cost tracking badges with meaningful orchestration-specific metrics.

## Badges Displayed

### 1. MTD Cost Badge
- **Shows**: Actual month-to-date costs incurred
- **Color**: Green if under $50/month budget, yellow otherwise
- **Format**: `MTD Cost: $XX.XX`

### 2. Orchestration Savings Badge  
- **Shows**: Amount saved through orchestration (in dollars and percentage)
- **Color**: Based on savings percentage:
  - Bright Green: ≥50% savings
  - Green: ≥30% savings
  - Yellow: ≥10% savings
  - Orange: >0% savings
  - Grey: No savings yet
- **Format**: `Orchestration Savings: $XX.XX (XX%)`

## How It Works

### 1. Metrics Collection
The system tracks commits made from:
- Main branch (traditional method)
- Worktree branches (orchestrated method)

### 2. Cost Calculation
- **Traditional commits**: ~50,000 tokens per commit
- **Orchestrated commits**: ~20,000 tokens per commit (60% reduction)
- **Cost**: $0.01 per 1,000 tokens (Claude API pricing)

### 3. Automatic Updates
- Post-commit hooks update metrics when commits are made
- Badges refresh automatically to show current data
- Monthly aggregation provides trend analysis

## File Structure

```
scripts/
├── orchestration_metrics_aggregator.py  # Collects and aggregates metrics
├── generate_orchestration_badges.py     # Creates badge URLs and updates README
└── .git/hooks/post-commit              # Auto-updates on commit

reports/orchestration/
├── aggregated_metrics.json             # Raw metrics data
└── README.md                           # Detailed savings report
```

## Implementation Details

### Metrics Aggregator
```python
# Tracks commit patterns
- Counts commits from main vs worktrees
- Calculates token usage for each
- Computes cost savings
```

### Badge Generator
```python
# Creates visual badges
- Generates shields.io URLs
- Updates README.md
- Creates detailed reports
```

### Git Hook Integration
```bash
# Auto-updates on commit
- Detects worktree commits
- Triggers badge regeneration
- Runs asynchronously
```

## Viewing Metrics

### Quick View
The badges in README.md show at-a-glance metrics.

### Detailed Report
Click on any badge to view the full report at `reports/orchestration/README.md`

### Raw Data
Access `reports/orchestration/aggregated_metrics.json` for programmatic use.

## Benefits

1. **Transparency**: See exactly how much orchestration saves
2. **Motivation**: Encourages worktree usage with visible savings
3. **ROI Tracking**: Proves the value of the orchestration system
4. **Real-time**: Updates automatically with each commit

## Future Enhancements

- Weekly/monthly trend charts
- Per-worktree efficiency metrics
- Team leaderboards for orchestration usage
- Projected annual savings calculator

## Maintenance & Rotation

The badge system includes automatic maintenance features:

### Monthly Metrics Rotation
- **Automatic Archival**: On the 1st of each month, commit metrics files are archived
- **Archive Location**: `reports/orchestration/archive/YYYY-MM/`
- **Retention Period**: Archives kept for 3 months then auto-deleted
- **Preserved Data**: `aggregated_metrics.json` is never rotated (contains all historical data)

### Manual Rotation Commands
```bash
# Check if rotation is needed
python scripts/orchestration/metrics_rotation.py --check

# Force rotation (useful for testing)
python scripts/orchestration/metrics_rotation.py --force
```

### Benefits of Rotation
1. **Clean Repository**: Prevents accumulation of thousands of JSON files
2. **Performance**: Faster git operations without excessive files
3. **Organization**: Easy to find metrics from specific months
4. **Automatic**: No manual cleanup required

---

*The orchestration badge system demonstrates the tangible value of parallel execution through clear, data-driven metrics.*