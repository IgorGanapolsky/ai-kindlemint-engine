#!/usr/bin/env python3
"""
Mission Control Webhook Server - Exposes endpoints for external automation triggers
"""
from flask import Flask, request, jsonify
import subprocess
import os
from datetime import datetime
import threading

app = Flask(__name__)

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'Mission Control Webhook Server Active',
        'timestamp': datetime.now().isoformat(),
        'endpoints': ['/run', '/publish', '/status']
    })

@app.route('/run', methods=['POST'])
def trigger_mission():
    """Trigger a full mission control run"""
    try:
        # Get topic from request body or use default
        data = request.get_json() or {}
        topic = data.get('topic', 'Automated Weekly Book Generation')
        
        # Log the trigger
        with open("mission_log.txt", "a") as log:
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Webhook triggered mission: {topic}\n")
        
        # Run mission control in background
        def run_mission():
            subprocess.run(['python', 'mission_control.py', topic], 
                         capture_output=False, cwd='.')
        
        thread = threading.Thread(target=run_mission)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': f'Mission started for topic: {topic}',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/publish', methods=['POST'])
def trigger_publish():
    """Trigger KDP publishing of latest book"""
    try:
        # Find latest .kpf file
        kpf_files = [f for f in os.listdir('output') if f.endswith('.kpf')]
        
        if not kpf_files:
            return jsonify({
                'status': 'error',
                'error': 'No .kpf files found in output directory',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        latest_file = max(kpf_files, key=lambda x: os.path.getctime(os.path.join('output', x)))
        
        # Log the publish trigger
        with open("mission_log.txt", "a") as log:
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Webhook triggered publish: {latest_file}\n")
        
        # Run publishing script
        def run_publish():
            subprocess.run(['./publish_kdp.sh'], capture_output=False, cwd='.')
        
        thread = threading.Thread(target=run_publish)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': f'Publishing started for: {latest_file}',
            'file': latest_file,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current status and recent activity"""
    try:
        # Count recent output files
        output_files = []
        if os.path.exists('output'):
            for root, dirs, files in os.walk('output'):
                for file in files:
                    filepath = os.path.join(root, file)
                    output_files.append({
                        'name': file,
                        'path': filepath,
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                        'size': os.path.getsize(filepath)
                    })
        
        # Read recent log entries
        recent_logs = []
        if os.path.exists('mission_log.txt'):
            with open('mission_log.txt', 'r') as log:
                recent_logs = log.readlines()[-10:]  # Last 10 entries
        
        return jsonify({
            'status': 'active',
            'output_files_count': len(output_files),
            'recent_files': output_files[-5:],  # Last 5 files
            'recent_logs': [log.strip() for log in recent_logs],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Ensure mission log exists
    if not os.path.exists('mission_log.txt'):
        with open('mission_log.txt', 'w') as log:
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mission Control Webhook Server initialized\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)