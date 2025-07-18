#!/usr/bin/env python3
import os
import stripe
from datetime import datetime
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

if not stripe.api_key:
    print("❌ No Stripe API key found")
    exit(1)

print("🔍 Checking Stripe payment data...")
print("=" * 50)

# Get recent payments
try:
    payments = stripe.PaymentIntent.list(limit=20)
    print(f"📊 Found {len(payments.data)} recent payments")
    print()
    
    for payment in payments.data:
        created_date = datetime.fromtimestamp(payment.created)
        amount = payment.amount / 100
        print(f"💰 Payment: ${amount:.2f}")
        print(f"   Date: {created_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Status: {payment.status}")
        if hasattr(payment, 'description') and payment.description:
            print(f"   Description: {payment.description}")
        print()
        
except Exception as e:
    print(f"❌ Error fetching payments: {e}")

# Get account balance
try:
    balance = stripe.Balance.retrieve()
    print("💰 Account Balance:")
    print(f"   Available: ${balance.available[0].amount/100:.2f}")
    print(f"   Pending: ${balance.pending[0].amount/100:.2f}")
    print()
except Exception as e:
    print(f"❌ Error fetching balance: {e}")

# Get products and prices
try:
    products = stripe.Product.list(limit=10)
    print("📦 Products in account:")
    for product in products.data:
        print(f"   - {product.name} (ID: {product.id})")
        if product.description:
            print(f"     Description: {product.description}")
    print()
except Exception as e:
    print(f"❌ Error fetching products: {e}")

print("=" * 50)
print("✅ Stripe data check complete") 