#!/usr/bin/env python3
"""
Revenue Monitor for Sudoku Business
"""
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import stripe

load_dotenv()
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def check_revenue_data():
    """Check current revenue data"""
    try:
        if os.path.exists('revenue_data.json'):
            with open('revenue_data.json', 'r') as f:
                data = json.load(f)
            return data
        else:
            return {"sales_count": 0, "channels": {}, "last_sale": None}
    except Exception as e:
        print(f"Error reading revenue data: {e}")
        return {"sales_count": 0, "channels": {}, "last_sale": None}

def check_stripe_sales():
    """Check actual Stripe sales for Sudoku business"""
    try:
        # Get recent payments
        payments = stripe.PaymentIntent.list(limit=20)
        sudoku_sales = []
        
        for payment in payments.data:
            # Check if it's a Sudoku-related sale
            if (payment.metadata and 
                payment.metadata.get('business') == 'sudoku-seniors'):
                sudoku_sales.append({
                    'amount': payment.amount / 100,
                    'status': payment.status,
                    'created': datetime.fromtimestamp(payment.created).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return sudoku_sales
    except Exception as e:
        print(f"Error checking Stripe: {e}")
        return []

def display_status():
    """Display current business status"""
    print("\n" + "="*60)
    print(f"📊 SUDOKU BUSINESS STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check revenue data
    revenue_data = check_revenue_data()
    print(f"\n💰 Revenue Data:")
    print(f"   Sales Count: {revenue_data.get('sales_count', 0)}")
    print(f"   Last Sale: {revenue_data.get('last_sale', 'None')}")
    
    if revenue_data.get('channels'):
        print(f"   Channel Activity:")
        for channel, count in revenue_data['channels'].items():
            print(f"     - {channel}: {count} activities")
    
    # Check actual Stripe sales
    stripe_sales = check_stripe_sales()
    print(f"\n💳 Actual Stripe Sales (Sudoku Business):")
    if stripe_sales:
        for sale in stripe_sales:
            print(f"   - ${sale['amount']:.2f} ({sale['status']}) - {sale['created']}")
    else:
        print("   No Sudoku sales found in Stripe")
    
    # Check if revenue generator is running
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'working_revenue_generator'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n✅ Revenue Generator: RUNNING (PID: {result.stdout.strip()})")
        else:
            print(f"\n❌ Revenue Generator: NOT RUNNING")
    except Exception as e:
        print(f"\n⚠️ Could not check revenue generator status: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    display_status() 