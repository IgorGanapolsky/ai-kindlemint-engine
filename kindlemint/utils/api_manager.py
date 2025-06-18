"""
AI API Management System for KindleMint
Handles multiple AI providers, rate limits, and fallback strategies.
"""
import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

from kindlemint.utils.logger import get_logger

class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    GROK = "grok"

class APIManager:
    """Manages multiple AI API providers with smart routing and fallbacks."""
    
    def __init__(self):
        """Initialize API manager."""
        self.logger = get_logger('api_manager')
        self.usage_file = Path(__file__).parent.parent.parent / "logs" / "api_usage.json"
        self.usage_file.parent.mkdir(exist_ok=True)
        
        # Load usage tracking
        self.usage_data = self._load_usage_data()
        
        # API configurations
        self.providers = {
            AIProvider.OPENAI: {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'models': {
                    'text': 'gpt-4',
                    'image': 'dall-e-3',
                    'cheap_text': 'gpt-3.5-turbo'
                },
                'rate_limits': {
                    'requests_per_minute': 3000,  # Tier 4
                    'tokens_per_minute': 150000,   # Tier 4
                    'requests_per_day': 10000
                },
                'costs': {
                    'gpt-4': {'input': 0.03, 'output': 0.06},  # per 1K tokens
                    'gpt-3.5-turbo': {'input': 0.002, 'output': 0.002},
                    'dall-e-3': 0.040  # per image
                }
            },
            AIProvider.GEMINI: {
                'api_key': os.getenv('GEMINI_API_KEY'),
                'models': {
                    'text': 'gemini-1.5-flash',
                    'cheap_text': 'gemini-1.5-flash'
                },
                'rate_limits': {
                    'requests_per_minute': 60,
                    'requests_per_day': 1500
                },
                'costs': {
                    'gemini-pro': {'input': 0.00025, 'output': 0.0005}  # Much cheaper!
                }
            },
            AIProvider.GROK: {
                'api_key': os.getenv('GROK_API_KEY'),  # X.AI API
                'models': {
                    'text': 'grok-beta',
                    'cheap_text': 'grok-beta'
                },
                'rate_limits': {
                    'requests_per_minute': 1000,
                    'requests_per_day': 10000
                },
                'costs': {
                    'grok-beta': {'input': 0.005, 'output': 0.015}  # Competitive pricing
                }
            }
        }
    
    def _load_usage_data(self) -> Dict:
        """Load API usage tracking data."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            'daily_usage': {},
            'monthly_costs': {},
            'provider_stats': {}
        }
    
    def _save_usage_data(self):
        """Save usage tracking data."""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save usage data: {e}")
    
    def get_best_provider_for_task(self, task_type: str, priority: str = 'balanced') -> AIProvider:
        """
        Get the best AI provider for a specific task.
        
        Args:
            task_type: 'text_generation', 'image_generation', 'cheap_text'
            priority: 'cost', 'quality', 'speed', 'balanced'
        """
        today = datetime.now().strftime('%Y-%m-%d')
        available_providers = []
        
        # Check which providers are available and under limits
        for provider, config in self.providers.items():
            if not config['api_key']:
                continue
            
            # Check daily limits
            daily_usage = self.usage_data['daily_usage'].get(today, {}).get(provider.value, {})
            requests_today = daily_usage.get('requests', 0)
            daily_limit = config['rate_limits'].get('requests_per_day', float('inf'))
            
            if requests_today < daily_limit:
                available_providers.append(provider)
        
        if not available_providers:
            self.logger.warning("⚠️ All providers at daily limits!")
            return AIProvider.GEMINI  # Fallback to Gemini (usually has higher limits)
        
        # Route based on task type and priority
        if task_type == 'image_generation':
            if AIProvider.OPENAI in available_providers:
                return AIProvider.OPENAI
            else:
                self.logger.warning("⚠️ No image generation providers available")
                return AIProvider.OPENAI  # Still return for fallback handling
        
        elif task_type == 'cheap_text' or priority == 'cost':
            # Prefer Gemini for cost-effective text generation
            if AIProvider.GEMINI in available_providers:
                return AIProvider.GEMINI
            elif AIProvider.GROK in available_providers:
                return AIProvider.GROK
            elif AIProvider.OPENAI in available_providers:
                return AIProvider.OPENAI
        
        elif priority == 'quality':
            # Prefer OpenAI GPT-4 for highest quality
            if AIProvider.OPENAI in available_providers:
                return AIProvider.OPENAI
            elif AIProvider.GROK in available_providers:
                return AIProvider.GROK
            elif AIProvider.GEMINI in available_providers:
                return AIProvider.GEMINI
        
        else:  # balanced or speed
            # Distribute load across available providers
            return available_providers[0]  # Simple rotation
    
    def generate_text(self, prompt: str, task_type: str = 'text_generation', 
                     priority: str = 'balanced', max_tokens: int = 1500) -> Optional[str]:
        """Generate text using the best available provider."""
        provider = self.get_best_provider_for_task(task_type, priority)
        
        try:
            if provider == AIProvider.OPENAI:
                return self._generate_with_openai(prompt, max_tokens)
            elif provider == AIProvider.GEMINI:
                return self._generate_with_gemini(prompt, max_tokens)
            elif provider == AIProvider.GROK:
                return self._generate_with_grok(prompt, max_tokens)
            else:
                self.logger.error(f"Unsupported provider: {provider}")
                return None
                
        except Exception as e:
            self.logger.error(f"Text generation failed with {provider.value}: {e}")
            
            # Try fallback provider
            fallback_providers = [p for p in [AIProvider.GEMINI, AIProvider.GROK, AIProvider.OPENAI] 
                                 if p != provider and self.providers[p]['api_key']]
            
            for fallback in fallback_providers:
                try:
                    self.logger.info(f"🔄 Trying fallback provider: {fallback.value}")
                    if fallback == AIProvider.GEMINI:
                        return self._generate_with_gemini(prompt, max_tokens)
                    elif fallback == AIProvider.GROK:
                        return self._generate_with_grok(prompt, max_tokens)
                    elif fallback == AIProvider.OPENAI:
                        return self._generate_with_openai(prompt, max_tokens)
                except Exception as fe:
                    self.logger.warning(f"Fallback {fallback.value} also failed: {fe}")
                    continue
            
            self.logger.error("❌ All text generation providers failed")
            return None
    
    def generate_image(self, prompt: str, size: str = "1024x1024") -> Optional[str]:
        """Generate image using DALL-E with fallback handling."""
        try:
            if not self.providers[AIProvider.OPENAI]['api_key']:
                self.logger.warning("⚠️ OpenAI API key not available for image generation")
                return None
            
            return self._generate_image_with_dalle(prompt, size)
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            return None
    
    def _generate_with_openai(self, prompt: str, max_tokens: int) -> str:
        """Generate text with OpenAI."""
        import openai
        
        client = openai.OpenAI(api_key=self.providers[AIProvider.OPENAI]['api_key'])
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        self._track_usage(AIProvider.OPENAI, 'text', tokens_used=max_tokens)
        return response.choices[0].message.content
    
    def _generate_with_gemini(self, prompt: str, max_tokens: int) -> str:
        """Generate text with Gemini."""
        import google.generativeai as genai
        
        genai.configure(api_key=self.providers[AIProvider.GEMINI]['api_key'])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(prompt)
        
        self._track_usage(AIProvider.GEMINI, 'text', tokens_used=max_tokens)
        return response.text
    
    def _generate_with_grok(self, prompt: str, max_tokens: int) -> str:
        """Generate text with Grok (X.AI)."""
        # Note: This would need X.AI's actual API implementation
        # For now, return a placeholder
        self.logger.warning("⚠️ Grok API integration not yet implemented")
        raise NotImplementedError("Grok API integration pending")
    
    def _generate_image_with_dalle(self, prompt: str, size: str) -> str:
        """Generate image with DALL-E."""
        import openai
        import requests
        
        client = openai.OpenAI(api_key=self.providers[AIProvider.OPENAI]['api_key'])
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="hd",
            n=1
        )
        
        image_url = response.data[0].url
        self._track_usage(AIProvider.OPENAI, 'image', images_generated=1)
        
        return image_url
    
    def _track_usage(self, provider: AIProvider, task_type: str, **kwargs):
        """Track API usage for monitoring and cost control."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.usage_data['daily_usage']:
            self.usage_data['daily_usage'][today] = {}
        
        if provider.value not in self.usage_data['daily_usage'][today]:
            self.usage_data['daily_usage'][today][provider.value] = {
                'requests': 0,
                'tokens': 0,
                'images': 0,
                'cost': 0.0
            }
        
        # Update usage stats
        usage = self.usage_data['daily_usage'][today][provider.value]
        usage['requests'] += 1
        
        if 'tokens_used' in kwargs:
            usage['tokens'] += kwargs['tokens_used']
        
        if 'images_generated' in kwargs:
            usage['images'] += kwargs['images_generated']
        
        # Calculate cost (simplified)
        if task_type == 'text' and 'tokens_used' in kwargs:
            model_costs = self.providers[provider]['costs']
            if provider == AIProvider.OPENAI:
                usage['cost'] += (kwargs['tokens_used'] / 1000) * model_costs['gpt-4']['input']
            elif provider == AIProvider.GEMINI:
                usage['cost'] += (kwargs['tokens_used'] / 1000) * model_costs['gemini-pro']['input']
        
        elif task_type == 'image':
            usage['cost'] += self.providers[provider]['costs']['dall-e-3']
        
        self._save_usage_data()
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get comprehensive usage summary."""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        this_month = datetime.now().strftime('%Y-%m')
        
        summary = {
            'today': self.usage_data['daily_usage'].get(today, {}),
            'yesterday': self.usage_data['daily_usage'].get(yesterday, {}),
            'total_cost_today': 0.0,
            'total_requests_today': 0,
            'provider_availability': {},
            'recommendations': []
        }
        
        # Calculate totals
        for provider_data in summary['today'].values():
            summary['total_cost_today'] += provider_data.get('cost', 0)
            summary['total_requests_today'] += provider_data.get('requests', 0)
        
        # Check provider availability
        for provider, config in self.providers.items():
            daily_usage = summary['today'].get(provider.value, {})
            requests_today = daily_usage.get('requests', 0)
            daily_limit = config['rate_limits'].get('requests_per_day', float('inf'))
            
            summary['provider_availability'][provider.value] = {
                'available': bool(config['api_key']) and requests_today < daily_limit,
                'requests_used': requests_today,
                'daily_limit': daily_limit,
                'cost_today': daily_usage.get('cost', 0)
            }
        
        # Generate recommendations
        if summary['total_cost_today'] > 10:  # $10 threshold
            summary['recommendations'].append("⚠️ High API costs today - consider using Gemini for text generation")
        
        if not any(p['available'] for p in summary['provider_availability'].values()):
            summary['recommendations'].append("🚨 All providers at limits - consider upgrading plans")
        
        return summary
    
    def _get_timestamp(self) -> str:
        """Get timestamp for file naming."""
        return datetime.now().strftime('%Y%m%d_%H%M%S')

# Global API manager instance
_api_manager = None

def get_api_manager() -> APIManager:
    """Get global API manager instance."""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIManager()
    return _api_manager