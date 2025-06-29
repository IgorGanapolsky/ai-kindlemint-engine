# Claude Code Flow Integration Guide for KindleMint Engine

## Overview
`claude-code-flow` (ccf) is a powerful tool that provides instant, context-aware code reviews and assistance directly from your terminal. This guide shows how to integrate it into the KindleMint Engine development workflow.

## Installation

```bash
# Install using pipx (recommended for isolation)
pipx install claude-code-flow

# Or using pip
pip install claude-code-flow
```

## Configuration

1. Add to your `.env` file (already in .gitignore):
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

2. Source the environment:
```bash
source .env
```

## Key Use Cases for KindleMint Engine

### 1. Pre-Push Code Review for Puzzle Generators
Before pushing changes to crossword or sudoku generators:

```bash
# After modifying crossword_engine_v2.py
ccf "Review my changes to the crossword generator. Check for:
- Proper error handling for API failures
- Grid symmetry validation
- Solution completeness
- Any potential infinite loops in word placement"
```

### 2. QA Validator Reviews
Our QA validators are critical for book quality:

```bash
# After updating puzzle_validators.py
ccf "Review these QA validator changes. Ensure:
- All edge cases are covered
- Validation logic matches KDP requirements
- No false positives that would reject valid puzzles
- Proper handling of empty solutions"
```

### 3. Automated Commit Messages
Generate consistent, detailed commit messages:

```bash
# After fixing a bug in hardcover generation
ccf "Generate a conventional commit message for these changes. Context: Fixed spine width calculation for hardcover books over 200 pages"
```

Example output:
```
fix: correct spine width calculation for thick hardcover books

- Update spine formula to account for paper thickness variance
- Add bounds checking for page counts over 200
- Include test cases for edge scenarios
- Fixes issue where books >200 pages had incorrect spine width

Affects: scripts/hardcover/create_hardcover_package.py
```

### 4. Architecture Decisions
When implementing new features:

```bash
# Before implementing S3 storage
ccf "I want to replace Git LFS with S3 for artifact storage. Given the current structure in .gitattributes and the output/ directory usage, what's the best approach? Consider:
- Backward compatibility
- CI/CD integration
- Cost optimization
- Migration strategy"
```

### 5. Test Coverage Analysis
Before committing new tests:

```bash
# After writing new tests
ccf "Review my new test cases for the sudoku generator. Are there any edge cases I'm missing? Consider:
- Invalid puzzle configurations
- Performance with large batches
- Memory usage
- Thread safety"
```

### 6. Slack Notification Optimization
When updating workflows:

```bash
# After modifying .github/workflows/
ccf "Review my GitHub Actions workflow changes. The goal is to make Slack notifications more informative. Check for:
- Proper error handling
- Secret usage security
- Message formatting
- Performance impact"
```

## Workflow Integration

### Daily Development Flow
1. Make changes to your code
2. Run `ccf` for instant review before committing
3. Fix any issues identified
4. Generate commit message with `ccf`
5. Push with confidence

### Example Morning Routine
```bash
# Start work on Volume 4
cd books/active_production/Large_Print_Crossword_Masters/volume_4

# Make changes to generation script
vim generate_volume_4.py

# Get instant review
ccf "Review my volume 4 generation script. Check that it:
- Follows the same pattern as volumes 1-3
- Includes proper metadata
- Generates 50 unique puzzles
- Has correct difficulty progression"

# Fix issues, then generate commit message
ccf "Generate commit message for volume 4 generation script"

# Commit and push
git add .
git commit -m "<paste generated message>"
git push
```

## Cost Management

### Monitoring Usage
```bash
# Add to your .bashrc or .zshrc
alias ccf-stats='echo "Check Anthropic dashboard for usage"'
```

### Cost-Saving Tips
1. Be specific in your prompts to reduce token usage
2. Use for complex reviews, not simple syntax checks
3. Batch related questions into single prompts
4. Set up usage alerts in Anthropic dashboard

### Estimated Costs for KindleMint
- Average code review: ~$0.05-0.10
- Commit message generation: ~$0.02-0.05
- Architecture consultation: ~$0.10-0.20
- Monthly estimate (heavy usage): ~$50-100

## Security Considerations

### What Gets Sent
- File diffs
- Full file contents (when needed)
- Project structure
- Your prompt

### Best Practices
1. Never include `.env` files in reviews
2. Avoid reviewing files with API keys or secrets
3. Use project-specific API keys
4. Rotate keys regularly

### Excluded Patterns
Add to `.ccfignore` (if supported):
```
.env
*.key
*.pem
*_secret*
research/
output/
```

## Team Onboarding

### Quick Start for New Developers
1. Install ccf: `pipx install claude-code-flow`
2. Get API key from team lead
3. Add to `.env` file
4. Try: `ccf "Explain the crossword generation process in this codebase"`

### Recommended First Uses
- Code review before first PR
- Understanding existing code
- Generating documentation
- Writing test cases

## Integration with Existing Tools

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
echo "Running AI code review..."
ccf "Quick review of staged changes for obvious issues" || true
```

### VS Code Integration
Add to `.vscode/tasks.json`:
```json
{
  "label": "AI Code Review",
  "type": "shell",
  "command": "ccf \"Review current file changes\"",
  "group": "build"
}
```

## Specific KindleMint Use Cases

### 1. Puzzle Quality Checks
```bash
ccf "Review the crossword at puzzles/crossword_042.json. Check:
- All clues are appropriate and solvable
- No duplicate clues
- Grid has proper symmetry
- Solution matches the clues"
```

### 2. PDF Generation Review
```bash
ccf "Review my PDF generation changes. Ensure:
- Margins meet KDP requirements
- Fonts are embedded
- Page numbers are correct
- No content is cut off"
```

### 3. Market Research Analysis
```bash
ccf "Analyze the market research data in research/2025-06-26/. What insights can you extract? What opportunities should we pursue?"
```

## Conclusion

`claude-code-flow` can significantly accelerate development on KindleMint Engine by:
- Catching bugs before they reach production
- Maintaining code quality standards
- Reducing review cycle time
- Helping developers learn the codebase faster

Start with simple code reviews and gradually expand usage as you become comfortable with the tool.
