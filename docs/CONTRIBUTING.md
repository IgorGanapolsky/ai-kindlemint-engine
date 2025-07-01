# 🤝 Contributing to AI-KindleMint-Engine

Thank you for your interest in contributing to AI-KindleMint-Engine! This guide will help you get started with our development process.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Getting Help](#getting-help)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:
- Be respectful and constructive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository**
   ```bash
   gh repo fork IgorGanapolsky/ai-kindlemint-engine --clone
   ```

2. **Set up your development environment**
   ```bash
   cd ai-kindlemint-engine
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

## Development Setup

### Required Tools
- Python 3.11 or 3.12
- Git
- GitHub CLI (`gh`) - [Install](https://cli.github.com/)
- Pre-commit - Installed via requirements

### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Add your API keys (if needed for development)
# OPENAI_API_KEY=your_key_here
```

### Verify Setup
```bash
# Run tests to ensure everything works
pytest tests/unit/

# Check code quality tools
black --check src/
flake8 src/
mypy src/
```

## Making Changes

### 1. Create an Issue First
Before making significant changes, create an issue to discuss your proposal:
- Bug reports: Describe the problem and how to reproduce it
- Feature requests: Explain the use case and proposed solution
- Questions: Ask in discussions first

### 2. Create a Feature Branch
```bash
# Sync with upstream
git checkout main
git pull origin main

# Create your branch
git checkout -b feature/your-feature-name
# Or: fix/bug-description
# Or: chore/task-description
```

### 3. Write Code

Follow our coding standards:
- **Style**: Follow PEP 8, enforced by black and flake8
- **Types**: Add type hints for all functions
- **Docs**: Write docstrings for public APIs
- **Tests**: Write tests for all new code

Example:
```python
from typing import List, Optional

def generate_puzzle(
    puzzle_type: str,
    difficulty: int = 5,
    count: int = 1
) -> List[Puzzle]:
    """Generate puzzles of the specified type and difficulty.
    
    Args:
        puzzle_type: Type of puzzle ('sudoku', 'crossword', etc.)
        difficulty: Difficulty level from 1-10
        count: Number of puzzles to generate
        
    Returns:
        List of generated Puzzle objects
        
    Raises:
        ValueError: If puzzle_type is not supported
    """
    # Implementation here
    pass
```

### 4. Write Tests

Tests are required for all new functionality:

```python
# tests/unit/test_puzzle_generator.py
import pytest
from kindlemint.generators import generate_puzzle

class TestPuzzleGenerator:
    def test_generate_single_puzzle(self):
        """Test generating a single puzzle"""
        puzzles = generate_puzzle("sudoku", difficulty=5, count=1)
        assert len(puzzles) == 1
        assert puzzles[0].type == "sudoku"
        
    def test_invalid_puzzle_type(self):
        """Test error handling for invalid types"""
        with pytest.raises(ValueError, match="Unsupported puzzle type"):
            generate_puzzle("invalid_type")
```

### 5. Run Quality Checks

Before committing, run all checks locally:

```bash
# Format code
black src/ scripts/ tests/
isort src/ scripts/ tests/

# Run linters
flake8 src/ scripts/ tests/
mypy src/ scripts/

# Run tests with coverage
pytest tests/ --cov=src/kindlemint --cov-report=term-missing

# Run security scan
bandit -r src/ scripts/

# Run business logic validation
python scripts/critical_metadata_qa.py
```

## Submitting a Pull Request

### 1. Commit Your Changes

Use conventional commit format:
```bash
git add .
git commit -m "feat(puzzles): Add word search generator

- Implement WordSearchGenerator class
- Add difficulty levels 1-10
- Include comprehensive unit tests
- Update documentation

Closes #123"
```

### 2. Push Your Branch
```bash
git push -u origin feature/your-feature-name
```

### 3. Create the PR

```bash
# Using GitHub CLI
gh pr create --title "feat(puzzles): Add word search generator" \
  --body "Description of changes" \
  --assignee @me

# Or create on GitHub web interface
```

### 4. Fill PR Template

Our PR template will be automatically loaded. Please fill all sections:
- ✅ Description of changes
- ✅ Related issues
- ✅ Type of change
- ✅ Testing performed
- ✅ Checklist items

### 5. Address Feedback

Our automated systems will review your PR:
- **CI/CD Pipeline**: Must pass all checks
- **Sentry AI**: Will suggest improvements
- **CodeRabbit**: Will review code quality
- **DeepSource**: Will check for issues

Human reviewers will also provide feedback. Please:
- Respond to all comments
- Make requested changes
- Re-request review when ready

## Code Standards

### Python Style Guide
- Follow PEP 8
- Use black for formatting (120 char line length)
- Use isort for import ordering
- Add type hints for all functions
- Write docstrings for public APIs

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, perf, test, chore

### File Organization
```
src/kindlemint/
├── agents/       # AI agents
├── engines/      # Content generators
├── validators/   # QA validators
├── utils/        # Utility functions
└── orchestrator/ # Orchestration logic

tests/
├── unit/         # Unit tests
├── integration/  # Integration tests
└── performance/  # Performance tests
```

## Testing Guidelines

### Test Coverage Requirements
- Minimum 80% coverage for new code
- 100% coverage for critical business logic
- All edge cases must be tested

### Test Structure
```python
# Arrange
generator = PuzzleGenerator(config)

# Act
result = generator.generate()

# Assert
assert result.is_valid()
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_puzzle_generator.py

# Run with coverage
pytest --cov=src/kindlemint --cov-report=html

# Run with verbose output
pytest -v -s
```

## Getting Help

### Resources
- 📖 [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)
- 🏗️ [Architecture Documentation](docs/ORCHESTRATION_ARCHITECTURE.md)
- 📋 [Project Plan](docs/plan.md)

### Communication
- **Issues**: Use GitHub issues for bugs and features
- **Discussions**: Use GitHub discussions for questions
- **PR Comments**: Ask questions directly in your PR

### Common Issues

**Pre-commit hooks failing:**
```bash
# Run manually to see errors
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

**Import errors:**
```bash
# Ensure package is installed in dev mode
pip install -e .

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

**Test failures:**
```bash
# Run specific failing test with verbose output
pytest path/to/test.py::test_function -vvs
```

## Recognition

Contributors will be:
- Listed in our contributors section
- Mentioned in release notes
- Given credit in commit co-authors

Thank you for contributing to AI-KindleMint-Engine! 🚀