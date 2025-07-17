#!/usr/bin/env python3
"""
Generate Stripe Payment Links

This script generates reusable payment links for all products
that can be included in emails and on the website.

Usage:
    python scripts/generate_payment_links.py
"""

import os
import sys
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kindlemint.payments import StripeCheckout


def generate_all_payment_links():
    """Generate payment links for all products"""
    print("💳 Generating Stripe Payment Links")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv('STRIPE_API_KEY'):
        print("❌ Error: STRIPE_API_KEY environment variable not set")
        print("\nTo set it:")
        print("export STRIPE_API_KEY='sk_test_your_stripe_key_here'")
        return
    
    # Initialize Stripe
    checkout = StripeCheckout()
    
    # Define all products
    products = [
        {
            'name': 'Large Print Sudoku Masters Volume 1',
            'price': 899,  # $8.99
            'description': '100 brain-boosting puzzles for seniors',
            'metadata': {
                'product_id': 'LPSM-VOL1',
                'format': 'pdf',
                'pages': 206
            }
        },
        {
            'name': 'Large Print Sudoku Masters Bundle (Volumes 1-5)',
            'price': 3499,  # $34.99 (save $10)
            'description': '500 puzzles across 5 volumes - Best value!',
            'metadata': {
                'product_id': 'LPSM-BUNDLE',
                'format': 'pdf',
                'volumes': 5
            }
        },
        {
            'name': 'Large Print Crossword Masters Volume 1',
            'price': 999,  # $9.99
            'description': '75 themed crossword puzzles in large print',
            'metadata': {
                'product_id': 'LPCM-VOL1',
                'format': 'pdf',
                'pages': 180
            }
        },
        {
            'name': 'Ultimate Puzzle Bundle (Sudoku + Crossword)',
            'price': 4999,  # $49.99
            'description': '10 books total - The complete collection',
            'metadata': {
                'product_id': 'ULTIMATE-BUNDLE',
                'format': 'pdf',
                'books': 10
            }
        }
    ]
    
    # Generate links
    payment_links = {}
    email_templates = {}
    
    for product in products:
        print(f"\n📦 Creating payment link for: {product['name']}")
        
        result = checkout.create_payment_link(
            product_name=product['name'],
            price_cents=product['price'],
            metadata=product['metadata']
        )
        
        if result['success']:
            payment_links[product['name']] = {
                'url': result['payment_link'],
                'price': product['price'] / 100,
                'product_id': result['product_id'],
                'price_id': result['price_id']
            }
            
            print("✅ Success!")
            print(f"   Payment Link: {result['payment_link']}")
            print(f"   Price: ${product['price'] / 100:.2f}")
            
            # Create email template snippet
            email_templates[product['name']] = f"""
🎯 {product['name']}
{product['description']}

💰 Only ${product['price'] / 100:.2f}

[Get Your Copy Now]({result['payment_link']})
"""
        else:
            print(f"❌ Failed: {result['error']}")
            payment_links[product['name']] = None
    
    # Save payment links
    output_dir = Path('data/payment_links')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON file
    links_file = output_dir / 'stripe_payment_links.json'
    with open(links_file, 'w') as f:
        json.dump(payment_links, f, indent=2)
    
    print(f"\n💾 Payment links saved to: {links_file}")
    
    # Save email templates
    templates_file = output_dir / 'email_templates.txt'
    with open(templates_file, 'w') as f:
        f.write("EMAIL TEMPLATE SNIPPETS FOR PAYMENT LINKS\n")
        f.write("=" * 60 + "\n\n")
        
        for product_name, template in email_templates.items():
            f.write(f"### {product_name}\n")
            f.write(template)
            f.write("\n" + "-" * 40 + "\n")
    
    print(f"📧 Email templates saved to: {templates_file}")
    
    # Generate summary report
    print("\n📊 SUMMARY")
    print("=" * 60)
    print(f"Total products: {len(products)}")
    print(f"Successful links: {sum(1 for v in payment_links.values() if v)}")
    print(f"Failed links: {sum(1 for v in payment_links.values() if not v)}")
    
    if all(payment_links.values()):
        print("\n✅ All payment links generated successfully!")
        print("\n🚀 Next Steps:")
        print("1. Add these links to your email sequences")
        print("2. Update your website with Buy Now buttons")
        print("3. Test each link with a small purchase")
        print("4. Monitor conversions in Stripe Dashboard")
    
    return payment_links


def generate_test_checkout_session():
    """Generate a test checkout session for immediate testing"""
    print("\n🧪 Creating Test Checkout Session")
    print("-" * 40)
    
    checkout = StripeCheckout()
    
    result = checkout.create_checkout_session(
        product_name="TEST - Large Print Sudoku (Do Not Buy)",
        price_cents=100,  # $1.00 for testing
        customer_email="test@example.com",
        success_url="https://kindlemint.com/success?test=true",
        cancel_url="https://kindlemint.com/cancel?test=true",
        metadata={'test_mode': True}
    )
    
    if result['success']:
        print("✅ Test session created!")
        print("\n🔗 Open this URL to test the checkout flow:")
        print(f"   {result['checkout_url']}")
        print("\n💡 Use test card: 4242 4242 4242 4242")
        print("   Any future expiry, any CVC")
    else:
        print(f"❌ Failed: {result['error']}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Stripe payment links')
    parser.add_argument('--test', action='store_true', 
                       help='Create a test checkout session')
    
    args = parser.parse_args()
    
    if args.test:
        generate_test_checkout_session()
    else:
        generate_all_payment_links()


if __name__ == "__main__":
    main()