#!/usr/bin/env python3
"""
Enhanced API Manager with Sentry Agent Monitoring
Integrates AI API calls with Sentry's new Agent Monitoring for debugging
"""

import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import google.generativeai as genai
import openai
from openai import OpenAI

# Import the original API manager and Sentry monitoring
from scripts.api_manager import APIConfig, APIManager, APIProvider
from scripts.sentry_agent_monitoring import (
    AgentContext,
    PromptTrace,
    get_agent_monitor,
    monitor_ai_agent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnhancedAPIManager")


class EnhancedAPIManager(APIManager):
    """
    Enhanced API Manager with Sentry Agent Monitoring integration.
    Automatically tracks all AI interactions for debugging.
    """

    def __init__(self):
        super().__init__()
        self.monitor = get_agent_monitor()
        logger.info("✅ Enhanced API Manager with Agent Monitoring initialized")

    def generate_text(
        self,
        prompt: str,
        provider: APIProvider = APIProvider.OPENAI,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        task_name: str = "text_generation",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate text with full agent monitoring.
        Tracks prompts, responses, tool usage, and errors.
        """

        # Create agent context for monitoring
        context = AgentContext(
            agent_id=f"{provider.value}_{int(time.time() * 1000)}",
            agent_type=provider.value,
            task_name=task_name,
            model=model
            or self.configs.get(provider, APIConfig(provider=provider)).model,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata={
                "has_system_prompt": bool(system_prompt),
                "has_tools": bool(tools),
                "additional_params": kwargs,
            },
        )

        # Start monitoring transaction
        with self.monitor.start_agent(context) as transaction:
            start_time = time.time()

            try:
                # Track the prompt
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

                # Call the appropriate provider
                if provider == APIProvider.OPENAI:
                    result = self._call_openai(
                        prompt,
                        model,
                        temperature,
                        max_tokens,
                        system_prompt,
                        tools,
                        **kwargs,
                    )
                elif provider == APIProvider.GEMINI:
                    result = self._call_gemini(
                        prompt, model, temperature, max_tokens, system_prompt, **kwargs
                    )
                else:
                    raise ValueError(f"Unsupported provider: {provider}")

                # Calculate metrics
                latency_ms = (time.time() - start_time) * 1000

                # Track successful completion
                transaction.track_prompt(
                    prompt=full_prompt,
                    response=result.get("text", ""),
                    tokens=result.get("usage", {}).get("total_tokens"),
                    latency_ms=latency_ms,
                    tool_calls=result.get("tool_calls", []),
                )

                # Track any tool calls
                if result.get("tool_calls"):
                    for tool_call in result["tool_calls"]:
                        self.monitor.track_tool_call(
                            agent_id=context.agent_id,
                            tool_name=tool_call.get("name", "unknown"),
                            tool_input=tool_call.get("arguments", {}),
                            tool_output=tool_call.get("output"),
                        )

                # Update usage stats
                self._update_usage_stats(provider, result)

                return result

            except Exception as e:
                # Capture AI-specific error with context
                error_context = {
                    "provider": provider.value,
                    "model": model,
                    "prompt_length": len(prompt),
                    "has_tools": bool(tools),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }

                # Check for specific error types
                if "rate_limit" in str(e).lower():
                    error_context["error_category"] = "rate_limit"
                elif "token" in str(e).lower() and "limit" in str(e).lower():
                    error_context["error_category"] = "token_limit"
                elif "json" in str(e).lower():
                    error_context["error_category"] = "json_parsing"

                self.monitor.capture_ai_error(context.agent_id, e, error_context)

                raise

    def _call_openai(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
        system_prompt: Optional[str],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Call OpenAI API with monitoring"""

        client = self.clients.get(APIProvider.OPENAI)
        if not client:
            raise ValueError("OpenAI client not initialized")

        config = self.configs[APIProvider.OPENAI]
        model = model or config.model

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Prepare API call parameters
        params = {"model": model, "messages": messages, "temperature": temperature}

        if max_tokens:
            params["max_tokens"] = max_tokens

        if tools:
            params["tools"] = tools
            params["tool_choice"] = kwargs.get("tool_choice", "auto")

        # Make API call
        response = client.chat.completions.create(**params)

        # Parse response
        result = {
            "text": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "finish_reason": response.choices[0].finish_reason,
        }

        # Handle tool calls if present
        if (
            hasattr(response.choices[0].message, "tool_calls")
            and response.choices[0].message.tool_calls
        ):
            result["tool_calls"] = []
            for tool_call in response.choices[0].message.tool_calls:
                result["tool_calls"].append(
                    {
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments),
                    }
                )

        return result

    def _call_gemini(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
        system_prompt: Optional[str],
        **kwargs,
    ) -> Dict[str, Any]:
        """Call Gemini API with monitoring"""

        config = self.configs.get(APIProvider.GEMINI)
        if not config:
            raise ValueError("Gemini not configured")

        genai.configure(api_key=config.api_key)
        model = genai.GenerativeModel(model or config.model)

        # Build prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        # Generate
        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )

        # Parse response
        result = {
            "text": response.text,
            "model": model.model_name,
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            },
        }

        return result

    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        task_name: str = "image_generation",
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate image with monitoring"""

        context = AgentContext(
            agent_id=f"dalle_{int(time.time() * 1000)}",
            agent_type="dalle",
            task_name=task_name,
            model=self.configs.get(
                APIProvider.DALLE, APIConfig(provider=APIProvider.DALLE)
            ).model,
            metadata={"size": size, "quality": quality, "count": n},
        )

        with self.monitor.start_agent(context) as transaction:
            start_time = time.time()

            try:
                client = self.clients.get(APIProvider.DALLE)
                if not client:
                    raise ValueError("DALL-E client not initialized")

                # Generate image
                response = client.images.generate(
                    model=self.configs[APIProvider.DALLE].model,
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=n,
                )

                # Calculate metrics
                latency_ms = (time.time() - start_time) * 1000

                # Track the generation
                transaction.track_prompt(
                    prompt=prompt,
                    response=f"Generated {n} image(s)",
                    latency_ms=latency_ms,
                )

                # Parse response
                result = {
                    "images": [img.url for img in response.data],
                    "revised_prompt": (
                        response.data[0].revised_prompt
                        if hasattr(response.data[0], "revised_prompt")
                        else prompt
                    ),
                }

                # Update usage stats
                self.usage_stats["dalle"]["requests"] += 1
                self.usage_stats["dalle"]["images"] += n

                return result

            except Exception as e:
                self.monitor.capture_ai_error(
                    context.agent_id,
                    e,
                    {"prompt_length": len(prompt), "size": size, "quality": quality},
                )
                raise

    def _update_usage_stats(self, provider: APIProvider, result: Dict[str, Any]):
        """Update usage statistics"""
        provider_key = provider.value

        self.usage_stats[provider_key]["requests"] += 1

        if "usage" in result:
            usage = result["usage"]
            self.usage_stats[provider_key]["tokens"] += usage.get("total_tokens", 0)

            # Estimate costs (example rates)
            if provider == APIProvider.OPENAI:
                # Example: $0.03 per 1K tokens for GPT-4
                cost = (usage.get("total_tokens", 0) / 1000) * 0.03
                self.usage_stats[provider_key]["cost"] += cost

    def batch_generate(
        self,
        prompts: List[str],
        provider: APIProvider = APIProvider.OPENAI,
        task_name: str = "batch_generation",
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Batch generate with monitoring.
        Useful for processing multiple prompts efficiently.
        """

        results = []

        # Create a parent context for the batch
        batch_context = AgentContext(
            agent_id=f"batch_{int(time.time() * 1000)}",
            agent_type=f"{provider.value}_batch",
            task_name=task_name,
            model=kwargs.get(
                "model", self.configs.get(provider, APIConfig(provider=provider)).model
            ),
            metadata={"batch_size": len(prompts), "provider": provider.value},
        )

        with self.monitor.start_agent(batch_context) as batch_transaction:
            for i, prompt in enumerate(prompts):
                try:
                    # Generate with individual task name
                    result = self.generate_text(
                        prompt=prompt,
                        provider=provider,
                        task_name=f"{task_name}_item_{i}",
                        **kwargs,
                    )
                    results.append({"index": i, "success": True, "result": result})

                except Exception as e:
                    # Track failed items
                    results.append({"index": i, "success": False, "error": str(e)})

                    # Log but continue batch
                    logger.error(f"Batch item {i} failed: {e}")

            # Summary tracking
            successful = sum(1 for r in results if r["success"])
            batch_transaction.track_prompt(
                prompt=f"Batch of {len(prompts)} prompts",
                response=f"Completed {successful}/{len(prompts)} successfully",
                latency_ms=None,  # Individual items tracked their own latency
            )

        return results

    def get_usage_report(self) -> Dict[str, Any]:
        """Get usage statistics with monitoring context"""
        report = {
            "usage_stats": self.usage_stats,
            "monitoring": {
                "active_agents": len(self.monitor.active_agents),
                "trace_history_count": len(self.monitor.trace_history),
            },
            "timestamp": time.time(),
        }

        # Add to Sentry context
        with get_agent_monitor() as monitor:
            monitor.add_breadcrumb(
                "Usage report generated", category="ai.analytics", data=report
            )

        return report


# Convenience decorator for monitored AI functions
def with_ai_monitoring(task_name: str, provider: APIProvider = APIProvider.OPENAI):
    """Decorator to add AI monitoring to any function using the API manager"""

    def decorator(func):
        @monitor_ai_agent(agent_type=provider.value, task_name=task_name)
        def wrapper(*args, **kwargs):
            # Inject enhanced API manager if not present
            if "api_manager" not in kwargs:
                kwargs["api_manager"] = EnhancedAPIManager()
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Export the main classes and functions
__all__ = ["EnhancedAPIManager", "with_ai_monitoring", "APIProvider", "APIConfig"]


# Example usage
if __name__ == "__main__":
    # Initialize enhanced manager
    manager = EnhancedAPIManager()

    # Example 1: Simple text generation with monitoring
    try:
        result = manager.generate_text(
            prompt="Generate 3 crossword clues for the word CAT",
            task_name="crossword_clue_generation",
            temperature=0.7,
            max_tokens=150,
        )
        print("Generated clues:", result.get("text"))

    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Batch generation
    prompts = [
        "Generate a clue for DOG",
        "Generate a clue for SUN",
        "Generate a clue for MOON",
    ]

    batch_results = manager.batch_generate(
        prompts=prompts, task_name="batch_clue_generation"
    )

    print(f"\nBatch results: {len(batch_results)} items processed")

    # Get usage report
    report = manager.get_usage_report()
    print(f"\nUsage Report: {json.dumps(report, indent=2)}")
