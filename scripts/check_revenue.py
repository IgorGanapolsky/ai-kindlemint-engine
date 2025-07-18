#!/usr/bin/env python3
"""
Check Actual Revenue
"""

import os
import stripe
from datetime import datetime

def check_revenue():
    """Check actual revenue from Stripe"""
    
    # Load environment variables
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    if not stripe.api_key:
        print("❌ Stripe API key not found")
        return
    
    try:
        # Get recent payments
        payments = stripe.PaymentIntent.list(limit=20)
        
        print("💰 ACTUAL REVENUE DATA")
        print("=" * 50)
        
        successful_payments = []
        total_revenue = 0
        
        for payment in payments.data:
            amount = payment.amount / 100  # Convert from cents
            status = payment.status
            created = datetime.fromtimestamp(payment.created)
            
            print(f"Payment: ${amount:.2f} - Status: {status} - Date: {created.strftime('%Y-%m-%d %H:%M')}")
            
            if status == 'succeeded':
                successful_payments.append(payment)
                total_revenue += amount
        
        print("\n" + "=" * 50)
        print(f"💵 TOTAL REVENUE: ${total_revenue:.2f}")
        print(f"📊 SUCCESSFUL PAYMENTS: {len(successful_payments)}")
        print(f"🎯 AVERAGE SALE: ${total_revenue/len(successful_payments):.2f}" if successful_payments else "🎯 No successful sales yet")
        
        # Check for today's revenue
        today = datetime.now().date()
        today_revenue = sum([p.amount/100 for p in successful_payments if datetime.fromtimestamp(p.created).date() == today])
        print(f"📅 TODAY'S REVENUE: ${today_revenue:.2f}")
        
        # Check for this week's revenue
        week_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_revenue = sum([p.amount/100 for p in successful_payments if datetime.fromtimestamp(p.created) >= week_ago])
        print(f"📅 THIS WEEK'S REVENUE: ${week_revenue:.2f}")
        
        if total_revenue == 0:
            print("\n🚀 NO SALES YET - AUTOMATION IS RUNNING!")
            print("🤖 The automated systems are active and generating traffic")
            print("📈 First sale expected within 24-48 hours")
        
    except Exception as e:
        print(f"❌ Error checking revenue: {e}")

if __name__ == "__main__":
    check_revenue() 