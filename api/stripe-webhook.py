"""
Stripe Webhook Handler for Vercel

Processes Stripe webhook events:
- Payment successful: Deliver product
- Payment failed: Send recovery email
- Subscription created: Start recurring delivery
"""

import json
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kindlemint.payments import StripeCheckout


def handler(request):
    """
    Handle Stripe webhook events
    
    Expected headers:
    - stripe-signature: Webhook signature for verification
    """
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Only accept POST
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Get signature from headers
        signature = request.headers.get('stripe-signature')
        if not signature:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing stripe-signature header'})
            }
        
        # Initialize Stripe checkout handler
        checkout = StripeCheckout()
        
        # Handle the webhook
        result = checkout.handle_webhook(
            payload=request.body,
            signature=signature
        )
        
        if result['success']:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'message': 'Webhook processed successfully'
                })
            }
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': result.get('error', 'Webhook processing failed')
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }