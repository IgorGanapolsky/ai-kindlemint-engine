from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Handle CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            email = body.get('email')
            first_name = body.get('firstName', '')
            
            if not email:
                response = {'error': 'Email is required'}
            else:
                response = {
                    'success': True,
                    'message': 'Thank you for subscribing! Check your email for your free puzzles.',
                    'subscriber': {
                        'email': email,
                        'firstName': first_name
                    }
                }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                'error': 'Internal server error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        # Handle preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()