# Sentry Agent Monitoring Integration Guide

## Overview

This guide explains how to use Sentry's new Agent Monitoring feature to debug AI workflows in the KindleMint Engine. Agent Monitoring provides visibility into:

- **Prompt/Response Tracking**: See exactly what prompts were sent and responses received
- **Tool Usage**: Monitor when AI agents use tools and what happens
- **Error Context**: Debug failures with full AI workflow context
- **Performance Metrics**: Track token usage, latency, and costs

## Setup

### 1. Environment Configuration

Set up your environment variables:

```bash
# Required
export SENTRY_DSN="your-sentry-dsn-here"
export OPENAI_API_KEY="your-openai-key"

# Optional
export ENVIRONMENT="production"  # or "development"
export SENTRY_TRACES_SAMPLE_RATE="1.0"  # 100% sampling for debugging
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

The key dependency is `sentry-sdk[openai]>=2.0.0` which includes the OpenAI integration.

## Usage

### Basic Integration

Use the `EnhancedAPIManager` instead of the regular `APIManager`:

```python
from scripts.api_manager_enhanced import EnhancedAPIManager

# Initialize with automatic monitoring
api_manager = EnhancedAPIManager()

# All API calls are now monitored
result = api_manager.generate_text(
    prompt="Generate crossword clues for CAT",
    task_name="clue_generation",  # Descriptive name for Sentry
    temperature=0.7
)
```

### Monitoring Custom Workflows

For complex workflows, use the `SentryAgentMonitor`:

```python
from scripts.sentry_agent_monitoring import get_agent_monitor, AgentContext

monitor = get_agent_monitor()

# Create context for your workflow
context = AgentContext(
    agent_id="workflow_001",
    agent_type="openai",
    task_name="crossword_generation",
    model="gpt-4",
    metadata={"puzzle_size": "15x15"}
)

# Start monitoring
with monitor.start_agent(context) as transaction:
    # Your AI workflow here
    
    # Track prompts
    transaction.track_prompt(
        prompt="Generate clues...",
        response="1. Feline pet (CAT)",
        tokens=150,
        latency_ms=523.4
    )
    
    # Track tool usage
    monitor.track_tool_call(
        agent_id=context.agent_id,
        tool_name="validate_clues",
        tool_input={"clues": ["Feline pet"]},
        tool_output={"valid": True}
    )
```

### Using Decorators

For simple functions, use the monitoring decorator:

```python
from scripts.api_manager_enhanced import with_ai_monitoring

@with_ai_monitoring(task_name="generate_puzzle", provider=APIProvider.OPENAI)
def generate_crossword_puzzle(words, **kwargs):
    # kwargs will include an EnhancedAPIManager instance
    api_manager = kwargs['api_manager']
    
    # Your puzzle generation logic
    return puzzle
```

### Error Handling

Errors are automatically captured with AI-specific context:

```python
try:
    result = api_manager.generate_text(prompt=very_long_prompt)
except Exception as e:
    # Error is automatically sent to Sentry with:
    # - Full prompt/response history
    # - Token usage up to failure
    # - Error categorization (rate limit, token limit, etc.)
    pass
```

## Viewing in Sentry

### 1. Navigate to Agent Monitoring

In your Sentry dashboard:
- Go to **Insights → Agents**
- Or use the direct link from the email

### 2. Understanding the Views

**Agent List View**:
- See all AI agents and their performance
- Filter by agent type (openai, dalle, gemini)
- Sort by error rate, latency, or token usage

**Agent Detail View**:
- Complete prompt/response traces
- Tool call timeline
- Error patterns and debugging info

**Transaction View**:
- Step-by-step execution flow
- Performance breakdowns
- Token usage per step

### 3. Debugging Common Issues

**Token Limit Errors**:
- View the exact prompt that exceeded limits
- See token count at failure point
- Review prompt optimization suggestions

**Rate Limit Errors**:
- Identify patterns in request frequency
- See which operations trigger limits
- Plan request batching strategies

**JSON Parsing Errors**:
- View the raw AI response
- See where parsing failed
- Implement better error handling

**Tool Failures**:
- Track which tools fail most often
- See input/output patterns
- Identify integration issues

## Best Practices

### 1. Use Descriptive Task Names

```python
# Good
task_name="generate_crossword_clues_15x15"
task_name="validate_puzzle_difficulty_hard"

# Less helpful
task_name="task1"
task_name="generate"
```

### 2. Add Relevant Metadata

```python
context = AgentContext(
    agent_id="puzzle_gen_001",
    agent_type="openai",
    task_name="generate_puzzle",
    model="gpt-4",
    metadata={
        "puzzle_type": "crossword",
        "size": "15x15",
        "difficulty": "medium",
        "theme": "animals"
    }
)
```

### 3. Track Tool Usage

Always track when AI uses tools:

```python
monitor.track_tool_call(
    agent_id=context.agent_id,
    tool_name="dictionary_lookup",
    tool_input={"word": "CAT"},
    tool_output={"definition": "A small domesticated carnivore"}
)
```

### 4. Batch Related Operations

Group related AI calls:

```python
# Use batch generation for multiple similar prompts
results = api_manager.batch_generate(
    prompts=["Clue for CAT", "Clue for DOG", "Clue for BIRD"],
    task_name="batch_clue_generation"
)
```

## Example Workflow

Here's a complete example of monitoring a crossword generation workflow:

```python
#!/usr/bin/env python3
from scripts.api_manager_enhanced import EnhancedAPIManager
from scripts.sentry_agent_monitoring import get_agent_monitor, AgentContext

def generate_crossword_with_monitoring():
    api_manager = EnhancedAPIManager()
    monitor = get_agent_monitor()
    
    # Define workflow context
    context = AgentContext(
        agent_id=f"crossword_{int(time.time())}",
        agent_type="workflow",
        task_name="full_crossword_generation",
        model="gpt-4",
        metadata={
            "puzzle_size": "15x15",
            "word_count": 50
        }
    )
    
    with monitor.start_agent(context) as transaction:
        # Step 1: Generate word list
        words_result = api_manager.generate_text(
            prompt="Generate 50 common crossword words",
            task_name="word_generation"
        )
        
        # Step 2: Generate clues for each word
        clues = []
        for word in words_result['text'].split('\n'):
            clue_result = api_manager.generate_text(
                prompt=f"Generate a crossword clue for: {word}",
                task_name=f"clue_gen_{word}"
            )
            clues.append({
                "word": word,
                "clue": clue_result['text']
            })
        
        # Step 3: Validate puzzle
        monitor.track_tool_call(
            agent_id=context.agent_id,
            tool_name="puzzle_validator",
            tool_input={"clues": clues},
            tool_output={"valid": True, "score": 0.95}
        )
        
        return {"words": words, "clues": clues}
```

## Troubleshooting

### No Data in Sentry

1. Verify `SENTRY_DSN` is set correctly
2. Check network connectivity
3. Ensure `sentry-sdk[openai]>=2.0.0` is installed
4. Look for initialization messages in logs

### Missing Prompts/Responses

1. Check `include_prompts=True` in OpenAI integration
2. Verify you're using `EnhancedAPIManager`
3. Ensure `send_default_pii=False` if needed

### Performance Impact

- Adjust `traces_sample_rate` for production (e.g., 0.1 for 10%)
- Use `profiles_sample_rate=0` if not needed
- Batch operations when possible

## Additional Resources

- [Sentry Agent Monitoring Docs](https://docs.sentry.io/product/insights/agents/)
- [OpenAI Integration Guide](https://docs.sentry.io/platforms/python/integrations/openai/)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)

## Support

For issues specific to this integration:
1. Check the error logs with full stack traces
2. Review the Sentry dashboard for error patterns
3. Use the Discord channel mentioned in the Sentry email
4. File issues in the KindleMint Engine repository