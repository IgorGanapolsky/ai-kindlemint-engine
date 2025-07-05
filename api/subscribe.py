"""
Vercel API endpoint for email subscription and lead magnet delivery

This endpoint:
1. Captures email and first name from landing page
2. Stores subscriber in database/CSV
3. Triggers SendGrid to send welcome email with PDF
4. Tags subscriber for email sequence
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kindlemint.email import EmailAutomation
from src.kindlemint.analytics import ConversionTracker
from scripts.generate_lead_magnet import generate_lead_magnet

def handler(request):
    """
    Handle POST requests for email subscription
    
    Expected body:
    {
        "email": "user@example.com",
        "firstName": "John"
    }
    """
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Only accept POST
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Parse request body
        body = json.loads(request.body)
        email = body.get('email')
        first_name = body.get('firstName', '')
        
        if not email:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Email is required'})
            }
        
        # Initialize email automation and tracking
        email_automation = EmailAutomation()
        tracker = ConversionTracker()
        
        # Check if lead magnet exists, generate if not
        lead_magnet_dir = Path('generated/lead_magnets')
        lead_magnet_files = list(lead_magnet_dir.glob('5_FREE_Brain_Boosting_Puzzles_*.pdf'))
        
        if not lead_magnet_files:
            # Generate lead magnet
            try:
                result = generate_lead_magnet()
                lead_magnet_path = result['pdf_file']
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Failed to generate lead magnet',
                        'message': str(e)
                    })
                }
        else:
            # Use existing lead magnet
            lead_magnet_path = str(lead_magnet_files[0])
        
        # Add subscriber to automation system
        result = email_automation.add_subscriber(
            email=email,
            first_name=first_name,
            sequence='sudoku_lead_magnet',
            tags=['senior_audience', 'large_print', 'landing_page'],
            lead_magnet_path=lead_magnet_path
        )
        
        if not result['success']:
            if result.get('error') == 'Already subscribed':
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'message': 'You are already subscribed! Check your email for your puzzles.',
                        'already_subscribed': True
                    })
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Failed to process subscription',
                        'message': result.get('error')
                    })
                }
        
        # Track successful signup
        tracker.track_signup(email, first_name, "landing_page")
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'message': 'Thank you for subscribing! Check your email for your free puzzles.',
                'subscriber': {
                    'email': email,
                    'firstName': first_name
                }
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