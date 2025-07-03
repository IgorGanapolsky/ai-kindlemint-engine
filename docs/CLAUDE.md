# Claude Code Configuration

## Build Commands
- `npm run build`: Build the project
- `npm run test`: Run the full test suite
- `npm run lint`: Run ESLint and format checks
- `npm run typecheck`: Run TypeScript type checking
- `./claude-flow --help`: Show all available commands

## Sentry AI Integration (NEW!)
- **Automatic PR Review**: `@sentry review` - Triggered automatically on all PRs
- **Test Generation**: `@sentry generate-test` - Auto-generates tests for new code
- **Manual PR Check**: `python scripts/alert_orchestration/sentry_ai_orchestrator.py check --pr <PR_NUMBER>`
- **Monitor All PRs**: `python scripts/alert_orchestration/sentry_ai_orchestrator.py monitor`
- **Test Automation**: `python scripts/test_sentry_ai_automation.py`

## Cursor Bugbot Integration (NEW!)

### Setup Instructions
1. **Enable in Cursor Dashboard** (Required):
   - Go to: https://cursor.com/dashboard?tab=integrations
   - Click "Connect to GitHub" → Authorize → Select this repository
   - Toggle BugBot ON for `IgorGanapolsky/ai-kindlemint-engine`
   - Configure: Disable "Only Run when Mentioned" for automatic reviews

2. **Repository Configuration** (Already Complete):
   - `.cursorignore` - Controls file access (security patterns included)
   - `.github/workflows/cursor-bugbot.yml` - Automated PR triggering
   - `scripts/cursor_bugbot_setup.py` - Validates configuration

### Usage
- **Automatic Review**: Bugbot analyzes every PR automatically (if enabled)
- **Manual Trigger**: Comment `bugbot run` on any PR
- **Verbose Mode**: Comment `bugbot run verbose=true` for detailed analysis
- **Fix Integration**: Click "Fix in Cursor" links to jump to issues in editor

### GitHub Action Automation
```bash
# Manually trigger Bugbot on a specific PR
gh workflow run cursor-bugbot.yml -f pr_number=123
```

### Validate Setup
```bash
# Check if Bugbot is properly configured
python scripts/cursor_bugbot_setup.py
```

### Limitations
- No API access (configuration via dashboard only)
- No webhooks or status badges with real data
- GitHub Enterprise not supported
- May require manual page refresh (known bug)
- Free during Beta for Cursor Pro users ($20/month)

## Claude Cost Tracking & Slack Notifications
- `./claude-flow-costs status`: Show current cost status
- `./claude-flow-costs summary --days 7`: View cost summary
- `./claude-flow-costs-notify setup`: Set up automated Slack notifications
- `./claude-flow-costs-notify daily`: Send daily cost report to Slack
- `./claude-flow-costs-notify weekly`: Send weekly analysis to Slack
- `./claude-flow-costs-notify test`: Test all notification types

## Claude-Flow Complete Command Reference

### Core System Commands
- `./claude-flow start [--ui] [--port 3000] [--host localhost]`: Start orchestration system with optional web UI
- `./claude-flow status`: Show comprehensive system status
- `./claude-flow monitor`: Real-time system monitoring dashboard
- `./claude-flow config <subcommand>`: Configuration management (show, get, set, init, validate)

### Agent Management
- `./claude-flow agent spawn <type> [--name <name>]`: Create AI agents (researcher, coder, analyst, etc.)
- `./claude-flow agent list`: List all active agents
- `./claude-flow spawn <type>`: Quick agent spawning (alias for agent spawn)

### Task Orchestration
- `./claude-flow task create <type> [description]`: Create and manage tasks
- `./claude-flow task list`: View active task queue
- `./claude-flow workflow <file>`: Execute workflow automation files

### Memory Management
- `./claude-flow memory store <key> <data>`: Store persistent data across sessions
- `./claude-flow memory get <key>`: Retrieve stored information
- `./claude-flow memory list`: List all memory keys
- `./claude-flow memory export <file>`: Export memory to file
- `./claude-flow memory import <file>`: Import memory from file
- `./claude-flow memory stats`: Memory usage statistics
- `./claude-flow memory cleanup`: Clean unused memory entries

### SPARC Development Modes
- `./claude-flow sparc "<task>"`: Run orchestrator mode (default)
- `./claude-flow sparc run <mode> "<task>"`: Run specific SPARC mode
- `./claude-flow sparc tdd "<feature>"`: Test-driven development mode
- `./claude-flow sparc modes`: List all 17 available SPARC modes

Available SPARC modes: orchestrator, coder, researcher, tdd, architect, reviewer, debugger, tester, analyzer, optimizer, documenter, designer, innovator, swarm-coordinator, memory-manager, batch-executor, workflow-manager

### Swarm Coordination
- `./claude-flow swarm "<objective>" [options]`: Multi-agent swarm coordination
- `--strategy`: research, development, analysis, testing, optimization, maintenance
- `--mode`: centralized, distributed, hierarchical, mesh, hybrid
- `--max-agents <n>`: Maximum number of agents (default: 5)
- `--parallel`: Enable parallel execution
- `--monitor`: Real-time monitoring
- `--output <format>`: json, sqlite, csv, html

### MCP Server Integration
- `./claude-flow mcp start [--port 3000] [--host localhost]`: Start MCP server
- `./claude-flow mcp status`: Show MCP server status
- `./claude-flow mcp tools`: List available MCP tools

### Claude Integration
- `./claude-flow claude auth`: Authenticate with Claude API
- `./claude-flow claude models`: List available Claude models
- `./claude-flow claude chat`: Interactive chat mode

### Session Management
- `./claude-flow session`: Manage terminal sessions
- `./claude-flow repl`: Start interactive REPL mode

### Enterprise Features
- `./claude-flow project <subcommand>`: Project management (Enterprise)
- `./claude-flow deploy <subcommand>`: Deployment operations (Enterprise)
- `./claude-flow cloud <subcommand>`: Cloud infrastructure management (Enterprise)
- `./claude-flow security <subcommand>`: Security and compliance tools (Enterprise)
- `./claude-flow analytics <subcommand>`: Analytics and insights (Enterprise)

### Project Initialization
- `./claude-flow init`: Initialize Claude-Flow project
- `./claude-flow init --sparc`: Initialize with full SPARC development environment

## Quick Start Workflows

### Research Workflow
```bash
# Start a research swarm with distributed coordination
./claude-flow swarm "Research modern web frameworks" --strategy research --mode distributed --parallel --monitor

# Or use SPARC researcher mode for focused research
./claude-flow sparc run researcher "Analyze React vs Vue vs Angular performance characteristics"

# Store findings in memory for later use
./claude-flow memory store "research_findings" "Key insights from framework analysis"
```

### Development Workflow
```bash
# Start orchestration system with web UI
./claude-flow start --ui --port 3000

# Run TDD workflow for new feature
./claude-flow sparc tdd "User authentication system with JWT tokens"

# Development swarm for complex projects
./claude-flow swarm "Build e-commerce API with payment integration" --strategy development --mode hierarchical --max-agents 8 --monitor

# Check system status
./claude-flow status
```

### Analysis Workflow
```bash
# Analyze codebase performance
./claude-flow sparc run analyzer "Identify performance bottlenecks in current codebase"

# Data analysis swarm
./claude-flow swarm "Analyze user behavior patterns from logs" --strategy analysis --mode mesh --parallel --output sqlite

# Store analysis results
./claude-flow memory store "performance_analysis" "Bottlenecks identified in database queries"
```

### Maintenance Workflow
```bash
# System maintenance with safety controls
./claude-flow swarm "Update dependencies and security patches" --strategy maintenance --mode centralized --monitor

# Security review
./claude-flow sparc run reviewer "Security audit of authentication system"

# Export maintenance logs
./claude-flow memory export maintenance_log.json
```

## Integration Patterns

### Memory-Driven Coordination
Use Memory to coordinate information across multiple SPARC modes and swarm operations:

```bash
# Store architecture decisions
./claude-flow memory store "system_architecture" "Microservices with API Gateway pattern"

# All subsequent operations can reference this decision
./claude-flow sparc run coder "Implement user service based on system_architecture in memory"
./claude-flow sparc run tester "Create integration tests for microservices architecture"
```

### Multi-Stage Development
Coordinate complex development through staged execution:

```bash
# Stage 1: Research and planning
./claude-flow sparc run researcher "Research authentication best practices"
./claude-flow sparc run architect "Design authentication system architecture"

# Stage 2: Implementation
./claude-flow sparc tdd "User registration and login functionality"
./claude-flow sparc run coder "Implement JWT token management"

# Stage 3: Testing and deployment
./claude-flow sparc run tester "Comprehensive security testing"
./claude-flow swarm "Deploy authentication system" --strategy maintenance --mode centralized
```

### Enterprise Integration
For enterprise environments with additional tooling:

```bash
# Project management integration
./claude-flow project create "authentication-system"
./claude-flow project switch "authentication-system"

# Security compliance
./claude-flow security scan
./claude-flow security audit

# Analytics and monitoring
./claude-flow analytics dashboard
./claude-flow deploy production --monitor
```

## Advanced Batch Tool Patterns

### TodoWrite Coordination
Always use TodoWrite for complex task coordination:

```javascript
TodoWrite([
  {
    id: "architecture_design",
    content: "Design system architecture and component interfaces",
    status: "pending",
    priority: "high",
    dependencies: [],
    estimatedTime: "60min",
    assignedAgent: "architect"
  },
  {
    id: "frontend_development",
    content: "Develop React components and user interface",
    status: "pending",
    priority: "medium",
    dependencies: ["architecture_design"],
    estimatedTime: "120min",
    assignedAgent: "frontend_team"
  }
]);
```

### Task and Memory Integration
Launch coordinated agents with shared memory:

```javascript
// Store architecture in memory
Task("System Architect", "Design architecture and store specs in Memory");

// Other agents use memory for coordination
Task("Frontend Team", "Develop UI using Memory architecture specs");
Task("Backend Team", "Implement APIs according to Memory specifications");
```

## Code Style Preferences
- Use ES modules (import/export) syntax
- Destructure imports when possible
- Use TypeScript for all new code
- Follow existing naming conventions
- Add JSDoc comments for public APIs
- Use async/await instead of Promise chains
- Prefer const/let over var

## Workflow Guidelines
- Always run typecheck after making code changes
- Run tests before committing changes
- Use meaningful commit messages
- Create feature branches for new functionality
- Ensure all tests pass before merging



## WORKTREE ORCHESTRATION (ACTIVE)
**CRITICAL**: All commits MUST use worktree orchestration for token cost optimization.
**CRITICAL**: Badge validation is MANDATORY - never remove project visibility badges!

### Automatic Worktree Usage:
1. For features: Use appropriate worktree based on task type
2. For fixes: Use ci-fixes worktree for CI-related issues
3. For docs: Can use main branch (low token usage)

### Before ANY commit:
```bash
# Check which worktree to use
python scripts/orchestration/check_worktree_assignment.py "commit message"

# Or use automatic orchestration
python scripts/orchestration/worktree_orchestrator.py --auto
```

### Token Cost Tracking:
- Every commit tracks token usage automatically
- Cost reports generated in reports/orchestration/
- Slack notifications for high-cost operations

## Important Notes
- **Use TodoWrite extensively** for all complex task coordination
- **Leverage Task tool** for parallel agent execution on independent work
- **Store all important information in Memory** for cross-agent coordination
- **Use batch file operations** whenever reading/writing multiple files
- **Check .claude/commands/** for detailed command documentation
- **All swarm operations include automatic batch tool coordination**
- **Monitor progress** with TodoRead during long-running operations
- **Enable parallel execution** with --parallel flags for maximum efficiency

## CRITICAL FILE MANAGEMENT RULE
- **ALWAYS DELETE OUTDATED FILES** before commit and push
- **Never keep obsolete versions** that could cause confusion
- **Replace outdated reports/files** with current versions
- **Clean up deprecated content** to maintain repository hygiene
- **This is MANDATORY** for all file operations and QA processes

This configuration ensures optimal use of Claude Code's batch tools for swarm orchestration and parallel task execution with full Claude-Flow capabilities.

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
**ALWAYS commit and push your changes** - After making any code changes, you MUST commit them with a descriptive message and push to the repository
**CRITICAL: ALWAYS DELETE OUTDATED FILES before commit and push - Never keep obsolete versions that could cause confusion**
**CRITICAL: KDP CATEGORIES - Never hallucinate categories! Always use ACTUAL KDP categories with FULL PATHS including subcategories (e.g., "Crafts, Hobbies & Home > Games & Activities"). KDP allows THREE categories, always provide exactly 3 complete category paths. Verify against actual KDP dropdown menus.**
**CRITICAL: KDP BOOK TYPE CLASSIFICATIONS - Always specify for every book metadata:**
- Low-content book: true (for puzzle books, journals, notebooks, planners)
- Large-print book: true (for books with 16-point font or greater, especially "Large Print" series)
**CRITICAL: BOOK TRIM SIZES - Never use wrong sizes for puzzle books:**
- Paperback puzzle books: ALWAYS 8.5x11 inches (enough space for large print puzzles)
- Hardcover puzzle books: 6x9 inches is acceptable
- NEVER use 6x9 for paperback puzzle books - too cramped for puzzle solving
**CRITICAL: COVER DESIGN PROMPTS - Every book MUST have DALL-E cover prompts:**
- Add cover_design.dalle_prompt field to all metadata files
- Include detailed, professional prompts for book cover generation
- Specify style, colors, typography, and puzzle theme elements
