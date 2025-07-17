#!/usr/bin/env python3
"""
Launch Stripe Monetization System
Secure implementation to generate first dollar
"""

import os
import sys
import json
import stripe
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class StripeMonetizationLauncher:
    def __init__(self):
        self.stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
        self.product_id = os.getenv('STRIPE_PRODUCT_ID')
        self.price_id = os.getenv('STRIPE_ONE_TIME_PRICE_ID')  # Use the one-time price
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if not all([self.stripe_publishable_key, self.stripe_secret_key, self.product_id, self.price_id]):
            print("❌ Missing Stripe configuration")
            sys.exit(1)
        
        # Initialize Stripe
        stripe.api_key = self.stripe_secret_key
        
    def create_checkout_session(self, product_name: str = "Large Print Sudoku Puzzles") -> str:
        """Create a Stripe checkout session"""
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': self.price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://igorganapolsky.github.io/ai-kindlemint-engine/docs/success.html',
                cancel_url='https://igorganapolsky.github.io/ai-kindlemint-engine/',
                metadata={
                    'product_name': product_name,
                    'launch_time': datetime.now().isoformat()
                }
            )
            return checkout_session.url
        except Exception as e:
            print(f"❌ Failed to create checkout session: {e}")
            return None
    
    def generate_landing_page(self) -> str:
        """Generate a landing page with Stripe integration"""
        landing_page = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Large Print Sudoku Puzzles - Brain Training for Seniors</title>
    <script src="https://js.stripe.com/v3/"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .container {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        .cta-button {{
            background: #28a745;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            margin: 20px 0;
            transition: all 0.3s ease;
        }}
        .cta-button:hover {{
            background: #218838;
            transform: translateY(-2px);
        }}
        .benefits {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .benefit {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧩 Large Print Sudoku Puzzles</h1>
        <h2>Brain Training Specifically Designed for Seniors</h2>
        
        <div class="benefits">
            <div class="benefit">
                <h3>👁️ Large Print</h3>
                <p>Easy-to-read numbers and clear grids</p>
            </div>
            <div class="benefit">
                <h3>🧠 Brain Health</h3>
                <p>Improve memory and cognitive function</p>
            </div>
            <div class="benefit">
                <h3>🎯 Perfect Difficulty</h3>
                <p>Challenging but not frustrating</p>
            </div>
        </div>
        
        <p><strong>Special Launch Price: $2.99</strong></p>
        <p>Get instant access to 100 large print Sudoku puzzles designed specifically for seniors. Improve your brain health while having fun!</p>
        
        <button class="cta-button" onclick="redirectToCheckout()">
            🚀 Get My Puzzles Now - $2.99
        </button>
        
        <p><small>✅ Instant download • ✅ 30-day money-back guarantee • ✅ Secure payment</small></p>
    </div>

    <script>
        function redirectToCheckout() {{
            // Create checkout session
            fetch('/api/create-checkout-session', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    product_name: 'Large Print Sudoku Puzzles'
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.url) {{
                    window.location.href = data.url;
                }} else {{
                    alert('Error creating checkout session');
                }}
            }})
            .catch(error => {{
                console.error('Error:', error);
                alert('Error creating checkout session');
            }});
        }}
    </script>
</body>
</html>
"""
        return landing_page
    
    def create_api_endpoint(self) -> str:
        """Create the API endpoint for checkout sessions"""
        api_code = f"""
from flask import Flask, request, jsonify
import stripe
import os

app = Flask(__name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
price_id = os.getenv('STRIPE_ONE_TIME_PRICE_ID')

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{{
                'price': price_id,
                'quantity': 1,
            }}],
            mode='payment',
            success_url='https://igorganapolsky.github.io/ai-kindlemint-engine/docs/success.html',
            cancel_url='https://igorganapolsky.github.io/ai-kindlemint-engine/',
        )
        return jsonify({{'url': checkout_session.url}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 400

@app.route('/api/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(f"Payment successful: {{session.id}}")
        # Here you would deliver the product
        
    return jsonify({{'status': 'success'}})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""
        return api_code
    
    def launch_monetization(self):
        """Launch the complete monetization system"""
        print("🚀 Launching Stripe Monetization System...")
        print("=" * 60)
        
        # 1. Create landing page
        print("📄 Creating landing page...")
        landing_page = self.generate_landing_page()
        with open('docs/landing_page.html', 'w') as f:
            f.write(landing_page)
        print("✅ Landing page created: docs/landing_page.html")
        
        # 2. Create API endpoint
        print("🔌 Creating API endpoint...")
        api_code = self.create_api_endpoint()
        with open('api/stripe_checkout.py', 'w') as f:
            f.write(api_code)
        print("✅ API endpoint created: api/stripe_checkout.py")
        
        # 3. Test checkout session
        print("🧪 Testing checkout session...")
        checkout_url = self.create_checkout_session()
        if checkout_url:
            print(f"✅ Checkout session created: {checkout_url}")
        else:
            print("❌ Failed to create checkout session")
            return
        
        # 4. Create deployment script
        print("🚀 Creating deployment script...")
        deploy_script = f"""#!/bin/bash
# Deploy Stripe Monetization System

echo "🚀 Deploying Stripe Monetization System..."

# Install dependencies
pip install flask stripe

# Start the API server
cd api
python stripe_checkout.py &

echo "✅ API server started on http://localhost:5000"
echo "🌐 Landing page available at: docs/landing_page.html"
echo "💳 Checkout URL: {checkout_url}"
echo ""
echo "🎯 Your monetization system is LIVE!"
echo "💰 First dollar incoming..."
"""
        
        with open('deploy_stripe_monetization.sh', 'w') as f:
            f.write(deploy_script)
        os.chmod('deploy_stripe_monetization.sh', 0o755)
        print("✅ Deployment script created: deploy_stripe_monetization.sh")
        
        # 5. Create success page
        print("✅ Creating success page...")
        success_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Payment Successful!</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .success { color: #28a745; font-size: 24px; }
    </style>
</head>
<body>
    <div class="success">
        <h1>🎉 Payment Successful!</h1>
        <p>Thank you for your purchase!</p>
        <p>Your Large Print Sudoku Puzzles are being prepared for download...</p>
        <p>You will receive an email with download instructions shortly.</p>
    </div>
</body>
</html>
"""
        with open('docs/success.html', 'w') as f:
            f.write(success_page)
        print("✅ Success page created: docs/success.html")
        
        print("=" * 60)
        print("🎉 STRIPE MONETIZATION SYSTEM LAUNCHED!")
        print("=" * 60)
        print("📄 Landing Page: docs/landing_page.html")
        print("🔌 API Endpoint: api/stripe_checkout.py")
        print("🚀 Deploy Script: ./deploy_stripe_monetization.sh")
        print("💳 Checkout URL: " + checkout_url)
        print("")
        print("💰 TO MAKE YOUR FIRST DOLLAR:")
        print("1. Run: ./deploy_stripe_monetization.sh")
        print("2. Share the landing page with potential customers")
        print("3. Monitor payments in your Stripe dashboard")
        print("")
        print("🎯 Your first $2.99 is just one customer away!")

def main():
    launcher = StripeMonetizationLauncher()
    launcher.launch_monetization()

if __name__ == "__main__":
    main() 