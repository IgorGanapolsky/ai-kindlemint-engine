"""
Stripe Checkout Integration for KindleMint

Handles payment processing for puzzle book sales:
- Creates checkout sessions
- Handles webhooks
- Tracks successful payments
- Delivers digital products
"""

import os
import logging
from typing import Dict, Optional, Any
import stripe
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class StripeCheckout:
    """Manage Stripe checkout and payment processing"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Stripe checkout
        
        Args:
            api_key: Stripe API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv('STRIPE_API_KEY')
        if self.api_key:
            stripe.api_key = self.api_key
            logger.info("💳 Stripe checkout initialized")
        else:
            logger.warning("⚠️ No Stripe API key found - payments disabled")
    
    def create_checkout_session(
        self,
        product_name: str,
        price_cents: int,
        customer_email: Optional[str] = None,
        success_url: str = "https://example.com/success",
        cancel_url: str = "https://example.com/cancel",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session
        
        Args:
            product_name: Name of the product
            price_cents: Price in cents (e.g., 899 for $8.99)
            customer_email: Pre-fill customer email
            success_url: Redirect URL after successful payment
            cancel_url: Redirect URL if customer cancels
            metadata: Additional metadata to track
            
        Returns:
            Dict with session details
        """
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'Stripe not configured'
                }
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                            'description': 'Instant digital download - PDF format',
                        },
                        'unit_amount': price_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                customer_email=customer_email,
                metadata=metadata or {},
                # Enable digital product delivery
                shipping_address_collection=None,
                # Collect billing address for tax purposes
                billing_address_collection='required',
            )
            
            logger.info(f"✅ Created checkout session: {session.id}")
            
            return {
                'success': True,
                'session_id': session.id,
                'checkout_url': session.url,
                'amount': price_cents / 100,
                'product': product_name
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"❌ Stripe error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"❌ Failed to create checkout session: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_product_links(self) -> Dict[str, str]:
        """
        Create checkout links for all products
        
        Returns:
            Dict of product names to checkout URLs
        """
        products = {
            'Large Print Sudoku Masters Volume 1': {
                'price': 899,  # $8.99
                'success_url': 'https://kindlemint.com/success',
                'cancel_url': 'https://kindlemint.com/puzzles'
            },
            'Large Print Sudoku Masters Bundle (5 Volumes)': {
                'price': 3499,  # $34.99
                'success_url': 'https://kindlemint.com/success',
                'cancel_url': 'https://kindlemint.com/puzzles'
            },
            'Monthly Puzzle Subscription': {
                'price': 499,  # $4.99/month
                'success_url': 'https://kindlemint.com/success',
                'cancel_url': 'https://kindlemint.com/puzzles'
            }
        }
        
        links = {}
        for product_name, details in products.items():
            result = self.create_checkout_session(
                product_name=product_name,
                price_cents=details['price'],
                success_url=details['success_url'],
                cancel_url=details['cancel_url']
            )
            
            if result['success']:
                links[product_name] = result['checkout_url']
            else:
                links[product_name] = None
                
        return links
    
    def handle_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            Dict with processing result
        """
        try:
            webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
            if not webhook_secret:
                logger.warning("No webhook secret configured")
                return {'success': False, 'error': 'Webhook not configured'}
            
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                return self._handle_successful_payment(session)
                
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                return self._handle_failed_payment(payment_intent)
                
            else:
                logger.info(f"Unhandled event type: {event['type']}")
                
            return {'success': True, 'event': event['type']}
            
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return {'success': False, 'error': 'Invalid payload'}
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return {'success': False, 'error': 'Invalid signature'}
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_successful_payment(self, session: Dict) -> Dict[str, Any]:
        """Handle successful payment"""
        try:
            customer_email = session.get('customer_email') or session.get('customer_details', {}).get('email')
            amount = session.get('amount_total', 0) / 100
            
            # Track conversion
            from ..analytics import ConversionTracker
            tracker = ConversionTracker()
            
            # Get product from metadata or line items
            product = session.get('metadata', {}).get('product_name', 'Unknown Product')
            
            # Track the purchase
            tracker.track_purchase(
                email=customer_email,
                product=product,
                amount=amount
            )
            
            # Send product delivery email
            from ..email import EmailAutomation
            automation = EmailAutomation()
            
            # Record conversion in email system
            automation.record_conversion(
                email=customer_email,
                product=product,
                amount=amount
            )
            
            # TODO: Send product delivery email with download link
            # This would be implemented based on your delivery system
            
            logger.info(f"✅ Payment processed: {customer_email} - ${amount}")
            
            return {
                'success': True,
                'customer_email': customer_email,
                'amount': amount,
                'product': product
            }
            
        except Exception as e:
            logger.error(f"Failed to handle payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_failed_payment(self, payment_intent: Dict) -> Dict[str, Any]:
        """Handle failed payment"""
        logger.warning(f"Payment failed: {payment_intent.get('id')}")
        
        # Could send a follow-up email to recover the sale
        return {
            'success': True,
            'payment_failed': True,
            'intent_id': payment_intent.get('id')
        }
    
    def create_payment_link(
        self,
        product_name: str,
        price_cents: int,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a reusable payment link
        
        Args:
            product_name: Name of the product
            price_cents: Price in cents
            metadata: Additional metadata
            
        Returns:
            Dict with payment link details
        """
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'Stripe not configured'
                }
            
            # First create a product
            product = stripe.Product.create(
                name=product_name,
                description='Digital puzzle book - instant download'
            )
            
            # Create a price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=price_cents,
                currency='usd'
            )
            
            # Create payment link
            payment_link = stripe.PaymentLink.create(
                line_items=[{
                    'price': price.id,
                    'quantity': 1
                }],
                metadata=metadata or {},
                after_completion={
                    'type': 'hosted_confirmation',
                    'hosted_confirmation': {
                        'custom_message': 'Thank you! Check your email for your download link.'
                    }
                }
            )
            
            logger.info(f"✅ Created payment link: {payment_link.url}")
            
            return {
                'success': True,
                'payment_link': payment_link.url,
                'product_id': product.id,
                'price_id': price.id
            }
            
        except Exception as e:
            logger.error(f"Failed to create payment link: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def generate_checkout_links():
    """Generate and save checkout links for all products"""
    checkout = StripeCheckout()
    
    products = [
        {
            'name': 'Large Print Sudoku Masters Volume 1',
            'price': 899,
            'metadata': {'sku': 'LPSM-001'}
        },
        {
            'name': 'Large Print Sudoku Masters Bundle (5 Volumes)',
            'price': 3499,
            'metadata': {'sku': 'LPSM-BUNDLE'}
        }
    ]
    
    links = {}
    for product in products:
        result = checkout.create_payment_link(
            product_name=product['name'],
            price_cents=product['price'],
            metadata=product['metadata']
        )
        
        if result['success']:
            links[product['name']] = result['payment_link']
            print(f"✅ {product['name']}: {result['payment_link']}")
        else:
            print(f"❌ Failed to create link for {product['name']}: {result['error']}")
    
    # Save links to file
    links_file = Path('data/stripe_payment_links.json')
    links_file.parent.mkdir(exist_ok=True)
    
    with open(links_file, 'w') as f:
        json.dump(links, f, indent=2)
    
    print(f"\n💾 Payment links saved to: {links_file}")
    return links


def main():
    """Test Stripe checkout"""
    print("🧪 Testing Stripe Checkout Integration")
    print("=" * 60)
    
    # Initialize checkout
    checkout = StripeCheckout()
    
    if not checkout.api_key:
        print("⚠️  No Stripe API key found!")
        print("Set STRIPE_API_KEY environment variable to test")
        return
    
    # Create test checkout session
    result = checkout.create_checkout_session(
        product_name="Test - Large Print Sudoku Masters Vol 1",
        price_cents=899,
        customer_email="test@example.com",
        metadata={'test': True}
    )
    
    if result['success']:
        print("✅ Checkout session created!")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Checkout URL: {result['checkout_url']}")
        print("\n🔗 Open this URL to test checkout:")
        print(f"   {result['checkout_url']}")
    else:
        print(f"❌ Failed: {result['error']}")


if __name__ == "__main__":
    main()