#!/usr/bin/env python3
"""
Check Payment Details
"""

import os
import stripe
from datetime import datetime

def check_payment_details():
    """Check detailed payment information"""
    
    # Load environment variables
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    if not stripe.api_key:
        print("❌ Stripe API key not found")
        return
    
    try:
        # Get all payments
        payments = stripe.PaymentIntent.list(limit=20)
        
        print("💰 DETAILED PAYMENT ANALYSIS")
        print("=" * 60)
        
        total_revenue = 0
        total_fees = 0
        successful_payments = []
        
        for payment in payments.data:
            amount = payment.amount / 100
            status = payment.status
            created = datetime.fromtimestamp(payment.created)
            
            print(f"\n💳 Payment: ${amount:.2f}")
            print(f"   Status: {status}")
            print(f"   Date: {created.strftime('%Y-%m-%d %H:%M')}")
            print(f"   ID: {payment.id}")
            
            if status == 'succeeded':
                successful_payments.append(payment)
                total_revenue += amount
                
                # Calculate fees (approximately 2.9% + 30 cents)
                fee = (amount * 0.029) + 0.30
                total_fees += fee
                net_amount = amount - fee
                
                print(f"   💰 Gross: ${amount:.2f}")
                print(f"   💸 Fees: ${fee:.2f}")
                print(f"   💵 Net: ${net_amount:.2f}")
            else:
                print(f"   ❌ Payment failed or pending")
        
        print(f"\n" + "=" * 60)
        print(f"📊 SUMMARY:")
        print(f"   Total Revenue: ${total_revenue:.2f}")
        print(f"   Total Fees: ${total_fees:.2f}")
        print(f"   Net Revenue: ${total_revenue - total_fees:.2f}")
        print(f"   Successful Payments: {len(successful_payments)}")
        
        # Check what happened to the money
        print(f"\n🤔 WHERE DID THE MONEY GO?")
        print(f"   💳 Customers paid: ${total_revenue:.2f}")
        print(f"   💸 Stripe fees: ${total_fees:.2f}")
        print(f"   💰 Net to you: ${total_revenue - total_fees:.2f}")
        
        # Check if money was already paid out
        payouts = stripe.Payout.list(limit=10)
        total_paid_out = 0
        
        for payout in payouts.data:
            if payout.status == 'paid':
                total_paid_out += payout.amount / 100
        
        print(f"   📤 Already paid out: ${total_paid_out:.2f}")
        
        # Current situation
        net_revenue = total_revenue - total_fees
        money_status = net_revenue - total_paid_out
        
        print(f"\n💡 CURRENT SITUATION:")
        if money_status > 0:
            print(f"   ✅ You have ${money_status:.2f} coming to you")
            print(f"   📅 Next payout should include this amount")
        elif money_status < 0:
            print(f"   ⚠️ Account has negative balance: ${abs(money_status):.2f}")
            print(f"   🔍 This might be due to refunds or chargebacks")
        else:
            print(f"   💰 All money has been paid out")
        
        # Action items
        print(f"\n🎯 WHAT TO DO:")
        if money_status > 0:
            print(f"   ✅ Wait for next payout (2-7 days)")
            print(f"   🌐 Check: https://dashboard.stripe.com/payouts")
        elif money_status < 0:
            print(f"   ⚠️ Contact Stripe support about negative balance")
            print(f"   📧 Email: support@stripe.com")
        else:
            print(f"   💰 All money has been transferred to your bank")
            print(f"   📈 Focus on generating new sales")
        
    except Exception as e:
        print(f"❌ Error checking payment details: {e}")

if __name__ == "__main__":
    check_payment_details() 