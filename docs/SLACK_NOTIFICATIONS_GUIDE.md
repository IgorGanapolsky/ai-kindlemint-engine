# Slack Notifications Guide

## Overview

The AI KindleMint Engine sends enhanced Slack notifications for CI/CD workflows to provide better visibility into book production quality and test results.

## Notification Types

### 1. Production QA Validation

Sent when books in `books/active_production` are validated for production readiness.

**What it shows:**
- **Full book path**: e.g., `Large_Print_Crossword_Masters/volume_4/paperback`
- **QA Score**: Score out of 100 with pass/fail status
- **Critical issues**: First 2 issues for failed books
- **Summary stats**: Total books validated, passed, and failed

**Example format:**
```
❌ Production QA Validation Results
Summary: 2 of 3 books not ready for production
Total Books: 3 | Ready: 1 | Failed: 2

📚 Book Status Details:
• ✅ Large_Print_Crossword_Masters/volume_3/paperback: Score 100/100 - Ready
• ❌ Large_Print_Crossword_Masters/volume_4/paperback: Score 75/100
    → Crossword grids appear to be missing or improperly rendered
• ❌ Large_Print_Crossword_Masters/volume_4/hardcover: Score 55/100
    → Crossword grids appear to be missing or improperly rendered
    → Nearly blank pages found: [5]

💡 Quick Reference:
• Score 75/100: Grid rendering detection issue (false positive)
• Score 55/100: Missing content or structural issues
• Score <50: Critical content problems
```

### 2. Book QA Validation

Sent when the enhanced QA validator checks book content quality.

**What it shows:**
- Book paths with PASS/FAIL status
- Overall QA scores
- Number of critical issues
- First 2 critical issues for failed books

### 3. Test Results

Sent after Python tests run (unit + integration).

**What it shows:**
- Python version tested
- Test suite type
- Pass/fail status
- Link to detailed test results

## Understanding QA Scores

### Common Score Ranges

- **100/100**: Perfect - All checks passed
- **75-99/100**: Minor issues or false positives
  - Grid rendering detection issues (validator limitation)
  - Minor formatting warnings
- **50-74/100**: Moderate issues
  - Missing content sections
  - Structural problems
  - Multiple warnings
- **0-49/100**: Critical issues
  - Placeholder content
  - Missing PDFs
  - Corrupted files
  - Major structural failures

### Common Issues

1. **"Crossword grids appear to be missing or improperly rendered"**
   - Often a false positive if grids are drawn directly on canvas
   - Score typically 55-75/100
   - Grids may be visually correct despite this error

2. **"Nearly blank pages found: [page numbers]"**
   - Indicates pages with insufficient content
   - Check if intentional (e.g., section breaks)

3. **"Placeholder clues detected"**
   - Real issue with crossword clue quality
   - Requires fixing clue generation

4. **"Test content found in metadata"**
   - Critical issue - production files contain test data
   - Must be fixed before publishing

## Notification Settings

### Webhook Configuration

Slack notifications are sent via webhook URL stored in GitHub Secrets:
- Secret name: `SLACK_WEBHOOK_URL`
- Configure in: Repository Settings → Secrets → Actions

### Workflow Triggers

Notifications are sent:
- On push to `books/active_production/**`
- On pull requests affecting production books
- On workflow completion (success or failure)
- Always sent, even if workflow fails

## Customization

### Adding More Context

To add more details to notifications, edit the workflow files:
- `.github/workflows/production_qa.yml`
- `.github/workflows/book_qa_validation.yml`

Key sections to modify:
1. Book details extraction
2. Issue formatting
3. Summary generation
4. Message payload structure

### Filtering Issues

To show more/fewer issues per book, adjust:
```bash
# Current: Shows first 2 issues
CRITICAL_ISSUES=$(jq -r '.critical_issues[0:2][]' "$report" 2>/dev/null | sed 's/^/    → /')

# To show first 5 issues:
CRITICAL_ISSUES=$(jq -r '.critical_issues[0:5][]' "$report" 2>/dev/null | sed 's/^/    → /')
```

## Troubleshooting

### No Notifications Received

1. Check if `SLACK_WEBHOOK_URL` is configured in GitHub Secrets
2. Verify webhook URL is valid and active
3. Check workflow logs for curl errors

### Missing Book Details

1. Ensure QA reports are generated (`qa_production_report.json`)
2. Check file paths in workflow match actual structure
3. Verify jq commands can parse report JSON

### Incorrect Scores

1. Check if using latest QA validator scripts
2. Ensure PDF files are properly generated
3. Review QA report JSON for detailed scoring breakdown

## Best Practices

1. **Review all failures**: Even if score is 75/100 (common false positive)
2. **Check detailed reports**: Click "View in GitHub" for full analysis
3. **Fix critical issues first**: Focus on scores below 50
4. **Update thresholds**: Adjust pass/fail criteria as needed
5. **Monitor trends**: Track if scores improve/degrade over time

## Future Enhancements

Planned improvements:
- [ ] Add graphs/charts for score trends
- [ ] Include preview images of failed pages
- [ ] Add one-click fix suggestions
- [ ] Integrate with issue creation
- [ ] Add @mentions for responsible developers
- [ ] Show diff between current and previous scores