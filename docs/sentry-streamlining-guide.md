# Sentry Integration Streamlining Guide

Based on the article about Sentry's new AI features (test generation and PR review), here's a comprehensive plan to streamline your Sentry integration.

## Current State Analysis

Your project already has:
- ✅ Sentry SDK integrated with error tracking (`sentry_config.py`)
- ✅ Advanced monitoring system (`sentry_monitor.py`)
- ✅ Custom error categorization and pattern analysis
- ✅ GitHub Actions workflows for CI/CD
- ✅ Environment-specific configuration (DSN in `.env`)

## Recommendations for Streamlining

### 1. Enable Sentry Seer GitHub App (Critical)

**Action Items:**
- Install the Sentry Seer GitHub App from the GitHub Marketplace
- Ensure it has access to your repository
- Verify integration by checking GitHub → Settings → Installed Apps

```bash
# Verify the app is working by commenting on any PR:
@sentry test-connection
```

### 2. Implement AI-Powered Test Generation

**Strategy for using `@sentry generate-test`:**

1. **Focus on Critical Paths**: Use test generation for:
   - New puzzle generation algorithms
   - PDF generation logic  
   - KDP metadata processing
   - Error handling code

2. **Integration Points**: Add to your PR workflow:
   ```yaml
   # Add to .github/workflows/tests.yml
   on:
     pull_request_comment:
       types: [created]
   ```

3. **Usage Guidelines**:
   - Comment `@sentry generate-test` after pushing significant logic changes
   - Review generated tests for:
     - Edge case coverage
     - Mock appropriateness
     - Integration with existing test suite

### 3. Leverage AI PR Reviews

**When to use `@sentry review`:**

1. **High-Risk Changes**:
   - Modifications to `batch_processor.py`
   - Changes to PDF generation logic
   - Updates to KDP automation scripts

2. **Complex Refactoring**:
   - Architecture changes
   - Dependency updates
   - Performance optimizations

3. **Review Checklist**:
   ```markdown
   - [ ] Run `@sentry review` before human review
   - [ ] Address security concerns flagged by Sentry
   - [ ] Verify dependency changes are intentional
   - [ ] Check for potential performance regressions
   ```

### 4. Enhance Current Sentry Configuration

Update `scripts/sentry_config.py`:

```python
# Add Seer AI optimization flags
def init_sentry(script_name: str = "kindlemint-script"):
    """Initialize Sentry with Seer AI-optimized configuration"""
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=os.getenv("ENVIRONMENT", "production"),
        release=f"kindlemint@{os.getenv('GITHUB_SHA', 'local')[:8]}",
        
        # Enhanced for Seer AI
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        
        # Add code context for better AI analysis
        include_source_context=True,
        
        # Enable session tracking for better error correlation
        auto_session_tracking=True,
        
        # Seer AI optimization
        _experiments={
            "profiles_sample_rate": 1.0,
            "enable_metrics": True,  # New metrics API
        },
        
        # Add beforeSend hook for PII scrubbing
        before_send=scrub_sensitive_data,
    )

def scrub_sensitive_data(event, hint):
    """Remove sensitive KDP data before sending to Sentry"""
    # Scrub KDP credentials
    if 'extra' in event:
        event['extra'] = {k: v for k, v in event['extra'].items() 
                         if 'password' not in k.lower() and 'key' not in k.lower()}
    return event
```

### 5. Create Team Workflow Documentation

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Generated tests reviewed (if applicable)

## Sentry AI Tools
- [ ] Run `@sentry generate-test` for new logic
- [ ] Run `@sentry review` before merge
- [ ] Address all Sentry AI suggestions

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

### 6. Integrate with Existing Monitoring

Update `scripts/alert_orchestration/sentry_monitor.py` to track AI tool usage:

```python
def track_sentry_ai_usage(pr_number: int, tool: str, result: str):
    """Track Sentry AI tool usage for analytics"""
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("sentry_ai_tool", tool)
        scope.set_tag("pr_number", pr_number)
        scope.set_context("ai_tool_result", {
            "tool": tool,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
```

### 7. CI/CD Integration

Add to `.github/workflows/tests.yml`:

```yaml
  sentry-ai-check:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - name: Comment for Sentry AI Review
        uses: actions/github-script@v6
        with:
          script: |
            const comment = '@sentry review';
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### 8. Monitoring Dashboard Updates

Add Sentry AI metrics to your monitoring dashboard:
- Test coverage improvements from AI-generated tests
- PR review turnaround time with AI assistance
- Error reduction rate after implementing AI suggestions

## Implementation Timeline

1. **Week 1**: Install Sentry Seer GitHub App and verify
2. **Week 2**: Train team on `@sentry` commands
3. **Week 3**: Implement PR templates and workflow updates
4. **Week 4**: Review metrics and adjust strategy

## Best Practices

1. **Don't rely solely on AI**: Use as a supplement to human review
2. **Review generated tests**: Ensure they match your testing standards
3. **Track effectiveness**: Monitor if AI suggestions reduce production errors
4. **Iterate on feedback**: Use 👍/👎 reactions to improve AI suggestions
5. **Security first**: Always review AI suggestions for security implications

## Success Metrics

- 30% reduction in bugs reaching production
- 50% improvement in test coverage
- 25% faster PR review cycle
- Reduced time spent writing boilerplate tests

## Next Steps

1. Install Sentry Seer GitHub App
2. Update team documentation
3. Run pilot program with select PRs
4. Gather feedback and iterate
5. Roll out to entire team