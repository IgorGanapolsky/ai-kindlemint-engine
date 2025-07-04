#!/usr/bin/env python3
"""
Monetization Setup for Kindlemint MCP Agent
Integrates payment processing and usage tracking
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class Usage:
    """Track usage for billing"""
    user_id: str
    books_generated: int
    last_reset: str
    plan: str = "free"  # free, basic, pro
    
    def to_dict(self):
        return asdict(self)

class MonetizationManager:
    """Handles payments, usage tracking, and plan limits"""
    
    def __init__(self, data_dir: str = "data/monetization"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.data_dir / "usage.json"
        
        # Plan limits
        self.plans = {
            "free": {"books_per_month": 2, "price": 0},
            "basic": {"books_per_month": 20, "price": 19},
            "pro": {"books_per_month": 100, "price": 49}
        }
        
        self.load_usage()
    
    def load_usage(self):
        """Load usage data from disk"""
        if self.usage_file.exists():
            with open(self.usage_file, 'r') as f:
                data = json.load(f)
                self.users = {
                    user_id: Usage(**user_data) 
                    for user_id, user_data in data.items()
                }
        else:
            self.users = {}
    
    def save_usage(self):
        """Save usage data to disk"""
        data = {
            user_id: user.to_dict() 
            for user_id, user in self.users.items()
        }
        with open(self.usage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_usage(self, user_id: str) -> Usage:
        """Get or create user usage record"""
        if user_id not in self.users:
            self.users[user_id] = Usage(
                user_id=user_id,
                books_generated=0,
                last_reset=datetime.now().isoformat(),
                plan="free"
            )
        
        user = self.users[user_id]
        
        # Reset monthly usage if needed
        last_reset = datetime.fromisoformat(user.last_reset)
        if datetime.now() - last_reset > timedelta(days=30):
            user.books_generated = 0
            user.last_reset = datetime.now().isoformat()
            self.save_usage()
        
        return user
    
    def can_generate_book(self, user_id: str) -> tuple[bool, str]:
        """Check if user can generate another book"""
        user = self.get_user_usage(user_id)
        plan_limits = self.plans[user.plan]
        
        if user.books_generated >= plan_limits["books_per_month"]:
            return False, f"Monthly limit reached ({plan_limits['books_per_month']} books). Upgrade your plan!"
        
        return True, "OK"
    
    def record_book_generation(self, user_id: str) -> None:
        """Record that a user generated a book"""
        user = self.get_user_usage(user_id)
        user.books_generated += 1
        self.save_usage()
    
    def upgrade_user_plan(self, user_id: str, new_plan: str, payment_confirmed: bool = False) -> bool:
        """Upgrade user to new plan (with payment verification)"""
        if new_plan not in self.plans:
            return False
        
        if not payment_confirmed:
            # In real implementation, verify payment with Stripe/Gumroad
            return False
        
        user = self.get_user_usage(user_id)
        user.plan = new_plan
        self.save_usage()
        return True
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """Get pricing information for display"""
        return {
            "plans": self.plans,
            "currency": "USD",
            "billing_period": "monthly",
            "payment_methods": ["stripe", "gumroad", "paypal"]
        }

def create_gumroad_product_links():
    """Generate Gumroad product setup instructions"""
    return {
        "basic_plan": {
            "title": "Kindlemint AI Agent - Basic Plan", 
            "price": "$19/month",
            "description": "Generate up to 20 puzzle books per month with AI",
            "url": "https://gumroad.com/l/kindlemint-basic",
            "features": [
                "20 books per month",
                "Sudoku & Crossword generation", 
                "Large print options",
                "KDP-ready PDFs",
                "Email support"
            ]
        },
        "pro_plan": {
            "title": "Kindlemint AI Agent - Pro Plan",
            "price": "$49/month", 
            "description": "Generate up to 100 puzzle books per month with AI",
            "url": "https://gumroad.com/l/kindlemint-pro",
            "features": [
                "100 books per month",
                "All puzzle types",
                "Custom themes & branding", 
                "Priority generation",
                "Phone support",
                "Lead magnet creation"
            ]
        }
    }

def create_stripe_setup():
    """Stripe integration setup (placeholder)"""
    return {
        "stripe_public_key": "pk_test_...",  # Replace with real key
        "stripe_webhook_secret": "whsec_...",  # Replace with real secret
        "basic_price_id": "price_...",  # Create in Stripe dashboard
        "pro_price_id": "price_...",    # Create in Stripe dashboard
    }

def setup_monetization():
    """Initial setup for monetization"""
    print("💰 Setting up Kindlemint monetization...")
    
    # Create monetization manager
    manager = MonetizationManager()
    
    # Create sample user for testing
    test_user = "test_user_123"
    usage = manager.get_user_usage(test_user)
    print(f"📊 Test user setup: {usage}")
    
    # Display pricing info
    pricing = manager.get_pricing_info()
    print(f"💳 Pricing plans: {json.dumps(pricing, indent=2)}")
    
    # Generate product links
    gumroad_links = create_gumroad_product_links()
    print(f"🔗 Gumroad setup: {json.dumps(gumroad_links, indent=2)}")
    
    # Save setup info
    setup_file = Path("data/monetization/setup_info.json")
    setup_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(setup_file, 'w') as f:
        json.dump({
            "pricing": pricing,
            "gumroad_products": gumroad_links,
            "stripe_config": create_stripe_setup(),
            "setup_date": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"✅ Monetization setup complete! Config saved to {setup_file}")
    
    return manager

if __name__ == "__main__":
    setup_monetization()