# 🎯 Unified Orchestration System Guide

> **Complete integration of Claude Code and A2A orchestration for AI-powered book publishing**

## 🚀 Overview

The AI-KindleMint-Engine now features a **unified orchestration system** that seamlessly integrates:

1. **Claude Code Orchestrator** - AI-accelerated development and high-level tasks
2. **A2A (Agent-to-Agent) Protocol** - Specialized, decoupled task execution
3. **Unified Interface** - Single point of control for both systems
4. **Monitoring & Health Checks** - Real-time system monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Orchestrator                    │
│                  (Master Coordinator)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌──────────────────┐         ┌──────────────────┐
│ Claude Code      │         │ A2A Protocol     │
│ Orchestrator     │         │ System           │
│                  │         │                  │
│ • Development    │         │ • Puzzle Gen     │
│ • Features       │         │ • PDF Layout     │
│ • Optimization   │         │ • Validation     │
│ • Testing        │         │ • Specialized    │
└──────────────────┘         └──────────────────┘
```

## 🎯 Execution Modes

### 1. **Claude Code Only**
- High-level development tasks
- Feature creation and optimization
- Code generation and testing

### 2. **A2A Only**
- Puzzle generation
- PDF creation
- Validation tasks
- Specialized operations

### 3. **Hybrid Mode**
- Complete book production workflows
- Multi-step processes
- Quality assurance pipelines

### 4. **Auto Mode** (Default)
- Intelligent routing based on task type
- Optimal system selection

## 🚀 Quick Start

### Option 1: Command Line Interface

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Create a complete puzzle book
python unified_orchestrator_cli.py create-book \
  --title "My Puzzle Book" \
  --count 50 \
  --difficulty medium \
  --format paperback

# Generate puzzles only
python unified_orchestrator_cli.py generate-puzzles \
  --count 10 \
  --difficulty hard \
  --output my_puzzles.json

# Create PDF from existing puzzles
python unified_orchestrator_cli.py create-pdf \
  --title "Custom Book" \
  --puzzles my_puzzles.json

# Check system status
python unified_orchestrator_cli.py status

# Run quality checks
python unified_orchestrator_cli.py quality-check --target all
```

### Option 2: Python API

```python
import asyncio
from src.kindlemint.orchestrator.unified_orchestrator import (
    create_unified_orchestrator, UnifiedTask, OrchestrationMode
)

async def create_book():
    # Initialize orchestrator
    orchestrator = create_unified_orchestrator()
    
    # Create task
    task = UnifiedTask(
        id="my_book",
        type="book_production",
        description="Create puzzle book",
        parameters={
            "book_title": "AI Puzzle Collection",
            "puzzle_count": 25,
            "difficulty": "medium",
            "book_format": "paperback"
        },
        mode=OrchestrationMode.HYBRID
    )
    
    # Execute
    result = await orchestrator.execute_task(task)
    print(f"Success: {result['success']}")

# Run
asyncio.run(create_book())
```

### Option 3: Interactive Demo

```bash
# Run the complete demonstration
python orchestration_demo.py
```

## 🤖 A2A Agents

### Puzzle Generator Agent
**Capabilities:**
- `generate_single_puzzle` - Create one puzzle
- `generate_puzzle_batch` - Create multiple puzzles
- `regenerate_failed_puzzle` - Retry failed generations
- `validate_puzzle_request` - Validate parameters

**Example Usage:**
```python
# Single puzzle
request = {
    "difficulty": "medium",
    "format": "json",
    "large_print": True
}

# Batch puzzles
request = {
    "count": 20,
    "difficulty": "hard",
    "format": "both"  # JSON + PNG
}
```

### PDF Layout Agent
**Capabilities:**
- `create_puzzle_book` - Complete book with cover
- `create_puzzle_pages` - Puzzles only
- `create_solution_pages` - Solutions only
- `validate_pdf_layout` - Validate parameters
- `optimize_pdf_size` - Reduce file size

**Example Usage:**
```python
request = {
    "puzzles": puzzle_list,
    "book_title": "My Book",
    "book_format": "paperback",
    "trim_size": "8.5x11",
    "include_solutions": True,
    "font_size": 16
}
```

## 🔧 System Configuration

### Routing Configuration
Tasks are automatically routed based on type:

```python
task_routing = {
    "puzzle_generation": OrchestrationMode.A2A_ONLY,
    "pdf_creation": OrchestrationMode.A2A_ONLY,
    "code_development": OrchestrationMode.CLAUDE_CODE_ONLY,
    "feature_creation": OrchestrationMode.CLAUDE_CODE_ONLY,
    "book_production": OrchestrationMode.HYBRID,
    "quality_assurance": OrchestrationMode.HYBRID,
}
```

### Override Routing
```python
# Force specific mode
task = UnifiedTask(
    id="custom_task",
    type="puzzle_generation",
    mode=OrchestrationMode.CLAUDE_CODE_ONLY  # Override default
)
```

## 📊 Monitoring & Health Checks

### Real-time Monitoring
```python
from src.kindlemint.orchestrator.monitoring import create_monitor

# Create monitor
monitor = create_monitor(orchestrator)

# Start monitoring
await monitor.start_monitoring()

# Get health status
health = monitor.get_health_summary()
print(f"Overall status: {health['overall_status']}")

# Get metrics
metrics = monitor.get_metrics_summary(hours=1)
print(f"Active tasks: {metrics['current']['active_tasks']}")
```

### Health Checks
- **Unified Orchestrator** - Overall system health
- **Claude Code** - Development orchestrator status
- **A2A System** - Agent communication health
- **Puzzle Generator** - Puzzle creation capability
- **PDF Layout** - PDF generation capability

### Metrics Tracked
- Active/completed/failed tasks
- Memory and CPU usage
- Task execution times
- System uptime
- Agent response times

## 🔄 Workflow Examples

### 1. Simple Puzzle Generation
```python
task = UnifiedTask(
    id="puzzles",
    type="puzzle_generation",
    parameters={
        "count": 10,
        "difficulty": "medium"
    }
)
# → Routed to A2A Puzzle Generator Agent
```

### 2. Complete Book Production
```python
task = UnifiedTask(
    id="book",
    type="book_production",
    parameters={
        "book_title": "My Book",
        "puzzle_count": 50,
        "difficulty": "hard"
    }
)
# → Hybrid workflow:
#    1. A2A: Generate puzzles
#    2. A2A: Create PDF
#    3. Claude Code: Quality assurance
```

### 3. Code Development
```python
task = UnifiedTask(
    id="feature",
    type="feature_development",
    parameters={
        "feature_name": "dark_mode",
        "generate_tests": True
    }
)
# → Routed to Claude Code Orchestrator
```

## 🛠️ Advanced Usage

### Custom Agent Registration
```python
# Register new A2A agent
from src.kindlemint.a2a.agent import A2AAgent

class CustomAgent(A2AAgent):
    def __init__(self, registry):
        super().__init__("custom_agent", registry)
        self.add_skill("custom_skill", self._custom_handler, "Description")
    
    async def _custom_handler(self, request):
        return {"success": True, "result": "Custom processing"}

# Register with orchestrator
orchestrator.a2a_agents["custom"] = CustomAgent(orchestrator.a2a_registry)
```

### Custom Workflows
```python
async def custom_workflow(orchestrator, params):
    # Step 1: Generate content with A2A
    content_task = UnifiedTask(
        id="content",
        type="content_generation",
        parameters=params["content"],
        mode=OrchestrationMode.A2A_ONLY
    )
    content_result = await orchestrator.execute_task(content_task)
    
    # Step 2: Process with Claude Code
    processing_task = UnifiedTask(
        id="process",
        type="content_processing",
        parameters={
            "content": content_result["result"],
            "optimization": True
        },
        mode=OrchestrationMode.CLAUDE_CODE_ONLY
    )
    return await orchestrator.execute_task(processing_task)
```

### Error Handling
```python
try:
    result = await orchestrator.execute_task(task)
    if not result["success"]:
        print(f"Task failed: {result['error']}")
        
        # Check task status
        status = orchestrator.get_task_status(task.id)
        print(f"Status: {status}")
        
except Exception as e:
    print(f"Execution error: {e}")
```

## 📋 Task Management

### Task Status Tracking
```python
# Get task status
status = orchestrator.get_task_status("task_id")
print(f"Status: {status['status']}")
print(f"Created: {status['created_at']}")

# List active tasks
active = orchestrator.list_active_tasks()
for task in active:
    print(f"- {task['task_id']}: {task['description']}")
```

### Task Lifecycle
1. **Created** - Task object instantiated
2. **Pending** - Waiting in queue
3. **Running** - Being executed
4. **Completed** - Successfully finished
5. **Failed** - Error occurred

## 🚨 Troubleshooting

### Common Issues

1. **Agent Not Found**
```python
# Check registered agents
status = orchestrator.get_system_status()
agents = status["a2a_system"]["agents"]
print(f"Available agents: {[a['agent_id'] for a in agents]}")
```

2. **Task Routing Issues**
```python
# Force specific mode
task.mode = OrchestrationMode.A2A_ONLY
```

3. **Health Check Failures**
```bash
python unified_orchestrator_cli.py status
```

4. **Performance Issues**
```python
# Check metrics
metrics = monitor.get_metrics_summary()
print(f"Memory usage: {metrics['current']['memory_usage_mb']} MB")
```

### Debug Mode
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Enable detailed logging
orchestrator = create_unified_orchestrator()
```

## 📈 Performance Optimization

### Task Batching
```python
# Batch multiple puzzles
task = UnifiedTask(
    type="puzzle_generation",
    parameters={"count": 100}  # Better than 100 individual tasks
)
```

### Resource Management
```python
# Monitor resource usage
await monitor.start_monitoring()

# Export metrics for analysis
monitor.export_metrics("metrics.json")
```

### Caching
```python
# A2A agents automatically cache validation results
# Claude Code caches generated code patterns
```

## 🔒 Security Considerations

1. **Input Validation** - All A2A agents validate inputs
2. **Error Handling** - Safe error propagation
3. **Resource Limits** - Memory and execution time limits
4. **Sandboxing** - Isolated agent execution

## 🚀 Future Enhancements

- **Distributed Execution** - Multi-node orchestration
- **GPU Acceleration** - For intensive AI tasks
- **Real-time Streaming** - Live task execution updates
- **Web Interface** - Browser-based orchestration dashboard
- **Plugin System** - Custom agent extensions

## 📞 Support

For issues with the unified orchestration system:

1. Check system status: `python unified_orchestrator_cli.py status`
2. Review health checks and metrics
3. Check logs for detailed error information
4. Refer to individual component documentation

---

## 🎉 You're Ready!

Your AI-KindleMint-Engine now has a powerful, unified orchestration system that combines the best of both Claude Code and A2A protocols. Use it to create amazing puzzle books with AI-powered efficiency! 🚀📚

**Happy orchestrating!** 🎭✨