#!/usr/bin/env python3
"""
Create Stripe Price for One-Time Payment
"""

import os
import stripe
from datetime import datetime

def create_one_time_price():
    """Create a one-time price for the Sudoku puzzles"""
    
    # Load environment variables
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    product_id = os.getenv('STRIPE_PRODUCT_ID')
    
    if not stripe.api_key or not product_id:
        print("❌ Missing Stripe configuration")
        return
    
    try:
        # Create a one-time price
        price = stripe.Price.create(
            product=product_id,
            unit_amount=299,  # $2.99 in cents
            currency='usd',
            recurring=None  # This makes it a one-time payment
        )
        
        print("✅ One-time price created successfully!")
        print(f"Price ID: {price.id}")
        print(f"Amount: ${price.unit_amount/100}")
        print(f"Currency: {price.currency}")
        print(f"Product: {price.product}")
        
        # Update .env file with new price ID
        with open('.env', 'a') as f:
            f.write(f'\nSTRIPE_ONE_TIME_PRICE_ID={price.id}')
        
        print(f"\n📝 Added to .env: STRIPE_ONE_TIME_PRICE_ID={price.id}")
        print("🔄 Please update your Stripe configuration to use this new price ID")
        
        return price.id
        
    except Exception as e:
        print(f"❌ Failed to create price: {e}")
        return None

if __name__ == "__main__":
    create_one_time_price() 