#!/bin/bash
# V3 Zero-Touch Publishing Engine - Container Entrypoint

set -e

echo "🚀 Starting V3 Zero-Touch KDP Publisher Container"

# Start virtual display for headless browser operation
echo "🖥️  Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Wait for display to initialize
sleep 2

# Start health check server in background
echo "🏥 Starting health check server..."
python -c "
import uvicorn
from fastapi import FastAPI
import asyncio
import threading

app = FastAPI()

@app.get('/health')
def health_check():
    return {'status': 'healthy', 'service': 'kdp-publisher'}

def run_health_server():
    uvicorn.run(app, host='0.0.0.0', port=8080, log_level='warning')

threading.Thread(target=run_health_server, daemon=True).start()
" &

# Wait for health server to start
sleep 3

echo "📚 Executing KDP Publishing Task..."

# Execute the main publishing task
python kdp_publisher_task.py

echo "✅ KDP Publishing Task Completed"