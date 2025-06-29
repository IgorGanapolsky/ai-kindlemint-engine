# Alert Orchestration System

## Overview

The Alert Orchestration System is an autonomous monitoring and resolution platform that integrates Sentry error tracking with Slack notifications and automated resolution capabilities. It provides intelligent error analysis, pattern recognition, and automated fixes for common issues while maintaining comprehensive escalation procedures for critical problems.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Sentry API    │    │    Slack API    │    │   GitHub API    │
│   Monitoring    │    │  Notifications  │    │   Integration   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Alert Orchestrator                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Sentry    │ │    Error    │ │    Auto     │ │    Slack    ││
│  │  Monitor    │ │  Analyzer   │ │  Resolver   │ │   Handler   ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Resolution    │    │   Escalation    │    │   Monitoring    │
│   Strategies    │    │     Rules       │    │   Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Features

### 🔍 **Intelligent Error Monitoring**
- Real-time Sentry error fetching and analysis
- Pattern recognition and error categorization
- Frequency analysis and trend detection
- Business impact assessment

### 🤖 **Automated Resolution**
- Safe automated fixes for common issues
- Multi-strategy resolution approaches
- Rollback capabilities for failed attempts
- Comprehensive validation and testing

### 📢 **Smart Notifications**
- Rich Slack notifications with interactive components
- Escalation management with configurable rules
- Context-aware alert prioritization
- Thread-based conversation management

### 📊 **Analytics and Reporting**
- Resolution success metrics
- Error pattern analysis
- Performance tracking
- Customizable dashboards

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/igorganapolsky/ai-kindlemint-engine.git
cd ai-kindlemint-engine/scripts/alert_orchestration

# Install dependencies
pip install -r ../../requirements.txt

# Install additional dependencies
pip install fastapi uvicorn pyyaml
```

### 2. Configuration

Create a `.env` file with your credentials:

```bash
# Sentry Configuration
SENTRY_AUTH_TOKEN=your_sentry_auth_token
SENTRY_ORGANIZATION=your_organization_name

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Optional: Additional integrations
GITHUB_TOKEN=your_github_token
PAGERDUTY_API_KEY=your_pagerduty_key
```

### 3. Basic Configuration

Edit `config.yaml` to match your environment:

```yaml
# Basic settings
system:
  environment: "production"  # or "staging", "development"

# Component enablement
components:
  sentry_enabled: true
  slack_enabled: true
  auto_resolution_enabled: true

# Operational settings
operation:
  dry_run: false  # Set to true for testing
  monitoring_interval: 300  # seconds
  max_concurrent_resolutions: 3
```

### 4. Start the Orchestrator

```bash
# Start in normal mode
python alert_orchestrator.py --config config.yaml

# Start in dry-run mode for testing
python alert_orchestrator.py --config config.yaml --dry-run
```

## Configuration Guide

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SENTRY_AUTH_TOKEN` | Yes | Sentry API authentication token |
| `SENTRY_ORGANIZATION` | Yes | Sentry organization slug |
| `SLACK_WEBHOOK_URL` | Recommended | Slack webhook for notifications |
| `SLACK_BOT_TOKEN` | Optional | Slack bot token for interactive features |
| `GITHUB_TOKEN` | Optional | GitHub token for issue creation |
| `PAGERDUTY_API_KEY` | Optional | PagerDuty integration |

### Configuration Files

#### `config.yaml`
Main configuration file controlling all system behavior:
- System settings and component enablement
- Operational parameters and safety limits
- Integration configurations
- Notification channels and templates

#### `error_patterns.json`
Database of known error patterns for recognition:
- Regular expression patterns for error matching
- Confidence scores and resolution strategies
- Categorization and business impact data

#### `escalation_rules.yaml`
Escalation logic and thresholds:
- Multi-level escalation definitions
- Trigger conditions and time-based rules
- Notification targets and actions

## Usage Examples

### Manual Error Analysis

```python
from error_analyzer import ErrorAnalyzer

analyzer = ErrorAnalyzer()

# Analyze a specific error
error_data = {
    'id': 'error_123',
    'message': 'Database connection timeout after 30 seconds',
    'level': 'error',
    'environment': 'production'
}

classification = analyzer.analyze_error(error_data)
print(f"Category: {classification.primary_category}")
print(f"Confidence: {classification.confidence_score}")
print(f"Suggested actions: {classification.suggested_actions}")
```

### Custom Resolution Strategy

```python
from resolution_strategies import ResolutionStrategy, register_custom_strategy

class CustomDatabaseStrategy(ResolutionStrategy):
    def __init__(self):
        super().__init__(
            name="Custom Database Fix",
            description="Custom strategy for database issues",
            confidence=0.8,
            safety_level="safe"
        )

    async def execute(self, error_context):
        # Custom resolution logic
        return StrategyResult(success=True, message="Fixed!")

    async def validate(self, error_context):
        return "database" in error_context.get("message", "").lower()

# Register the custom strategy
register_custom_strategy(CustomDatabaseStrategy())
```

### Custom Notification Template

```python
from notification_templates import SlackBlockTemplate, register_custom_template

def custom_alert_blocks(data):
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔥 Custom Alert: {data.get('title')}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Details:* {data.get('description')}"
            }
        }
    ]

# Register the custom template
template = SlackBlockTemplate("custom_alert", custom_alert_blocks)
register_custom_template(template)
```

## Component Documentation

### SentryMonitor
Handles Sentry API integration and error fetching.

**Key Methods:**
- `fetch_errors()` - Retrieve errors from Sentry
- `analyze_error_patterns()` - Analyze error trends
- `get_projects()` - List available projects

### ErrorAnalyzer
Provides intelligent error classification and analysis.

**Key Methods:**
- `analyze_error()` - Classify and analyze errors
- `analyze_trends()` - Trend analysis over time
- `get_error_suggestions()` - Resolution suggestions

### AutoResolver
Executes automated resolution strategies safely.

**Key Methods:**
- `resolve_error()` - Attempt automated resolution
- `rollback_resolution()` - Rollback failed attempts
- `get_resolution_history()` - Track resolution attempts

### SlackHandler
Manages Slack notifications and interactions.

**Key Methods:**
- `send_alert()` - Send formatted alerts
- `handle_interaction()` - Process button clicks
- `send_escalation()` - Escalate critical issues

## Safety and Security

### Safety Mechanisms
- **Dry Run Mode**: Test without making changes
- **Rate Limiting**: Prevent excessive actions
- **Rollback Support**: Undo failed resolutions
- **Validation Checks**: Verify actions before execution

### Security Features
- **Environment Separation**: Different configs per environment
- **Credential Management**: Secure credential handling
- **Audit Logging**: Complete action history
- **Access Control**: Role-based permissions

### Production Safety
- **Gradual Rollout**: Deploy changes incrementally
- **Monitoring**: Comprehensive system monitoring
- **Alerting**: Immediate notification of issues
- **Circuit Breakers**: Automatic failure prevention

## Monitoring and Metrics

### Key Metrics
- **Error Processing Rate**: Errors handled per hour
- **Resolution Success Rate**: Percentage of successful auto-fixes
- **Alert Response Time**: Time from error to notification
- **Escalation Frequency**: How often issues escalate

### Health Monitoring
```bash
# Check system status
./scripts/alert_orchestration/health_check.py

# View metrics
curl http://localhost:8000/metrics

# Check component health
python -c "from alert_orchestrator import AlertOrchestrator; print('System healthy')"
```

### Dashboards
The system provides built-in monitoring dashboards:
- **Error Analysis Dashboard**: Error patterns and trends
- **Resolution Performance**: Success rates and timing
- **System Health**: Component status and metrics
- **Business Impact**: Cost and user impact tracking

## Troubleshooting

### Common Issues

#### Sentry Connection Issues
```bash
# Test Sentry connectivity
python -c "
from sentry_monitor import SentryMonitor
monitor = SentryMonitor()
projects = monitor.get_projects()
print(f'Connected! Found {len(projects)} projects')
"
```

#### Slack Integration Issues
```bash
# Test Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  $SLACK_WEBHOOK_URL
```

#### Permission Issues
```bash
# Check file permissions
ls -la scripts/alert_orchestration/
chmod +x scripts/alert_orchestration/*.py
```

### Debug Mode
Enable debug logging for troubleshooting:

```yaml
# In config.yaml
system:
  log_level: "DEBUG"

development:
  debug_mode: true
  verbose_logging: true
```

### Log Analysis
```bash
# View orchestrator logs
tail -f /var/log/alert-orchestrator/orchestrator.log

# Check error patterns
grep "ERROR" /var/log/alert-orchestrator/orchestrator.log

# Monitor resolution attempts
grep "resolution" /var/log/alert-orchestrator/orchestrator.log
```

## API Reference

### REST API Endpoints
The orchestrator exposes REST endpoints for integration:

```bash
# Get system status
GET /api/v1/status

# Get active alerts
GET /api/v1/alerts

# Get resolution history
GET /api/v1/resolutions

# Trigger manual resolution
POST /api/v1/resolve
Content-Type: application/json
{
  "error_id": "error_123",
  "strategy": "restart_service"
}
```

### Webhook Integration
Process external webhooks:

```bash
# Sentry webhook
POST /webhooks/sentry
Content-Type: application/json

# Custom alert webhook
POST /webhooks/alert
Content-Type: application/json
{
  "title": "Custom Alert",
  "severity": "high",
  "source": "external_system"
}
```

## Advanced Configuration

### Custom Error Patterns
Add new error patterns to `error_patterns.json`:

```json
{
  "id": "custom_error_pattern",
  "name": "Custom Application Error",
  "pattern": "(?:custom|app).{0,50}(?:error|failure)",
  "category": "application",
  "severity": "medium",
  "confidence": 0.85,
  "resolution_strategy": "restart_application"
}
```

### Escalation Rules
Customize escalation in `escalation_rules.yaml`:

```yaml
category_rules:
  custom_category:
    priority: "high"
    escalation_speed: "fast"
    rules:
      - condition: "error.environment == 'production'"
        immediate_level: 2
        reason: "Production custom errors require immediate attention"
```

### Integration Plugins
Extend functionality with custom plugins:

```python
# Create custom integration
class CustomIntegration:
    def __init__(self, config):
        self.config = config

    async def send_notification(self, alert_data):
        # Custom notification logic
        pass

    async def handle_escalation(self, escalation_data):
        # Custom escalation logic
        pass

# Register integration
from alert_orchestrator import AlertOrchestrator
orchestrator = AlertOrchestrator()
orchestrator.register_integration("custom", CustomIntegration(config))
```

## Performance Tuning

### Optimization Settings
```yaml
# High-performance configuration
operation:
  monitoring_interval: 60  # More frequent monitoring
  max_concurrent_resolutions: 10  # Higher concurrency

# Database optimization
database:
  connection_pool_size: 20
  query_timeout: 30

# Cache configuration
cache:
  enabled: true
  ttl: 300
  max_size: 1000
```

### Scaling Considerations
- **Horizontal Scaling**: Run multiple orchestrator instances
- **Load Balancing**: Distribute error processing
- **Database Optimization**: Tune query performance
- **Cache Strategy**: Implement intelligent caching

## Contributing

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/igorganapolsky/ai-kindlemint-engine.git
cd ai-kindlemint-engine
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Run tests
python -m pytest scripts/alert_orchestration/tests/

# Run linting
flake8 scripts/alert_orchestration/
black scripts/alert_orchestration/
```

### Adding New Features
1. **Error Patterns**: Add to `error_patterns.json`
2. **Resolution Strategies**: Extend `resolution_strategies.py`
3. **Notification Templates**: Add to `notification_templates.py`
4. **Integrations**: Create new integration modules

### Testing
```bash
# Run unit tests
pytest scripts/alert_orchestration/tests/test_*.py

# Run integration tests
pytest scripts/alert_orchestration/tests/integration/

# Test configuration validation
python scripts/alert_orchestration/validate_config.py
```

## Support and Documentation

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Complete API and configuration reference
- **Slack Channel**: #alert-orchestration for real-time support
- **Wiki**: Detailed guides and best practices

### Resources
- [Sentry API Documentation](https://docs.sentry.io/api/)
- [Slack API Documentation](https://api.slack.com/)
- [System Architecture Guide](./docs/architecture.md)
- [Best Practices Guide](./docs/best-practices.md)

## License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.

---

**Built with ❤️ for autonomous infrastructure management**
