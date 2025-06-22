#!/usr/bin/env python3
"""
CostTracker Agent - Precise cost calculation for each book
Tracks API calls (OpenAI, DALL-E) and AWS compute costs to calculate true book production costs
"""
import os
import json
import time
import boto3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP

# Sentry integration
try:
    from ..utils.sentry_config import capture_business_event, SentryPerformanceTracker
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

@dataclass
class APICallCost:
    """Represents the cost of a single API call."""
    service: str  # openai, dalle, gemini
    operation: str  # chat, completion, image_generation
    tokens_or_units: int
    cost_per_unit: float
    total_cost: float
    timestamp: str
    book_id: Optional[str] = None
    volume_number: Optional[int] = None
    
@dataclass
class AWSComputeCost:
    """Represents AWS compute costs for a specific operation."""
    service: str  # lambda, fargate, ec2
    operation: str  # book_generation, publishing, processing
    duration_seconds: float
    compute_units: float  # vCPU seconds, GB-seconds, etc.
    cost_per_unit: float
    total_cost: float
    timestamp: str
    book_id: Optional[str] = None
    volume_number: Optional[int] = None

@dataclass
class BookProductionCost:
    """Complete cost breakdown for producing a single book."""
    book_id: str
    series_name: str
    volume_number: int
    production_date: str
    
    # API costs
    openai_costs: List[APICallCost]
    dalle_costs: List[APICallCost]
    gemini_costs: List[APICallCost]
    
    # AWS costs
    lambda_costs: List[AWSComputeCost]
    fargate_costs: List[AWSComputeCost]
    
    # Totals
    total_api_cost: float
    total_aws_cost: float
    total_production_cost: float
    
    # Metadata
    tokens_used: int
    images_generated: int
    compute_time_seconds: float

class CostTracker:
    """Tracks and calculates precise costs for book production."""
    
    # Current pricing (as of 2024 - update regularly)
    PRICING = {
        'openai': {
            'gpt-4': {'input': 0.00003, 'output': 0.00006},  # per token
            'gpt-3.5-turbo': {'input': 0.0000015, 'output': 0.000002},
            'text-embedding-ada-002': 0.0000001,
        },
        'dalle': {
            'dall-e-3': {'1024x1024': 0.040, '1024x1792': 0.080, '1792x1024': 0.080},
            'dall-e-2': {'1024x1024': 0.020, '512x512': 0.018, '256x256': 0.016},
        },
        'gemini': {
            'gemini-pro': {'input': 0.00025, 'output': 0.0005},  # per 1K characters
        },
        'aws': {
            'lambda': 0.0000166667,  # per GB-second
            'fargate': {'vcpu': 0.04048, 'memory': 0.004445},  # per vCPU-hour, per GB-hour
            'ecr': 0.10,  # per GB-month
        }
    }
    
    def __init__(self):
        self.costs_dir = Path("output/cost_tracking")
        self.costs_dir.mkdir(parents=True, exist_ok=True)
        
        # Current tracking session
        self.session_id = f"session_{int(time.time())}"
        self.current_book_id = None
        self.current_volume = None
        
        # Cost accumulation for current book
        self.api_calls: List[APICallCost] = []
        self.aws_costs: List[AWSComputeCost] = []
        
        # AWS clients for cost analysis
        self.setup_aws_clients()
        
    def setup_aws_clients(self):
        """Setup AWS clients for cost tracking."""
        try:
            self.cost_explorer = boto3.client('ce')
            self.cloudwatch = boto3.client('cloudwatch')
            self.pricing = boto3.client('pricing', region_name='us-east-1')
        except Exception as e:
            print(f"⚠️ AWS clients setup failed: {e}")
            self.cost_explorer = None
            self.cloudwatch = None
            self.pricing = None
    
    def start_book_tracking(self, book_id: str, series_name: str, volume_number: int):
        """Start cost tracking for a new book production."""
        self.current_book_id = book_id
        self.current_volume = volume_number
        self.current_series = series_name
        
        # Clear previous tracking
        self.api_calls.clear()
        self.aws_costs.clear()
        
        if SENTRY_AVAILABLE:
            capture_business_event("cost_tracking_started", 
                                 f"Started cost tracking for {book_id}",
                                 extra_data={"book_id": book_id, "volume": volume_number})
        
        print(f"💰 COST TRACKING: Started for {book_id} (Volume {volume_number})")
    
    def track_openai_call(self, 
                         model: str,
                         input_tokens: int, 
                         output_tokens: int,
                         operation: str = "completion") -> float:
        """Track an OpenAI API call and calculate cost."""
        pricing = self.PRICING['openai'].get(model, self.PRICING['openai']['gpt-4'])
        
        input_cost = input_tokens * pricing['input']
        output_cost = output_tokens * pricing['output']
        total_cost = input_cost + output_cost
        
        call_cost = APICallCost(
            service="openai",
            operation=f"{model}_{operation}",
            tokens_or_units=input_tokens + output_tokens,
            cost_per_unit=(input_cost + output_cost) / (input_tokens + output_tokens),
            total_cost=total_cost,
            timestamp=datetime.now().isoformat(),
            book_id=self.current_book_id,
            volume_number=self.current_volume
        )
        
        self.api_calls.append(call_cost)
        
        print(f"💸 OpenAI: {model} - {input_tokens}+{output_tokens} tokens = ${total_cost:.6f}")
        return total_cost
    
    def track_dalle_call(self, 
                        model: str,
                        size: str,
                        quantity: int = 1,
                        operation: str = "image_generation") -> float:
        """Track a DALL-E API call and calculate cost."""
        pricing = self.PRICING['dalle'].get(model, {})
        cost_per_image = pricing.get(size, 0.040)  # Default to DALL-E 3 pricing
        
        total_cost = cost_per_image * quantity
        
        call_cost = APICallCost(
            service="dalle",
            operation=f"{model}_{operation}",
            tokens_or_units=quantity,
            cost_per_unit=cost_per_image,
            total_cost=total_cost,
            timestamp=datetime.now().isoformat(),
            book_id=self.current_book_id,
            volume_number=self.current_volume
        )
        
        self.api_calls.append(call_cost)
        
        print(f"🎨 DALL-E: {model} {size} x{quantity} = ${total_cost:.6f}")
        return total_cost
    
    def track_aws_lambda_execution(self, 
                                  function_name: str,
                                  duration_ms: int,
                                  memory_mb: int) -> float:
        """Track AWS Lambda execution cost."""
        duration_seconds = duration_ms / 1000
        gb_seconds = (memory_mb / 1024) * duration_seconds
        
        # Lambda pricing: $0.0000166667 per GB-second
        total_cost = gb_seconds * self.PRICING['aws']['lambda']
        
        lambda_cost = AWSComputeCost(
            service="lambda",
            operation=function_name,
            duration_seconds=duration_seconds,
            compute_units=gb_seconds,
            cost_per_unit=self.PRICING['aws']['lambda'],
            total_cost=total_cost,
            timestamp=datetime.now().isoformat(),
            book_id=self.current_book_id,
            volume_number=self.current_volume
        )
        
        self.aws_costs.append(lambda_cost)
        
        print(f"🔧 Lambda: {function_name} - {duration_ms}ms @ {memory_mb}MB = ${total_cost:.6f}")
        return total_cost
    
    def track_fargate_execution(self, 
                               task_name: str,
                               vcpu: float,
                               memory_gb: float,
                               duration_seconds: float) -> float:
        """Track AWS Fargate execution cost."""
        # Convert to hours for pricing
        duration_hours = duration_seconds / 3600
        
        vcpu_cost = vcpu * duration_hours * self.PRICING['aws']['fargate']['vcpu']
        memory_cost = memory_gb * duration_hours * self.PRICING['aws']['fargate']['memory']
        total_cost = vcpu_cost + memory_cost
        
        fargate_cost = AWSComputeCost(
            service="fargate",
            operation=task_name,
            duration_seconds=duration_seconds,
            compute_units=vcpu * duration_hours + memory_gb * duration_hours,
            cost_per_unit=(vcpu_cost + memory_cost) / (vcpu * duration_hours + memory_gb * duration_hours),
            total_cost=total_cost,
            timestamp=datetime.now().isoformat(),
            book_id=self.current_book_id,
            volume_number=self.current_volume
        )
        
        self.aws_costs.append(fargate_cost)
        
        print(f"🐳 Fargate: {task_name} - {vcpu}vCPU, {memory_gb}GB for {duration_seconds}s = ${total_cost:.6f}")
        return total_cost
    
    def estimate_ecr_storage_cost(self, image_size_gb: float) -> float:
        """Estimate ECR storage cost for container images."""
        # ECR pricing: $0.10 per GB-month
        monthly_cost = image_size_gb * self.PRICING['aws']['ecr']
        daily_cost = monthly_cost / 30  # Approximate daily cost
        
        return daily_cost
    
    def finish_book_tracking(self) -> BookProductionCost:
        """Finish tracking and calculate final book production cost."""
        if not self.current_book_id:
            raise ValueError("No active book tracking session")
        
        # Separate costs by service
        openai_costs = [c for c in self.api_calls if c.service == "openai"]
        dalle_costs = [c for c in self.api_calls if c.service == "dalle"]
        gemini_costs = [c for c in self.api_calls if c.service == "gemini"]
        
        lambda_costs = [c for c in self.aws_costs if c.service == "lambda"]
        fargate_costs = [c for c in self.aws_costs if c.service == "fargate"]
        
        # Calculate totals
        total_api_cost = sum(c.total_cost for c in self.api_calls)
        total_aws_cost = sum(c.total_cost for c in self.aws_costs)
        total_production_cost = total_api_cost + total_aws_cost
        
        # Calculate metadata
        tokens_used = sum(c.tokens_or_units for c in openai_costs + gemini_costs)
        images_generated = sum(c.tokens_or_units for c in dalle_costs)
        compute_time_seconds = sum(c.duration_seconds for c in self.aws_costs)
        
        # Create final cost record
        book_cost = BookProductionCost(
            book_id=self.current_book_id,
            series_name=self.current_series,
            volume_number=self.current_volume,
            production_date=datetime.now().isoformat(),
            openai_costs=openai_costs,
            dalle_costs=dalle_costs,
            gemini_costs=gemini_costs,
            lambda_costs=lambda_costs,
            fargate_costs=fargate_costs,
            total_api_cost=total_api_cost,
            total_aws_cost=total_aws_cost,
            total_production_cost=total_production_cost,
            tokens_used=tokens_used,
            images_generated=images_generated,
            compute_time_seconds=compute_time_seconds
        )
        
        # Save cost data
        self._save_book_cost(book_cost)
        
        # Send to Sentry
        if SENTRY_AVAILABLE:
            capture_business_event("cost_tracking_completed",
                                 f"Book {self.current_book_id} cost: ${total_production_cost:.4f}",
                                 extra_data={
                                     "book_id": self.current_book_id,
                                     "total_cost": total_production_cost,
                                     "api_cost": total_api_cost,
                                     "aws_cost": total_aws_cost
                                 })
        
        print(f"📊 COST SUMMARY: {self.current_book_id}")
        print(f"   API Costs: ${total_api_cost:.4f}")
        print(f"   AWS Costs: ${total_aws_cost:.4f}")
        print(f"   TOTAL: ${total_production_cost:.4f}")
        
        # Reset tracking
        self.current_book_id = None
        self.current_volume = None
        self.api_calls.clear()
        self.aws_costs.clear()
        
        return book_cost
    
    def _save_book_cost(self, book_cost: BookProductionCost):
        """Save book cost data to file."""
        cost_file = self.costs_dir / f"{book_cost.book_id}_cost_breakdown.json"
        
        # Convert to JSON-serializable format
        cost_data = asdict(book_cost)
        
        with open(cost_file, 'w') as f:
            json.dump(cost_data, f, indent=2, default=str)
            
        print(f"💾 Cost data saved to {cost_file}")
    
    def get_series_cost_summary(self, series_name: str) -> Dict[str, Any]:
        """Get cost summary for an entire series."""
        series_costs = []
        total_cost = 0
        
        # Find all cost files for the series
        for cost_file in self.costs_dir.glob("*_cost_breakdown.json"):
            try:
                with open(cost_file, 'r') as f:
                    cost_data = json.load(f)
                
                if cost_data.get('series_name') == series_name:
                    series_costs.append(cost_data)
                    total_cost += cost_data.get('total_production_cost', 0)
                    
            except Exception as e:
                print(f"⚠️ Failed to load {cost_file}: {e}")
        
        # Sort by volume number
        series_costs.sort(key=lambda x: x.get('volume_number', 0))
        
        summary = {
            'series_name': series_name,
            'total_volumes': len(series_costs),
            'total_production_cost': total_cost,
            'average_cost_per_volume': total_cost / len(series_costs) if series_costs else 0,
            'volumes': series_costs,
            'cost_breakdown': {
                'total_api_cost': sum(c.get('total_api_cost', 0) for c in series_costs),
                'total_aws_cost': sum(c.get('total_aws_cost', 0) for c in series_costs),
                'total_tokens_used': sum(c.get('tokens_used', 0) for c in series_costs),
                'total_images_generated': sum(c.get('images_generated', 0) for c in series_costs),
            }
        }
        
        return summary
    
    def get_daily_cost_report(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Generate daily cost report."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        daily_costs = []
        total_cost = 0
        
        # Find all cost files for the date
        for cost_file in self.costs_dir.glob("*_cost_breakdown.json"):
            try:
                with open(cost_file, 'r') as f:
                    cost_data = json.load(f)
                
                production_date = cost_data.get('production_date', '')
                if production_date.startswith(date):
                    daily_costs.append(cost_data)
                    total_cost += cost_data.get('total_production_cost', 0)
                    
            except Exception as e:
                print(f"⚠️ Failed to load {cost_file}: {e}")
        
        report = {
            'date': date,
            'books_produced': len(daily_costs),
            'total_cost': total_cost,
            'average_cost_per_book': total_cost / len(daily_costs) if daily_costs else 0,
            'books': daily_costs
        }
        
        return report

# Global cost tracker instance
cost_tracker = CostTracker()

# Convenience functions
def start_tracking(book_id: str, series_name: str, volume_number: int):
    """Start cost tracking for a book."""
    return cost_tracker.start_book_tracking(book_id, series_name, volume_number)

def track_openai(model: str, input_tokens: int, output_tokens: int, operation: str = "completion"):
    """Track OpenAI API call."""
    return cost_tracker.track_openai_call(model, input_tokens, output_tokens, operation)

def track_dalle(model: str, size: str, quantity: int = 1, operation: str = "image_generation"):
    """Track DALL-E API call."""
    return cost_tracker.track_dalle_call(model, size, quantity, operation)

def track_lambda(function_name: str, duration_ms: int, memory_mb: int):
    """Track Lambda execution."""
    return cost_tracker.track_aws_lambda_execution(function_name, duration_ms, memory_mb)

def track_fargate(task_name: str, vcpu: float, memory_gb: float, duration_seconds: float):
    """Track Fargate execution."""
    return cost_tracker.track_fargate_execution(task_name, vcpu, memory_gb, duration_seconds)

def finish_tracking():
    """Finish tracking and get final cost."""
    return cost_tracker.finish_book_tracking()

def get_series_summary(series_name: str):
    """Get series cost summary."""
    return cost_tracker.get_series_cost_summary(series_name)

def get_daily_report(date: str = None):
    """Get daily cost report."""
    return cost_tracker.get_daily_cost_report(date)