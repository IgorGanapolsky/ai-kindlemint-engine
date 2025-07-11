# AI-KindleMint-Engine Agent Guide

## Build/Lint/Test Commands
- **Test**: `python -m pytest tests/ -v --cov=src/kindlemint --cov-report=term-missing`
- **Test single file**: `python -m pytest tests/test_specific.py -v`
- **Lint**: `black src/ scripts/ tests/ && flake8 src/ scripts/ tests/ && isort src/ scripts/ tests/`
- **Type check**: `mypy src/ scripts/`
- **Install**: `pip install -e .` (dev: `pip install -e .[dev]`)

## Architecture Overview
- **Core**: `src/kindlemint/` - Main publishing platform (generators, agents, orchestrator, validators)
- **API**: `api/` - Webhook handlers, subscription management, landing pages
- **Scripts**: `scripts/` - 200+ automation scripts for book generation, CI/CD, market research
- **Tests**: `tests/` - Unit tests in `unit/`, integration tests in `integration/`
- **MCP Server**: Orchestrates GitHub workflows via EC2 deployment at `44.201.249.255:8080`

## Key Technologies
- **AI APIs**: OpenAI (GPT-4, DALL-E), Claude (Anthropic), configurable API manager
- **Business**: Stripe payments, SendGrid email, Botpress chatbots
- **Data**: SQLite (context, audit logs), JSON config, file-based puzzle cache
- **Publishing**: Amazon KDP integration, social media APIs (LinkedIn, Twitter, Instagram)

## Code Style
- **Formatting**: Black with 88-char line length, isort for imports
- **Linting**: Flake8 with standard rules
- **Types**: MyPy for type checking, use type hints
- **Testing**: pytest with coverage reporting, async tests supported
- **Structure**: Package-based organization, CLI entry point via `kindlemint.cli:cli`
