"""
AI API Management System for KindleMint
Handles multiple AI providers, rate limits, and fallback strategies.
"""

# import time # Unused
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional  # List unused

# Attempt to import API clients, they will be None if library not installed
try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Grok client would be imported here if available
# try:
#     import groq_client # Placeholder for actual Grok client library
# except ImportError:
#     groq_client = None

from kindlemint.utils.logger import get_logger


class AIProvider(Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"  # Defined but not fully integrated in logic/costs
    GROK = "grok"


class APIManager:
    """Manages multiple AI API providers with smart routing and fallbacks."""

    def __init__(self):
        """Initialize API manager."""
        self.logger = get_logger("api_manager")
        self.usage_file = (
            Path(__file__).parent.parent.parent / "logs" / "api_usage.json"
        )
        self.usage_file.parent.mkdir(exist_ok=True)

        self.usage_data = self._load_usage_data()

        self.providers = {
            AIProvider.OPENAI: {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "models": {
                    "text": "gpt-4",
                    "image": "dall-e-3",
                    "cheap_text": "gpt-3.5-turbo",
                },
                "rate_limits": {
                    "requests_per_minute": 3000,
                    "tokens_per_minute": 150000,
                    "requests_per_day": 10000,
                },
                "costs": {
                    "gpt-4": {"input": 0.03, "output": 0.06},
                    "gpt-3.5-turbo": {
                        "input": 0.0005,
                        "output": 0.0015,
                    },  # Updated example cost
                    "dall-e-3": 0.040,  # Cost per image (This is a flat rate, not token based for cost)
                },
            },
            AIProvider.GEMINI: {
                "api_key": os.getenv("GEMINI_API_KEY"),
                "models": {
                    "text": "gemini-1.5-flash",
                    "cheap_text": "gemini-1.5-flash",
                },  # Example, could be gemini-pro for quality text
                "rate_limits": {"requests_per_minute": 60, "requests_per_day": 1500},
                "costs": {
                    "gemini-1.5-flash": {
                        "input": 0.000125,
                        "output": 0.000375,
                    }  # Example for Flash per 1K tokens
                    # 'gemini-pro': {'input': 0.0025, 'output': 0.005} # Example for Pro per 1K tokens
                },
            },
            AIProvider.GROK: {
                "api_key": os.getenv("GROK_API_KEY"),
                "models": {
                    "text": "grok-beta",
                    "cheap_text": "grok-beta",
                },  # Placeholder
                "rate_limits": {"requests_per_minute": 1000, "requests_per_day": 10000},
                "costs": {
                    "grok-beta": {"input": 0.005, "output": 0.015}
                },  # Example pricing per 1K tokens
            },
        }

        # Initialize clients
        self.openai_client = None
        if self.providers[AIProvider.OPENAI]["api_key"] and openai:
            try:
                self.openai_client = openai.OpenAI(
                    api_key=self.providers[AIProvider.OPENAI]["api_key"]
                )
                self.logger.info("OpenAI client initialized.")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")

        # For Gemini, API key is configured globally, model chosen per request.
        if self.providers[AIProvider.GEMINI]["api_key"] and genai:
            try:
                genai.configure(api_key=self.providers[AIProvider.GEMINI]["api_key"])
                self.logger.info("Gemini client library configured with API key.")
            except Exception as e:
                self.logger.error(f"Failed to configure Gemini client library: {e}")

        self.grok_client = None  # Placeholder
        # if self.providers[AIProvider.GROK]['api_key'] and groq_client: # Example
        #     try:
        #         self.grok_client = groq_client.Client(api_key=self.providers[AIProvider.GROK]['api_key'])
        #         self.logger.info("Grok client initialized.")
        #     except Exception as e:
        #         self.logger.error(f"Failed to initialize Grok client: {e}")

    def _load_usage_data(self) -> Dict:
        """Load API usage tracking data."""
        if self.usage_file.exists():
            try:
                with open(
                    self.usage_file, "r", encoding="utf-8"
                ) as f:  # Added encoding
                    return json.load(f)
            except json.JSONDecodeError:  # More specific error
                self.logger.error(
                    f"Error decoding JSON from {self.usage_file}. Initializing new usage data."
                )
            except Exception as e:  # Catch other potential errors
                self.logger.error(
                    f"Error loading usage data from {self.usage_file}: {e}. Initializing new usage data."
                )

        return {  # Default structure
            "daily_usage": {},
            "monthly_costs": {},
            "provider_stats": {},
        }

    def _save_usage_data(self):
        """Save usage tracking data."""
        try:
            with open(self.usage_file, "w", encoding="utf-8") as f:  # Added encoding
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save usage data to {self.usage_file}: {e}")

    def get_best_provider_for_task(
        self, task_type: str, priority: str = "balanced"
    ) -> AIProvider:
        """
        Get the best AI provider for a specific task, considering client readiness.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        eligible_providers = []

        for (
            provider_enum,
            config,
        ) in self.providers.items():  # Corrected iteration variable name
            if not config["api_key"]:
                self.logger.debug(
                    f"Provider {provider_enum.value} skipped: No API key."
                )
                continue

            # Check client/library readiness
            if provider_enum == AIProvider.OPENAI and not self.openai_client:
                self.logger.debug(
                    f"Provider {provider_enum.value} skipped: OpenAI client not initialized."
                )
                continue
            if provider_enum == AIProvider.GEMINI and not (
                genai and self.providers[AIProvider.GEMINI]["api_key"]
            ):  # Check genai lib and configured API key
                self.logger.debug(
                    f"Provider {provider_enum.value} skipped: Gemini library or API key not configured."
                )
                continue
            if provider_enum == AIProvider.GROK and not (
                self.grok_client or os.getenv("GROK_API_KEY")
            ):  # Assuming self.grok_client would be set, or check key
                self.logger.debug(
                    f"Provider {provider_enum.value} skipped: Grok API key or client not available."
                )
                continue

            # Check daily limits
            daily_usage = (
                self.usage_data["daily_usage"]
                .get(today, {})
                .get(provider_enum.value, {})
            )
            requests_today = daily_usage.get("requests", 0)
            daily_limit = config["rate_limits"].get("requests_per_day", float("inf"))

            if requests_today < daily_limit:
                eligible_providers.append(provider_enum)
            else:
                self.logger.warning(
                    f"Provider {provider_enum.value} at daily request limit ({requests_today}/{daily_limit})."
                )

        if not eligible_providers:
            self.logger.warning(
                "⚠️ All configured and ready providers are at daily limits or unavailable! Defaulting to OpenAI if configured, else first provider."
            )
            # Fallback to OpenAI if its client is ready, otherwise just the first in the main list (which might be empty)
            return (
                AIProvider.OPENAI
                if self.openai_client
                else (
                    self.providers.keys()[0]
                    if self.providers.keys()
                    else AIProvider.OPENAI
                )
            )

        # Route based on task type and priority
        if task_type == "image_generation":
            if (
                AIProvider.OPENAI in eligible_providers
            ):  # Image gen currently tied to OpenAI
                return AIProvider.OPENAI
            else:
                self.logger.warning(
                    "⚠️ OpenAI not eligible for image generation, though it's the only option. Returning first eligible provider."
                )
                return eligible_providers[0]

        model_key_suffix = "cheap_text" if task_type == "cheap_text" else "text"

        # Cost-driven selection
        order = []
        if priority == "cost":
            cost_priority_order = [
                AIProvider.GEMINI,
                AIProvider.GROK,
                AIProvider.OPENAI,
            ]
            for p in cost_priority_order:
                if p in eligible_providers and self.providers[p]["models"].get(
                    model_key_suffix
                ):
                    order.append(p)
        # Quality-driven selection
        elif priority == "quality":
            quality_priority_order = [
                AIProvider.OPENAI,
                AIProvider.GROK,
                AIProvider.GEMINI,
            ]
            for p in quality_priority_order:
                if p in eligible_providers and self.providers[p]["models"].get(
                    model_key_suffix
                ):
                    order.append(p)

        # If a priority order was established and has candidates, pick the first one
        if order:
            return order[0]

        # Balanced or speed (currently first eligible that has the model type from the eligible_providers list)
        for p in eligible_providers:  # Iterate in current order of eligible_providers
            if self.providers[p]["models"].get(model_key_suffix):
                return p

        self.logger.warning(
            f"No provider found for task '{task_type}' with priority '{priority}' among eligible. Falling back to first eligible provider."
        )
        return eligible_providers[0]

    def generate_text(
        self,
        prompt: str,
        task_type: str = "text_generation",
        priority: str = "balanced",
        max_tokens: int = 1500,
        model_preference: Optional[str] = None,
    ) -> Optional[str]:
        """Generate text using the best available provider and specified model preference."""
        provider = self.get_best_provider_for_task(task_type, priority)

        model_key_for_task = "cheap_text" if task_type == "cheap_text" else "text"
        selected_model_name = model_preference

        if provider and model_preference:
            # Check if the preferred model is valid for this provider (exists in its 'models' dict under any key)
            is_valid_preference = any(
                model_preference == m_name
                for m_name in self.providers[provider]["models"].values()
            )
            if not is_valid_preference:
                self.logger.warning(
                    f"Model preference '{model_preference}' not found for provider {provider.value}. Using provider's default for task type '{model_key_for_task}'."
                )
                selected_model_name = self.providers[provider]["models"].get(
                    model_key_for_task
                )
        elif provider:  # No preference, use provider's default for task type
            selected_model_name = self.providers[provider]["models"].get(
                model_key_for_task
            )

        if (
            not selected_model_name
        ):  # If still no model (e.g. provider has no model for 'cheap_text')
            if provider and self.providers[provider]["models"].get(
                "text"
            ):  # Fallback to provider's main 'text' model
                selected_model_name = self.providers[provider]["models"]["text"]
                self.logger.info(
                    f"No model for '{model_key_for_task}' for {provider.value}, falling back to main text model: {selected_model_name}"
                )
            else:
                self.logger.error(
                    f"Could not determine any model for provider {provider.value if provider else 'N/A'}, task_type {task_type}, preference {model_preference}."
                )
                return None

        self.logger.info(
            f"Attempting text generation with {provider.value} using model {selected_model_name}."
        )

        try:
            if provider == AIProvider.OPENAI:
                if not self.openai_client:
                    raise Exception("OpenAI client not initialized.")
                return self._generate_with_openai(
                    prompt, max_tokens, model_name=selected_model_name
                )
            elif provider == AIProvider.GEMINI:
                if not (genai and self.providers[AIProvider.GEMINI]["api_key"]):
                    raise Exception("Gemini library/API key not configured.")
                return self._generate_with_gemini(
                    prompt, max_tokens, model_name=selected_model_name
                )
            elif provider == AIProvider.GROK:
                # Assumes grok_client or key check is done in _generate_with_grok
                return self._generate_with_grok(
                    prompt, max_tokens, model_name=selected_model_name
                )  # This will raise NotImplementedError
            else:  # Should ideally not be reached if get_best_provider_for_task works
                self.logger.error(
                    f"Unsupported or uninitialized provider determined: {provider}"
                )
                return None
        except Exception as e:
            self.logger.error(
                f"Text generation failed with {provider.value} (model: {selected_model_name}): {e}"
            )

            # Simplified fallback: try OpenAI if it wasn't the primary, then Gemini
            fallback_attempts = []
            if provider != AIProvider.OPENAI and self.openai_client:
                fallback_attempts.append(
                    {"provider": AIProvider.OPENAI, "model_key": "text"}
                )
            if provider != AIProvider.GEMINI and (
                genai and self.providers[AIProvider.GEMINI]["api_key"]
            ):
                fallback_attempts.append(
                    {"provider": AIProvider.GEMINI, "model_key": "text"}
                )

            for attempt in fallback_attempts:
                fb_provider = attempt["provider"]
                fb_model_name = self.providers[fb_provider]["models"].get(
                    attempt["model_key"]
                )
                if not fb_model_name:
                    continue

                try:
                    self.logger.info(
                        f"🔄 Trying fallback: {fb_provider.value} with model {fb_model_name}"
                    )
                    if fb_provider == AIProvider.OPENAI:
                        return self._generate_with_openai(
                            prompt, max_tokens, model_name=fb_model_name
                        )
                    elif fb_provider == AIProvider.GEMINI:
                        return self._generate_with_gemini(
                            prompt, max_tokens, model_name=fb_model_name
                        )
                except Exception as fe:
                    self.logger.warning(
                        f"Fallback {fb_provider.value} (model: {fb_model_name}) also failed: {fe}"
                    )

            self.logger.error(
                f"❌ All text generation attempts failed for prompt (first 50 chars): {prompt[:50]}..."
            )
            return None

    def generate_image(self, prompt: str, size: str = "1024x1024") -> Optional[str]:
        """Generate image using DALL-E (via OpenAI provider)."""
        if not self.openai_client:  # Check if OpenAI client is initialized
            self.logger.warning(
                "⚠️ OpenAI client not initialized. Cannot generate image."
            )
            return None
        try:
            # Image generation model is typically fixed for a provider (e.g., dall-e-3 for OpenAI)
            dalle_model_name = self.providers[AIProvider.OPENAI]["models"]["image"]
            return self._generate_image_with_dalle(
                prompt, size, model_name=dalle_model_name
            )
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            return None

    def _generate_with_openai(
        self, prompt: str, max_tokens: int, model_name: str
    ) -> str:
        """Generate text with OpenAI using the pre-initialized client and specified model."""
        if not self.openai_client:
            self.logger.error("OpenAI client accessed but not initialized.")
            raise Exception("OpenAI client not initialized.")

        self.logger.debug(f"Generating with OpenAI model: {model_name}")
        response = self.openai_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,  # Can be made configurable if needed
        )

        usage = response.usage
        input_tokens = (
            usage.prompt_tokens if usage and hasattr(usage, "prompt_tokens") else 0
        )
        output_tokens = (
            usage.completion_tokens
            if usage and hasattr(usage, "completion_tokens")
            else 0
        )

        self._track_usage(
            AIProvider.OPENAI,
            "text",
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        return response.choices[0].message.content

    def _generate_with_gemini(
        self, prompt: str, max_tokens: int, model_name: str
    ) -> str:
        """Generate text with Gemini using the pre-configured API and specified model."""
        if not (genai and self.providers[AIProvider.GEMINI]["api_key"]):
            self.logger.error(
                "Gemini library or API key not configured when _generate_with_gemini called."
            )
            raise Exception("Gemini library or API key not configured.")

        self.logger.debug(f"Generating with Gemini model: {model_name}")
        active_gemini_model = genai.GenerativeModel(model_name)

        response = active_gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,  # Can be made configurable
            ),
        )

        input_tokens = 0
        output_tokens = 0
        # Attempt to get accurate token counts
        try:
            input_tokens = active_gemini_model.count_tokens(prompt).total_tokens
            # For Gemini, response.usage_metadata might be more accurate for output if available
            if (
                hasattr(response, "usage_metadata")
                and response.usage_metadata
                and hasattr(response.usage_metadata, "candidates_token_count")
            ):
                output_tokens = response.usage_metadata.candidates_token_count
            elif hasattr(
                response, "text"
            ):  # Fallback to counting tokens from response.text if usage_metadata is not helpful
                output_tokens = active_gemini_model.count_tokens(
                    response.text
                ).total_tokens
            else:  # Further fallback if response.text is also not available (should not happen for successful calls)
                self.logger.warning(
                    f"Could not determine output tokens for Gemini model {model_name} from response structure."
                )
        except Exception as e:
            self.logger.warning(
                f"Could not get exact token counts for Gemini model {model_name}: {e}. Estimating."
            )
            input_tokens = len(prompt) // 4  # Rough estimate
            output_tokens = (
                len(response.text) // 4 if hasattr(response, "text") else 0
            )  # Rough estimate

        self._track_usage(
            AIProvider.GEMINI,
            "text",
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        return response.text

    def _generate_with_grok(self, prompt: str, max_tokens: int, model_name: str) -> str:
        """Generate text with Grok (X.AI). Placeholder."""
        if not (
            self.grok_client or os.getenv("GROK_API_KEY")
        ):  # Check if client or at least key is available
            self.logger.error("Grok client/API key accessed but not available.")
            raise Exception("Grok client/API key not available.")
        self.logger.warning(
            f"⚠️ Grok API integration for model {model_name} not yet implemented. Prompt (start): {prompt[:50]}..."
        )
        # Actual Grok call would be here. Example:
        # response = self.grok_client.chat.completions.create(...)
        # self._track_usage(AIProvider.GROK, 'text', model_name=model_name, input_tokens=..., output_tokens=...)
        # return response.choices[0].message.content
        raise NotImplementedError(
            f"Grok API integration for model {model_name} pending"
        )

    def _generate_image_with_dalle(
        self, prompt: str, size: str, model_name: str
    ) -> str:
        """Generate image with DALL-E using the pre-initialized client."""
        if not self.openai_client:
            self.logger.error(
                "OpenAI client (for DALL-E) accessed but not initialized."
            )
            raise Exception("OpenAI client (for DALL-E) not initialized.")

        self.logger.debug(f"Generating image with DALL-E model: {model_name}")
        response = self.openai_client.images.generate(
            model=model_name,  # Use passed model_name, e.g., "dall-e-3"
            prompt=prompt,
            size=size,
            quality="hd",  # Can be made configurable
            n=1,
        )

        image_url = response.data[0].url
        # DALL-E cost is per image, not token based in the same way as text.
        # The 'model_name' here is 'dall-e-3'.
        self._track_usage(
            AIProvider.OPENAI, "image", model_name=model_name, images_generated=1
        )
        return image_url

    def _track_usage(
        self, provider: AIProvider, task_type: str, model_name: str, **kwargs
    ):
        """Track API usage for monitoring and cost control, including per-model stats."""
        today = datetime.now().strftime("%Y-%m-%d")

        provider_value = provider.value  # e.g. "openai"

        # Ensure daily usage structure exists
        if today not in self.usage_data["daily_usage"]:
            self.usage_data["daily_usage"][today] = {}

        # Ensure provider structure for the day exists
        if provider_value not in self.usage_data["daily_usage"][today]:
            self.usage_data["daily_usage"][today][provider_value] = {
                "requests": 0,
                "tokens_input": 0,
                "tokens_output": 0,
                "images": 0,
                "cost": 0.0,
                "model_usage": {},
            }

        usage_today_provider = self.usage_data["daily_usage"][today][provider_value]
        usage_today_provider["requests"] += 1

        # Ensure model usage structure for the provider and day exists
        if model_name not in usage_today_provider["model_usage"]:
            usage_today_provider["model_usage"][model_name] = {
                "requests": 0,
                "tokens_input": 0,
                "tokens_output": 0,
                "images_generated": 0,
                "cost": 0.0,  # Added images_generated here for per-model image tracking
            }

        model_usage_stats = usage_today_provider["model_usage"][model_name]
        model_usage_stats["requests"] += 1

        current_cost = 0.0
        provider_config_block = self.providers.get(
            provider
        )  # Get the whole config for the provider

        if task_type == "text":
            input_tokens = kwargs.get("input_tokens", 0)
            output_tokens = kwargs.get("output_tokens", 0)
            usage_today_provider["tokens_input"] += input_tokens
            usage_today_provider["tokens_output"] += output_tokens
            model_usage_stats["tokens_input"] += input_tokens
            model_usage_stats["tokens_output"] += output_tokens

            if provider_config_block and model_name in provider_config_block["costs"]:
                cost_config_for_model = provider_config_block["costs"][
                    model_name
                ]  # e.g. {'input': 0.03, 'output': 0.06}
                if isinstance(
                    cost_config_for_model, dict
                ):  # Standard input/output cost structure
                    current_cost += (input_tokens / 1000) * cost_config_for_model.get(
                        "input", 0
                    )
                    current_cost += (output_tokens / 1000) * cost_config_for_model.get(
                        "output", 0
                    )
                else:  # Should not happen if config is correct for text models
                    self.logger.warning(
                        f"Cost config for text model {model_name} of {provider_value} is not a dict: {cost_config_for_model}"
                    )
            else:
                self.logger.warning(
                    f"No cost config found for text model {model_name} of {provider_value}"
                )

        elif task_type == "image" and "images_generated" in kwargs:
            images_generated = kwargs["images_generated"]
            usage_today_provider[
                "images"
            ] += images_generated  # Overall images by provider
            model_usage_stats[
                "images_generated"
            ] += images_generated  # Images by this specific model (e.g. dall-e-3)

            if provider_config_block and model_name in provider_config_block["costs"]:
                cost_per_image = provider_config_block["costs"][
                    model_name
                ]  # e.g. dall-e-3: 0.040
                if isinstance(cost_per_image, (float, int)):  # Flat rate for image
                    current_cost += images_generated * cost_per_image
                else:  # Should not happen if config for image model is just a float
                    self.logger.warning(
                        f"Cost config for image model {model_name} of {provider_value} is not a flat rate: {cost_per_image}"
                    )
            else:
                self.logger.warning(
                    f"No cost config found for image model {model_name} of {provider_value}"
                )

        usage_today_provider["cost"] = round(
            usage_today_provider.get("cost", 0.0) + current_cost, 6
        )  # Accumulate and round
        model_usage_stats["cost"] = round(
            model_usage_stats.get("cost", 0.0) + current_cost, 6
        )  # Accumulate and round

        self._save_usage_data()

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get comprehensive usage summary with detailed provider status."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        summary = {
            "daily_totals": {  # Moved totals into a sub-dict for clarity
                "cost": 0.0,
                "requests": 0,
            },
            "today_by_provider": self.usage_data["daily_usage"].get(today_str, {}),
            "yesterday_by_provider": self.usage_data["daily_usage"].get(
                yesterday_str, {}
            ),  # Renamed for clarity
            "provider_status": {},  # Changed from provider_availability for more detailed info
            "recommendations": [],
        }

        # Calculate daily totals
        for _provider_name, provider_data in summary["today_by_provider"].items():
            summary["daily_totals"]["cost"] += provider_data.get("cost", 0)
            summary["daily_totals"]["requests"] += provider_data.get("requests", 0)
        summary["daily_totals"]["cost"] = round(summary["daily_totals"]["cost"], 6)

        # Check provider status
        for p_enum, config in self.providers.items():
            p_value = p_enum.value
            daily_usage = summary["today_by_provider"].get(p_value, {})
            requests_today = daily_usage.get("requests", 0)
            limit = config["rate_limits"].get("requests_per_day", float("inf"))

            api_key_present = bool(config.get("api_key"))
            client_ready = False
            status_detail = "Not configured (No API Key)"

            if api_key_present:
                if p_enum == AIProvider.OPENAI:
                    client_ready = bool(self.openai_client)
                    status_detail = (
                        "OpenAI Client Initialized"
                        if client_ready
                        else "OpenAI Client Failed/Not Initialized"
                    )
                elif p_enum == AIProvider.GEMINI:
                    client_ready = bool(
                        genai and config.get("api_key")
                    )  # Genai lib loaded and key was present for configure()
                    status_detail = (
                        "Gemini Library Configured"
                        if client_ready
                        else "Gemini Library/API Key Not Configured"
                    )
                elif p_enum == AIProvider.GROK:
                    # Assuming self.grok_client would be set if successfully initialized
                    client_ready = bool(
                        self.grok_client or os.getenv("GROK_API_KEY")
                    )  # Looser check if client object not used yet
                    status_detail = (
                        "Grok Configured/Client Ready"
                        if client_ready
                        else "Grok Not Fully Initialized/Client Missing"
                    )
                else:
                    status_detail = "Provider client status unknown"  # For Claude or other future providers

            within_limit = requests_today < limit
            fully_available = api_key_present and client_ready and within_limit

            summary["provider_status"][p_value] = {
                "api_key_set": api_key_present,
                "client_library_ready": client_ready,  # More accurate naming
                "status_detail": status_detail,
                "within_daily_request_limit": within_limit,
                "is_fully_available": fully_available,
                "requests_today": requests_today,
                "daily_request_limit": limit if limit != float("inf") else "Unlimited",
                "cost_today": daily_usage.get("cost", 0),
                "configured_models": list(config.get("models", {}).keys()),
            }

        # Generate recommendations based on new structure
        if summary["daily_totals"]["cost"] > 10:
            summary["recommendations"].append(
                f"⚠️ High API costs today (${summary['daily_totals']['cost']:.2f}). Review usage, consider cost-effective models."
            )

        num_fully_available_providers = sum(
            1 for s in summary["provider_status"].values() if s["is_fully_available"]
        )
        num_configured_providers = sum(
            1 for s in summary["provider_status"].values() if s["api_key_set"]
        )

        if num_configured_providers > 0 and num_fully_available_providers == 0:
            summary["recommendations"].append(
                "🚨 All configured providers are currently unavailable (check limits or client errors). System functionality may be impacted."
            )
        elif num_configured_providers == 0:
            summary["recommendations"].append(
                "🚫 No AI providers appear to be configured with API keys. System will not function."
            )

        # Check primary providers (example: OpenAI and Gemini)
        primary_down_messages = []
        for p_name in [AIProvider.OPENAI.value, AIProvider.GEMINI.value]:
            if (
                p_name in summary["provider_status"]
                and not summary["provider_status"][p_name]["is_fully_available"]
            ):
                reason = (
                    "at limit"
                    if not summary["provider_status"][p_name][
                        "within_daily_request_limit"
                    ]
                    else (
                        "client/config issue"
                        if not summary["provider_status"][p_name][
                            "client_library_ready"
                        ]
                        else "unknown reason"
                    )
                )
                primary_down_messages.append(f"{p_name} ({reason})")

        if len(primary_down_messages) == 2:  # Both primary are down
            summary["recommendations"].append(
                f"🚨 CRITICAL: Both OpenAI & Gemini are down/limited ({'; '.join(primary_down_messages)}). Severe impact likely."
            )
        elif primary_down_messages:
            summary["recommendations"].append(
                f"⚠️ Primary provider issue: {'; '.join(primary_down_messages)} unavailable/limited."
            )

        return summary

    def _get_timestamp(self) -> str:
        """Get timestamp for file naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")


# Global API manager instance
_api_manager = None  # Global instance variable


def get_api_manager() -> APIManager:
    """Get global API manager instance (Singleton pattern)."""
    global _api_manager
    if _api_manager is None:
        # Logger for get_api_manager itself, as self.logger isn't available yet
        # This direct get_logger call might be slightly redundant if APIManager also logs init, but fine for singleton creation log.
        logger_instance_creation = get_logger("api_manager_singleton")
        logger_instance_creation.info("Creating new APIManager instance.")
        _api_manager = APIManager()
        # _api_manager.logger.info("APIManager instance created and assigned globally.") # APIManager __init__ logs this if self.logger is used there
    return _api_manager
