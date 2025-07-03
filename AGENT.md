# Agent Configuration for AI-KindleMint-Engine

## Build/Test/Lint Commands
```bash
# Test commands
pytest                              # Run all tests
pytest tests/unit/test_file.py::test_function -vvs  # Run single test with verbose output
pytest --cov=src/kindlemint --cov-report=html       # Run with coverage

# Code quality (install: pip install -e ".[dev]")
black src/ scripts/                 # Format code (line length 88)
isort --profile black src/ scripts/ # Sort imports
flake8 src/ scripts/ --max-line-length=88 --extend-ignore=E203,W503  # Lint
mypy src/                          # Type checking
pre-commit run --all-files         # Run all pre-commit hooks
```

## Architecture & Codebase Structure
**AI-Powered Book Publishing Platform:**
- `kindlemint/` - Core AI-powered book publishing platform with agents, generators, validators
- `agents/` - Specialized AI agents (content, cover design, market research, automation)
- `src/kindlemint/orchestrator/` - Unified orchestrator coordinating Claude Code development system
- Key APIs: `APIManager` (multi-provider AI), `BaseAgent` (agent framework), validators (14-point QA)
- Databases: None (stateless design), uses external APIs (OpenAI, Gemini, KDP)
- Entry points: `./claude-code` CLI, `kindlemint.cli:cli` console script

## Code Style & Conventions
- **Python 3.11+**, Black formatting (88 char), isort with `--profile black`
- **Imports:** Absolute imports preferred, `from kindlemint.module import Class`
- **Classes:** Agent classes end with "Agent" suffix, inherit from `BaseAgent`
- **Async:** Use `async def` for I/O operations, `@property` for computed attributes
- **Types:** Type hints required, use `Optional[Type]` and `List[Type]`
- **Errors:** Custom exceptions, structured logging, comprehensive error handling
- **Naming:** snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
