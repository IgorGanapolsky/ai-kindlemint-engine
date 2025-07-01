# 🚀 AI-KindleMint-Engine Development Workflow

## 📋 Table of Contents
1. [Overview](#overview)
2. [Branch Strategy](#branch-strategy)
3. [Development Process](#development-process)
4. [PR Guidelines](#pr-guidelines)
5. [Quality Standards](#quality-standards)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Emergency Procedures](#emergency-procedures)

## Overview

This document outlines our PR-based development workflow designed to maintain high code quality while enabling rapid development. **All changes must go through pull requests** - no direct commits to main.

## Branch Strategy

### Branch Naming Convention
```
feature/{ticket-id}-{description}  # New features
fix/{ticket-id}-{description}      # Bug fixes
hotfix/{ticket-id}-{description}   # Emergency fixes
chore/{description}                # Maintenance tasks
release/v{major}.{minor}.{patch}   # Release branches
exp/{experiment-name}              # Experiments
```

### Examples
```bash
feature/KM-123-add-epub-support
fix/KM-456-sudoku-validation-error
hotfix/KM-789-critical-pdf-crash
chore/update-dependencies
release/v1.2.0
exp/new-puzzle-algorithm
```

## Development Process

### 1. Starting New Work

```bash
# Always start from updated main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/KM-123-add-epub-support

# Set up pre-commit hooks (if not already done)
pre-commit install
```

### 2. Development Guidelines

#### Test-Driven Development (TDD)
1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor while keeping tests green

```python
# 1. Write test first
def test_epub_generator():
    generator = EpubGenerator()
    result = generator.create_book(title="Test Book")
    assert result.format == "epub"
    assert result.is_valid()

# 2. Implement feature
class EpubGenerator:
    def create_book(self, title):
        # Implementation here
        pass
```

#### Commit Guidelines

Follow conventional commits format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```bash
git commit -m "feat(epub): Add EPUB generation support

- Implement EpubGenerator class
- Add unit tests for EPUB validation
- Update documentation

Closes #123"
```

### 3. Pre-Push Checklist

Before pushing your branch:

```bash
# Run all quality checks locally
black src/ scripts/ tests/
isort src/ scripts/ tests/
flake8 src/ scripts/ tests/
mypy src/ scripts/
pytest tests/
python scripts/critical_metadata_qa.py

# Check test coverage
pytest --cov=src/kindlemint --cov-report=term-missing

# Run security scan
bandit -r src/ scripts/
```

## PR Guidelines

### Creating a Pull Request

1. **Push your branch**
   ```bash
   git push -u origin feature/KM-123-add-epub-support
   ```

2. **Create PR on GitHub**
   - Use the PR template (automatically loaded)
   - Fill all sections completely
   - Link related issues
   - Add appropriate labels

3. **PR Title Format**
   ```
   feat(scope): Brief description (#issue-number)
   ```
   Examples:
   - `feat(epub): Add EPUB export functionality (#123)`
   - `fix(sudoku): Resolve validation error in puzzle generator (#456)`

### PR Size Guidelines

Keep PRs small and focused:
- **Ideal**: < 400 lines changed
- **Maximum**: 1000 lines changed
- **Files**: < 50 files changed

If larger, consider splitting into multiple PRs.

### Review Process

1. **Automated Checks** (must pass)
   - CI/CD pipeline validation
   - Code quality checks
   - Test coverage (≥80%)
   - Security scanning

2. **AI Reviews** (address feedback)
   - Sentry AI suggestions
   - CodeRabbit analysis
   - DeepSource recommendations

3. **Human Review** (required)
   - Code owner approval
   - Peer review (if applicable)

## Quality Standards

### Code Quality Requirements

| Metric | Requirement | Target |
|--------|------------|--------|
| Test Coverage | ≥80% | 90% |
| Complexity | <10 per function | <7 |
| Duplication | <5% | <3% |
| Security Issues | 0 | 0 |
| Type Coverage | 100% | 100% |

### Testing Requirements

1. **Unit Tests**: Required for all new code
2. **Integration Tests**: Required for new features
3. **Performance Tests**: Required for critical paths
4. **QA Validation**: Must pass all validators

Example test structure:
```python
class TestEpubGenerator:
    def test_create_basic_book(self):
        """Test basic EPUB creation"""
        # Arrange
        generator = EpubGenerator()
        
        # Act
        book = generator.create_book(title="Test")
        
        # Assert
        assert book.is_valid()
        assert book.metadata.title == "Test"
    
    def test_invalid_input_handling(self):
        """Test error handling for invalid inputs"""
        generator = EpubGenerator()
        
        with pytest.raises(ValueError):
            generator.create_book(title="")
```

## CI/CD Pipeline

### Pipeline Stages

1. **Quick Checks** (2-3 min)
   - Branch name validation
   - PR size check
   - Commit message format

2. **Code Quality** (5-7 min)
   - Formatting (black, isort)
   - Linting (flake8, pylint)
   - Type checking (mypy)
   - Security scanning (bandit)

3. **Testing** (10-15 min)
   - Unit tests
   - Integration tests
   - Coverage analysis
   - Business logic validation

4. **AI Reviews** (5-10 min)
   - Sentry AI analysis
   - CodeRabbit review
   - DeepSource scan

5. **Final Validation**
   - Quality gate checks
   - Documentation validation
   - PR status summary

### Handling CI Failures

1. **Check the failing job**
   ```bash
   # View GitHub Actions logs
   gh run view --log-failed
   ```

2. **Fix locally and verify**
   ```bash
   # Run the specific failing check
   pytest tests/unit/test_failing.py -v
   ```

3. **Push fix**
   ```bash
   git add .
   git commit -m "fix: Address CI failure in test_failing"
   git push
   ```

## Emergency Procedures

### Hotfix Process

For critical production issues:

1. **Create hotfix branch from main**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/KM-999-critical-issue
   ```

2. **Implement fix with tests**
   - Minimal changes only
   - Must include regression test

3. **Fast-track review**
   - Skip non-critical checks
   - Requires 1 approval (instead of 2)
   - Deploy immediately after merge

### Reverting Changes

If a merged PR causes issues:

```bash
# Revert via GitHub
gh pr revert <pr-number>

# Or manually
git revert <commit-hash>
git push origin main
```

## Best Practices

### DO's ✅
- Keep PRs small and focused
- Write descriptive commit messages
- Add tests for all new code
- Update documentation
- Respond to reviews promptly
- Use draft PRs for work-in-progress

### DON'Ts ❌
- Don't commit directly to main
- Don't ignore CI failures
- Don't merge without reviews
- Don't skip tests
- Don't include unrelated changes
- Don't commit sensitive data

## Useful Commands

```bash
# Check your PR status
gh pr status

# View PR checks
gh pr checks

# Run CI locally
act -j code-quality

# Check what changed
git diff main...HEAD

# Interactive rebase to clean commits
git rebase -i main

# Update PR after review
git add .
git commit -m "address review feedback"
git push
```

## Getting Help

- **CI Issues**: Check `.github/workflows/` documentation
- **Quality Standards**: See `config/quality-gates.yaml`
- **AI Tools**: Review feedback in PR comments
- **Team Support**: Ask in #dev-help Slack channel

---

Remember: **Quality over speed**. A well-reviewed PR saves time in the long run by preventing bugs and technical debt.