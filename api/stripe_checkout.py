
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
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://igorganapolsky.github.io/ai-kindlemint-engine/docs/success.html',
            cancel_url='https://igorganapolsky.github.io/ai-kindlemint-engine/',
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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
        print(f"Payment successful: {session.id}")
        # Here you would deliver the product
        
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
