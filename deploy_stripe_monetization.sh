#!/bin/bash
# Deploy Stripe Monetization System

echo "🚀 Deploying Stripe Monetization System..."

# Install dependencies
pip install flask stripe

# Start the API server
cd api
python stripe_checkout.py &

echo "✅ API server started on http://localhost:5000"
echo "🌐 Landing page available at: docs/landing_page.html"
echo "💳 Checkout URL: https://checkout.stripe.com/c/pay/cs_live_a1IH5vCC4STNf0hMJgNScGyw37thqsNLqgdHSAdxfP4VkE2jIlQQBb6kuW#fidkdWxOYHwnPyd1blppbHNgWjA0V0tmTzRCQkd1YTA3NVRcMEwwZ2dCcVNdS09BVklzTmxycERMYW9Mbn1JX2IyQmpXMGdQcH1gPUNLM3FPNW5rU0JLPUg2SkRWZHZnNkF8RHxfaTNhQVRcNTV%2FPGpzf25ofScpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"
echo ""
echo "🎯 Your monetization system is LIVE!"
echo "💰 First dollar incoming..."
