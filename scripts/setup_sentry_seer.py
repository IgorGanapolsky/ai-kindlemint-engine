#!/usr/bin/env python3
"""
Setup script for Sentry Seer AI integration
Helps configure and verify the Sentry AI features for the project
"""

import os
import subprocess
import sys
from pathlib import Path

    """Check Sentry Config"""
def check_sentry_config():
    """Verify Sentry is properly configured"""
    print("🔍 Checking Sentry configuration...")

    # Check for DSN
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        print("❌ SENTRY_DSN not found in environment")
        return False

    print("✅ Sentry DSN configured")

    # Check for sentry-sdk
    try:
        import sentry_sdk

        print(f"✅ sentry-sdk version: {sentry_sdk.VERSION}")
    except ImportError:
        print("❌ sentry-sdk not installed")
        return False

    return True


    """Check Github App"""
def check_github_app():
    """Check if Sentry Seer GitHub App is accessible"""
    print("\n🔍 Checking GitHub integration...")

    # Check if we're in a git repo
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ Git repository: {result.stdout.strip()}")
        else:
            print("❌ Not in a git repository")
            return False
    except BaseException:
        print("❌ Git not available")
        return False

    print("\n📝 Next steps for GitHub App:")
    print("1. Go to: https://github.com/apps/sentry-seer")
    print("2. Click 'Install' or 'Configure'")
    print("3. Select your repository")
    print("4. Grant necessary permissions")

    return True


    """Create Pr Workflow"""
def create_pr_workflow():
    """Create or update PR workflow for Sentry AI"""
    print("\n🔧 Setting up PR workflow...")

    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)

    sentry_workflow = workflow_dir / "sentry-ai-assist.yml"

    workflow_content = """name: Sentry AI Assistance

on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]

jobs:
  notify-sentry-ai:
    if: |
      (github.event_name == 'pull_request' && github.event.action == 'opened') ||
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@sentry'))
    runs-on: ubuntu-latest
    steps:
      - name: Acknowledge Sentry AI Request
        uses: actions/github-script@v6
        with:
          script: |
            const isPR = context.eventName === 'pull_request';
            const isComment = context.eventName === 'issue_comment';

            if (isPR) {
              // Add label to indicate Sentry AI can be used
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                labels: ['sentry-ai-ready']
              });
            }

            if (isComment && context.payload.comment.body.includes('@sentry')) {
              // Add reaction to acknowledge command
              await github.rest.reactions.createForIssueComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                comment_id: context.payload.comment.id,
                content: 'eyes'
              });
            }
"""

    with open(sentry_workflow, "w") as f:
        f.write(workflow_content)

    print(f"✅ Created workflow: {sentry_workflow}")
    return True


    """Create Documentation"""
def create_documentation():
    """Create team documentation for Sentry AI usage"""
    print("\n📚 Creating documentation...")

    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    quickstart = docs_dir / "sentry-ai-quickstart.md"

    quickstart_content = """# Sentry AI Quick Start Guide

## Available Commands

### Generate Tests
```
@sentry generate-test
```
Use this on any PR to automatically generate unit tests for your changes.

### Get PR Review
```
@sentry review
```
Use this to get an AI-powered code review with suggestions.

## Best Practices

1. **For New Features**: Always run `@sentry generate-test` after implementing
2. **For Bug Fixes**: Use `@sentry review` to catch related issues
3. **For Refactoring**: Both commands help ensure nothing breaks

## Examples

### Example 1: New Function
```python
# After adding a new puzzle generator function
# Comment: @sentry generate-test
# Sentry will create comprehensive tests including edge cases
```

### Example 2: Complex Changes
```python
# After refactoring PDF generation logic
# Comment: @sentry review
# Sentry will analyze for potential issues and suggest improvements
```

## Tips

- Wait for Sentry's 👀 reaction before assuming it's processing
- Review all generated tests before committing
- Use 👍/👎 on Sentry's suggestions to improve future results
- Combine both commands for maximum coverage

## Troubleshooting

If Sentry doesn't respond:
1. Check if Sentry Seer GitHub App is installed
2. Ensure you're commenting on a PR, not an issue
3. Verify the repository has the app permissions
"""

    with open(quickstart, "w") as f:
        f.write(quickstart_content)

    print(f"✅ Created documentation: {quickstart}")
    return True


    """Main"""
def main():
    """Main setup process"""
    print("🚀 Sentry Seer AI Setup Script")
    print("=" * 50)

    # Check prerequisites
    if not check_sentry_config():
        print("\n❌ Please configure Sentry first")
        sys.exit(1)

    # GitHub app instructions
    check_github_app()

    # Setup automation
    create_pr_workflow()
    create_documentation()

    print("\n✨ Setup complete!")
    print("\n📋 Checklist:")
    print("1. [ ] Install Sentry Seer GitHub App")
    print("2. [ ] Test with: @sentry help (on any PR)")
    print("3. [ ] Share docs/sentry-ai-quickstart.md with team")
    print("4. [ ] Update CLAUDE.md with Sentry AI commands")

    print("\n🎯 Quick Test:")
    print("1. Create a test PR")
    print("2. Comment: @sentry review")
    print("3. Wait for AI analysis")
    print("4. Try: @sentry generate-test")


if __name__ == "__main__":
    main()
