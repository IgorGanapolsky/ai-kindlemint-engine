#!/usr/bin/env python3
"""
Sentry Agent Monitoring for AI Workflows
Provides comprehensive monitoring and debugging for AI agent interactions,
model calls, tool usage, and prompt-response chains.
"""

import functools
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import sentry_sdk
from sentry_sdk.integrations.openai import OpenAIIntegration

# Import the existing Sentry config
from .sentry_config import add_breadcrumb


@dataclass
class AgentContext:
    """Context information for AI agent monitoring"""

    agent_id: str
    agent_type: str  # 'openai', 'claude', 'gemini', etc.
    task_name: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Sentry context"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class PromptTrace:
    """Trace information for prompts and responses"""

    prompt: str
    response: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Sentry context"""
        data = asdict(self)
        # Truncate long prompts/responses for Sentry
        if data["prompt"] and len(data["prompt"]) > 1000:
            data["prompt"] = data["prompt"][:1000] + "... (truncated)"
        if data["response"] and len(data["response"]) > 1000:
            data["response"] = data["response"][:1000] + "... (truncated)"
        return data


class SentryAgentMonitor:
    """
    Enhanced Sentry monitoring for AI agent workflows.
    Tracks prompts, model calls, tool usage, and helps debug AI failures.
    """

    def __init__(self):
        """Initialize the agent monitor with Sentry"""
        # Initialize Sentry with OpenAI integration
        self._init_enhanced_sentry()
        self.active_agents: Dict[str, AgentContext] = {}
        self.trace_history: List[PromptTrace] = []

    def _init_enhanced_sentry(self):
        """Initialize Sentry with AI-specific integrations"""
        sentry_dsn = os.getenv("SENTRY_DSN")

        if not sentry_dsn:
            print("⚠️ No SENTRY_DSN found - Agent monitoring disabled")
            return False

        # Initialize with OpenAI integration for automatic tracing
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("ENVIRONMENT", "production"),
            release=f"kindlemint@{os.getenv('GITHUB_SHA', 'local')[:8]}",
            # Performance monitoring
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            # AI-specific settings
            attach_stacktrace=True,
            send_default_pii=False,  # Important for not sending prompts by default
            max_breadcrumbs=100,  # More breadcrumbs for complex AI workflows
            # Integrations including OpenAI
            integrations=[
                OpenAIIntegration(),  # Default settings for compatibility
            ],
            # Custom tags for AI workflows
            before_send=self._before_send_filter,
        )

        # Set default AI context
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("ai_monitoring", "enabled")
            scope.set_tag("system", "kindlemint-ai-engine")
            scope.set_context(
                "ai_configuration",
                {
                    "monitoring_version": "1.0.0",
                    "agent_types": ["openai", "dalle", "gemini"],
                    "features": ["prompt_tracing", "tool_monitoring", "error_analysis"],
                },
            )

        print("✅ Sentry Agent Monitoring initialized")
        return True

    def _before_send_filter(self, event, hint):
        """Filter sensitive information before sending to Sentry"""
        # Add custom filtering logic here if needed
        # For example, redact API keys, personal information, etc.
        return event

    def start_agent(self, context: AgentContext) -> "AgentTransaction":
        """Start monitoring an AI agent workflow"""
        self.active_agents[context.agent_id] = context

        # Create transaction for the agent workflow
        transaction = sentry_sdk.start_transaction(
            op="ai.agent",
            name=f"{context.agent_type}.{context.task_name}",
            description=f"AI Agent: {context.task_name}",
        )

        # Set agent context
        transaction.set_tag("ai.agent_id", context.agent_id)
        transaction.set_tag("ai.agent_type", context.agent_type)
        transaction.set_tag("ai.model", context.model)
        transaction.set_tag("ai.task", context.task_name)

        transaction.set_context("agent_config", context.to_dict())

        # Add breadcrumb
        add_breadcrumb(
            f"Started AI agent: {context.agent_type}/{context.model}",
            category="ai.agent",
            level="info",
            data=context.to_dict(),
        )

        return AgentTransaction(transaction, context, self)

    def track_prompt(self, agent_id: str, prompt_trace: PromptTrace):
        """Track a prompt/response pair for an agent"""
        self.trace_history.append(prompt_trace)

        with sentry_sdk.configure_scope() as scope:
            # Add prompt trace to breadcrumbs
            add_breadcrumb(
                "AI prompt executed",
                category="ai.prompt",
                level="info",
                data={
                    "agent_id": agent_id,
                    "tokens": prompt_trace.tokens_used,
                    "latency_ms": prompt_trace.latency_ms,
                    "has_error": bool(prompt_trace.error),
                    "tool_calls": len(prompt_trace.tool_calls or []),
                },
            )

            # Store recent prompts in context (last 5)
            recent_traces = [t.to_dict() for t in self.trace_history[-5:]]
            scope.set_context("recent_prompts", {"traces": recent_traces})

    def track_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Any = None,
        error: Optional[Exception] = None,
    ):
        """Track AI agent tool usage"""
        with sentry_sdk.configure_scope() as scope:
            tool_data = {
                "agent_id": agent_id,
                "tool": tool_name,
                "input": str(tool_input)[:500],  # Truncate for size
                "success": error is None,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if tool_output is not None:
                tool_data["output_preview"] = str(tool_output)[:500]

            if error:
                tool_data["error"] = str(error)

            add_breadcrumb(
                f"Tool call: {tool_name}",
                category="ai.tool",
                level="error" if error else "info",
                data=tool_data,
            )

            # Update tool usage context
            scope.set_context("last_tool_call", tool_data)

    def capture_ai_error(
        self, agent_id: str, error: Exception, context: Optional[Dict[str, Any]] = None
    ):
        """Capture AI-specific errors with enhanced context"""
        agent_context = self.active_agents.get(agent_id)

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("ai.error_type", type(error).__name__)
            scope.set_tag("ai.agent_id", agent_id)

            if agent_context:
                scope.set_context("agent_state", agent_context.to_dict())

            # Add recent prompt history
            if self.trace_history:
                recent_prompts = [t.to_dict() for t in self.trace_history[-3:]]
                scope.set_context("prompt_history", {"recent": recent_prompts})

            # Add custom error context
            if context:
                scope.set_context("error_details", context)

            # Determine if this is a common AI error
            ai_error_types = {
                "token limit": "ai.error.token_limit",
                "rate limit": "ai.error.rate_limit",
                "invalid response": "ai.error.invalid_response",
                "tool error": "ai.error.tool_failure",
                "json parsing": "ai.error.json_parsing",
            }

            error_str = str(error).lower()
            for key, tag in ai_error_types.items():
                if key in error_str:
                    scope.set_tag("ai.error_category", tag)
                    break

        return sentry_sdk.capture_exception(error)


class AgentTransaction:
    """Context manager for AI agent transactions"""

    def __init__(self, transaction, context: AgentContext, monitor: SentryAgentMonitor):
        self.transaction = transaction
        self.context = context
        self.monitor = monitor
        self.start_time = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.monitor.capture_ai_error(
                self.context.agent_id, exc_val, {"transaction": self.context.task_name}
            )

        # Calculate total execution time
        execution_time = time.time() - self.start_time
        self.transaction.set_measurement("ai.execution_time", execution_time)

        # Finish transaction
        self.transaction.finish()

        # Clean up active agent
        if self.context.agent_id in self.monitor.active_agents:
            del self.monitor.active_agents[self.context.agent_id]

        return False  # Don't suppress exceptions

    def track_prompt(
        self,
        prompt: str,
        response: str = None,
        tokens: int = None,
        latency_ms: float = None,
        tool_calls: List[Dict[str, Any]] = None,
    ):
        """Track a prompt within this transaction"""
        trace = PromptTrace(
            prompt=prompt,
            response=response,
            tokens_used=tokens,
            latency_ms=latency_ms,
            tool_calls=tool_calls,
        )
        self.monitor.track_prompt(self.context.agent_id, trace)

        # Add span for this prompt
        with self.transaction.start_child(
            op="ai.prompt", description=f"Prompt: {prompt[:100]}..."
        ) as span:
            if tokens:
                span.set_measurement("ai.tokens", tokens)
            if latency_ms:
                span.set_measurement("ai.latency", latency_ms)
            if tool_calls:
                span.set_tag("ai.has_tools", "true")
                span.set_data("tool_count", len(tool_calls))


# Decorator for monitoring AI functions
def monitor_ai_agent(agent_type: str, task_name: str, model: str = None):
    """Decorator to automatically monitor AI agent functions"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create agent context
            context = AgentContext(
                agent_id=f"{agent_type}_{int(time.time() * 1000)}",
                agent_type=agent_type,
                task_name=task_name,
                model=model or kwargs.get("model", "unknown"),
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens"),
                metadata={"function": func.__name__, "module": func.__module__},
            )

            # Get or create monitor instance
            monitor = SentryAgentMonitor()

            # Start monitoring
            with monitor.start_agent(context) as transaction:
                # Inject transaction into kwargs for function to use
                kwargs["_sentry_transaction"] = transaction

                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception:
                    # Error is automatically captured by context manager
                    raise

        return wrapper

    return decorator


# Global monitor instance
_global_monitor = None


def get_agent_monitor() -> SentryAgentMonitor:
    """Get the global agent monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = SentryAgentMonitor()
    return _global_monitor


# Example usage functions
def example_monitored_ai_function():
    """Example of how to use the agent monitoring"""
    monitor = get_agent_monitor()

    # Create agent context
    context = AgentContext(
        agent_id="example_001",
        agent_type="openai",
        task_name="generate_crossword_clues",
        model="gpt-4",
        temperature=0.7,
        max_tokens=1000,
    )

    # Start monitoring
    with monitor.start_agent(context) as transaction:
        # Simulate prompt
        prompt = "Generate 5 crossword clues for common 3-letter words"

        # Track the prompt (before making actual API call)
        transaction.track_prompt(
            prompt=prompt,
            response="1. Feline pet (CAT)\n2. Canine companion (DOG)...",
            tokens=150,
            latency_ms=523.4,
        )

        # Track tool usage
        monitor.track_tool_call(
            agent_id=context.agent_id,
            tool_name="validate_clues",
            tool_input={"clues": ["Feline pet", "Canine companion"]},
            tool_output={"valid": True, "score": 0.95},
        )

        # Simulate an error
        try:
            # Some operation that might fail
            raise ValueError("Invalid clue format detected")
        except Exception as e:
            monitor.capture_ai_error(
                context.agent_id, e, {"step": "clue_validation", "clue_index": 3}
            )


if __name__ == "__main__":
    # Test the monitoring
    example_monitored_ai_function()
    print("✅ Agent monitoring example completed")
