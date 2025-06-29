# Claude API Cost Tracking System

This system automatically tracks Claude API usage costs for your repository, providing insights into API expenses per commit and helping optimize Claude usage.

## Features

- **Automatic Cost Tracking**: Pre-commit hook automatically calculates costs for changed files
- **Token Estimation**: Analyzes file complexity and estimates token usage
- **Model-Specific Pricing**: Supports all Claude models (Opus, Sonnet, Haiku)
- **Repository Analysis**: Compares worktree costs vs full repository costs
- **Historical Tracking**: Maintains commit history with associated costs
- **Export Capabilities**: Export data to CSV or JSON for further analysis

## Installation

The cost tracking system is already installed. To verify:

```bash
./claude-flow-costs status
```

## File Structure

- `commit_costs.json` - Historical commit cost data
- `last_commit_cost.json` - Latest commit analysis
- `scripts/claude_cost_tracker.py` - Core tracking module
- `scripts/claude_costs.py` - User-friendly CLI interface
- `.git/hooks/pre-commit` - Git hook for automatic tracking

## Usage

### Basic Commands

```bash
# Check current status
./claude-flow-costs status

# View cost summary (last 30 days)
./claude-flow-costs summary

# View last 7 days
./claude-flow-costs summary --days 7

# Show detailed commit history
./claude-flow-costs details --last 10

# Export data
./claude-flow-costs export costs.csv
./claude-flow-costs export costs.json
```

### Manual Tracking

If you need to manually track changes:

```bash
# Track with default model (Sonnet)
./claude-flow-costs track

# Track with specific model
./claude-flow-costs track --model claude-3-opus
```

## Cost Calculation

The system estimates costs based on:

1. **File Content Analysis**: Counts tokens in changed files
2. **Complexity Assessment**:
   - Low: Simple files (1.5x output multiplier)
   - Medium: Moderate complexity (2.5x output multiplier)
   - High: Complex code files (4.0x output multiplier)
3. **Model Pricing**: Uses official Claude API pricing

### Current Pricing (per million tokens)

| Model | Input | Output |
|-------|--------|---------|
| Claude 3 Opus | $15.00 | $75.00 |
| Claude 3 Sonnet | $3.00 | $15.00 |
| Claude 3 Haiku | $0.25 | $1.25 |

## Automatic Tracking

Every git commit automatically:
1. Analyzes changed files
2. Estimates token usage and costs
3. Updates `commit_costs.json` and `last_commit_cost.json`
4. Includes cost files in the commit

## Understanding the Output

### Status Output
```
📊 Claude Cost Tracking Status
==================================================
Total tracked cost: $0.3250        # Cumulative cost
Commits tracked: 2                 # Number of commits
Last commit:
  Hash: c08cdbab
  Cost: $0.1790                   # Cost for this commit
  Files: 2                        # Files changed

Repository Analysis:
  Full repo cost estimate: $7.34   # If entire repo was processed
  Last worktree cost: $0.1790      # Actual cost (only changes)
  Savings potential: $7.17         # Saved by processing only changes
```

### Cost Optimization Tips

1. **Batch Changes**: Group related changes into single commits
2. **Focus on Modified Files**: The system only analyzes changed files
3. **Use Appropriate Models**:
   - Haiku for simple tasks
   - Sonnet for general development
   - Opus for complex analysis
4. **Monitor Expensive Files**: Use `details` command to identify costly files

## Troubleshooting

### Cost tracking not working?

1. Ensure Python 3 is installed: `python3 --version`
2. Check hook is executable: `ls -la .git/hooks/pre-commit`
3. Verify files exist: `ls -la *.json`

### Reset tracking data

```bash
rm commit_costs.json last_commit_cost.json
./claude-flow-costs init
```

## Integration with CI/CD

Add to your CI pipeline:

```yaml
- name: Check Claude Costs
  run: |
    ./claude-flow-costs summary --days 7
    # Fail if weekly cost exceeds $50
    cost=$(./claude-flow-costs summary --days 7 | grep "Total cost" | awk '{print $3}' | tr -d '$')
    if (( $(echo "$cost > 50" | bc -l) )); then
      echo "Weekly Claude costs exceeded $50!"
      exit 1
    fi
```

## Data Privacy

- All cost data is stored locally in your repository
- No data is sent to external services
- Cost calculations are estimates based on token counting
- Actual API costs may vary slightly

## Contributing

To improve cost estimation accuracy:
1. Compare estimated vs actual API costs
2. Adjust complexity multipliers in `claude_cost_tracker.py`
3. Submit PRs with improved token counting algorithms
