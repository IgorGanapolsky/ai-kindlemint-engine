#!/usr/bin/env python3
"""
Check Stripe Balance and Payouts
"""

import os
import stripe
from datetime import datetime

def check_stripe_balance():
    """Check actual Stripe balance and payout information"""
    
    # Load environment variables
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    if not stripe.api_key:
        print("❌ Stripe API key not found")
        return
    
    try:
        # Get current balance
        balance = stripe.Balance.retrieve()
        
        print("💰 STRIPE BALANCE & PAYOUTS")
        print("=" * 50)
        
        # Available balance (ready to transfer)
        available_amount = 0
        if balance.available:
            available_amount = balance.available[0].amount / 100
            print(f"💵 Available Balance: ${available_amount:.2f}")
        else:
            print("💵 Available Balance: $0.00")
        
        # Pending balance (not yet available)
        pending_amount = 0
        if balance.pending:
            pending_amount = balance.pending[0].amount / 100
            print(f"⏳ Pending Balance: ${pending_amount:.2f}")
        else:
            print("⏳ Pending Balance: $0.00")
        
        total_balance = available_amount + pending_amount
        print(f"📊 Total Balance: ${total_balance:.2f}")
        
        # Check recent payouts
        print(f"\n📤 RECENT PAYOUTS:")
        payouts = stripe.Payout.list(limit=10)
        
        if payouts.data:
            for payout in payouts.data:
                amount = payout.amount / 100
                status = payout.status
                created = datetime.fromtimestamp(payout.created)
                print(f"   ${amount:.2f} - {status} - {created.strftime('%Y-%m-%d')}")
        else:
            print("   No payouts found")
        
        # Check account details
        print(f"\n🏦 ACCOUNT INFORMATION:")
        account = stripe.Account.retrieve()
        print(f"   Account ID: {account.id}")
        print(f"   Country: {account.country}")
        print(f"   Currency: {account.default_currency}")
        
        # Payout schedule
        print(f"\n📅 PAYOUT SCHEDULE:")
        if hasattr(account, 'payouts_enabled') and account.payouts_enabled:
            print(f"   ✅ Payouts enabled")
            if hasattr(account, 'payout_schedule'):
                print(f"   Schedule: {account.payout_schedule.interval}")
        else:
            print(f"   ❌ Payouts not enabled")
        
        # How to get your money
        print(f"\n💡 HOW TO GET YOUR MONEY:")
        if available_amount > 0:
            print(f"   ✅ You have ${available_amount:.2f} available to transfer")
            print(f"   🌐 Go to: https://dashboard.stripe.com/payouts")
            print(f"   📱 Or use Stripe mobile app")
        elif total_balance > 0:
            print(f"   ⏳ You have ${total_balance:.2f} pending")
            print(f"   📅 Payouts typically happen every 2-7 days")
            print(f"   🌐 Check: https://dashboard.stripe.com/balance")
        else:
            print(f"   💰 No balance available")
            print(f"   📈 Focus on generating new sales")
        
        # Revenue vs Balance explanation
        print(f"\n🤔 REVENUE vs BALANCE EXPLANATION:")
        print(f"   💳 Revenue: Money customers paid")
        print(f"   💰 Balance: Money available to you")
        print(f"   ⏳ Pending: Money processing (2-7 days)")
        print(f"   📤 Payouts: Money transferred to your bank")
        
    except Exception as e:
        print(f"❌ Error checking balance: {e}")

if __name__ == "__main__":
    check_stripe_balance() 