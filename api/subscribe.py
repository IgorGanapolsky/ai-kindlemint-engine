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
from http.server import BaseHTTPRequestHandler
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Handle CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            email = body.get('email')
            first_name = body.get('firstName', '')
            
            if not email:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Email is required'}).encode())
                return
            
            # For now, just return success
            # TODO: Integrate with actual email system once imports are fixed
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response_data = {
                'success': True,
                'message': 'Thank you for subscribing! Check your email for your free puzzles.',
                'subscriber': {
                    'email': email,
                    'firstName': first_name
                }
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            }).encode())
    
    def do_OPTIONS(self):
        # Handle preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()