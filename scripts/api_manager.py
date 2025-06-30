#!/usr/bin/env python3
"""
Centralized API Manager
Handles all AI API interactions (OpenAI, DALL-E, Gemini) with consistent error handling,
rate limiting, and configuration management.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APIManager")


class APIProvider(Enum):
    """Supported API providers"""

    OPENAI = "openai"
    DALLE = "dalle"
    GEMINI = "gemini"


@dataclass
class APIConfig:
    """Configuration for API providers"""

    provider: APIProvider
    api_key: Optional[str] = None
    model: Optional[str] = None
    max_retries: int = 3
    timeout: int = 60
    rate_limit_delay: float = 1.0


class APIManager:
    """
    Centralized manager for all AI API interactions.
    Provides consistent interface, error handling, and rate limiting.
    """

        """  Init  """
def __init__(self):
        self.configs = self._load_configs()
        self.clients = self._initialize_clients()
        self.usage_stats = {
            "openai": {"requests": 0, "tokens": 0, "cost": 0.0},
            "dalle": {"requests": 0, "images": 0, "cost": 0.0},
            "gemini": {"requests": 0, "tokens": 0, "cost": 0.0},
        }

    def _load_configs(self) -> Dict[APIProvider, APIConfig]:
        """Load API configurations from environment variables"""
        configs = {}

        # OpenAI configuration
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            configs[APIProvider.OPENAI] = APIConfig(
                provider=APIProvider.OPENAI,
                api_key=openai_key,
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3")),
                timeout=int(os.getenv("OPENAI_TIMEOUT", "60")),
            )
            configs[APIProvider.DALLE] = APIConfig(
                provider=APIProvider.DALLE,
                api_key=openai_key,
                model=os.getenv("DALLE_MODEL", "dall-e-3"),
            )

        # Gemini configuration
        gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            configs[APIProvider.GEMINI] = APIConfig(
                provider=APIProvider.GEMINI,
                api_key=gemini_key,
                model=os.getenv("GEMINI_MODEL", "gemini-pro"),
            )

        return configs

    def _initialize_clients(self) -> Dict[APIProvider, Any]:
        """Initialize API clients"""
        clients = {}

        # Initialize OpenAI client
        if APIProvider.OPENAI in self.configs:
            config = self.configs[APIProvider.OPENAI]
            clients[APIProvider.OPENAI] = OpenAI(api_key=config.api_key)
            clients[APIProvider.DALLE] = clients[APIProvider.OPENAI]  # Same client

        # Initialize Gemini client
        if APIProvider.GEMINI in self.configs:
            config = self.configs[APIProvider.GEMINI]
            genai.configure(api_key=config.api_key)
            clients[APIProvider.GEMINI] = genai.GenerativeModel(config.model)

        return clients

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_text(
        self,
        prompt: str,
        provider: APIProvider = APIProvider.OPENAI,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate text using specified provider

        Args:
            prompt: The user prompt
            provider: API provider to use
            model: Override default model
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: System message for context

        Returns:
            Generated text response
        """
        if provider not in self.clients:
            raise ValueError(f"Provider {provider} not configured")

        config = self.configs[provider]
        model = model or config.model

        try:
            if provider == APIProvider.OPENAI:
                return self._openai_text_generation(
                    prompt, model, temperature, max_tokens, system_prompt
                )
            elif provider == APIProvider.GEMINI:
                return self._gemini_text_generation(prompt, temperature, max_tokens)
            else:
                raise ValueError(f"Text generation not supported for {provider}")

        except Exception as e:
            logger.error(f"API error with {provider}: {e}")
            raise

    def _openai_text_generation(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        system_prompt: Optional[str],
    ) -> str:
        """Generate text using OpenAI"""
        client = self.clients[APIProvider.OPENAI]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Update usage stats
        self.usage_stats["openai"]["requests"] += 1
        if hasattr(response.usage, "total_tokens"):
            self.usage_stats["openai"]["tokens"] += response.usage.total_tokens
            # Rough cost estimate (GPT-4 pricing)
            self.usage_stats["openai"]["cost"] += (
                response.usage.total_tokens / 1000
            ) * 0.03

        return response.choices[0].message.content

    def _gemini_text_generation(
        self, prompt: str, temperature: float, max_tokens: Optional[int]
    ) -> str:
        """Generate text using Gemini"""
        model = self.clients[APIProvider.GEMINI]

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens or 2048,
        }

        response = model.generate_content(prompt, generation_config=generation_config)

        # Update usage stats
        self.usage_stats["gemini"]["requests"] += 1

        return response.text

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        style: Optional[str] = None,
    ) -> List[str]:
        """
        Generate images using DALL-E

        Args:
            prompt: Image generation prompt
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: standard or hd
            n: Number of images to generate
            style: vivid or natural

        Returns:
            List of image URLs
        """
        if APIProvider.DALLE not in self.clients:
            raise ValueError("DALL-E not configured")

        client = self.clients[APIProvider.DALLE]

        # Build request parameters
        params = {
            "model": self.configs[APIProvider.DALLE].model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n,
        }

        if style:
            params["style"] = style

        response = client.images.generate(**params)

        # Update usage stats
        self.usage_stats["dalle"]["requests"] += 1
        self.usage_stats["dalle"]["images"] += n
        # Cost estimate based on quality and size
        cost_per_image = 0.04 if quality == "standard" else 0.08
        if size != "1024x1024":
            cost_per_image *= 1.5
        self.usage_stats["dalle"]["cost"] += cost_per_image * n

        return [image.url for image in response.data]

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return self.usage_stats

        """Reset Usage Stats"""
def reset_usage_stats(self):
        """Reset usage statistics"""
        for provider in self.usage_stats:
            self.usage_stats[provider] = {
                "requests": 0,
                "tokens": 0,
                "images": 0,
                "cost": 0.0,
            }

    def estimate_cost(self, provider: APIProvider, **kwargs) -> float:
        """
        Estimate cost for a specific operation

        Args:
            provider: API provider
            **kwargs: Operation-specific parameters

        Returns:
            Estimated cost in USD
        """
        if provider == APIProvider.OPENAI:
            tokens = kwargs.get("tokens", 1000)
            model = kwargs.get("model", "gpt-4")
            # Rough estimates
            if "gpt-4" in model:
                return (tokens / 1000) * 0.03
            else:
                return (tokens / 1000) * 0.002

        elif provider == APIProvider.DALLE:
            quality = kwargs.get("quality", "standard")
            size = kwargs.get("size", "1024x1024")
            n = kwargs.get("n", 1)

            cost_per_image = 0.04 if quality == "standard" else 0.08
            if size != "1024x1024":
                cost_per_image *= 1.5
            return cost_per_image * n

        elif provider == APIProvider.GEMINI:
            # Gemini is currently free for most use cases
            return 0.0

        return 0.0


# Singleton instance
_api_manager = None


def get_api_manager() -> APIManager:
    """Get or create the singleton APIManager instance"""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIManager()
    return _api_manager


    """Main"""
def main():
    """Example usage and testing"""
    manager = get_api_manager()

    # Example: Generate text
    try:
        response = manager.generate_text(
            prompt="Write a haiku about crossword puzzles",
            provider=APIProvider.OPENAI,
            temperature=0.9,
        )
        print(f"OpenAI Response:\n{response}\n")
    except Exception as e:
        print(f"OpenAI not available: {e}")

    # Example: Generate image
    try:
        urls = manager.generate_image(
            prompt="A cozy reading nook with crossword puzzle books",
            quality="standard",
            size="1024x1024",
        )
        print(f"DALL-E Image URL: {urls[0]}\n")
    except Exception as e:
        print(f"DALL-E not available: {e}")

    # Show usage stats
    stats = manager.get_usage_stats()
    print("\nUsage Statistics:")
    for provider, data in stats.items():
        if data["requests"] > 0:
            print(f"{provider}: {data}")


if __name__ == "__main__":
    main()
