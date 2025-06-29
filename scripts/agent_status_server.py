#!/usr/bin/env python3
"""
Real-time Agent Status Server
Serves live agent orchestration status via HTTP endpoints
"""

import asyncio
import json
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class AgentStatusHandler(BaseHTTPRequestHandler):
    """HTTP handler for agent status endpoints"""

    def __init__(self, *args, status_monitor=None, **kwargs):
        self.status_monitor = status_monitor
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        # CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        if path == "/status":
            self.serve_status()
        elif path == "/badges":
            self.serve_badges()
        elif path == "/health":
            self.serve_health()
        elif path == "/dashboard":
            self.serve_dashboard()
        elif path.startswith("/badge/"):
            badge_type = path.split("/")[-1]
            self.serve_individual_badge(badge_type)
        else:
            self.serve_api_info()

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def serve_status(self):
        """Serve complete agent status as JSON"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        if self.status_monitor:
            status = self.status_monitor.get_comprehensive_status()
        else:
            status = {"error": "Status monitor not available"}

        self.wfile.write(json.dumps(status, indent=2).encode())

    def serve_badges(self):
        """Serve badge URLs as JSON"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        try:
            from generate_status_badges import StatusBadgeGenerator

            generator = StatusBadgeGenerator()
            badges = generator.generate_badges()
            self.wfile.write(json.dumps(badges, indent=2).encode())
        except Exception as e:
            error = {"error": f"Failed to generate badges: {str(e)}"}
            self.wfile.write(json.dumps(error).encode())

    def serve_health(self):
        """Serve simple health check"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": (
                getattr(self.status_monitor, "uptime", 0) if self.status_monitor else 0
            ),
        }
        self.wfile.write(json.dumps(health).encode())

    def serve_dashboard(self):
        """Serve dashboard markdown"""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        try:
            from generate_status_badges import StatusBadgeGenerator

            generator = StatusBadgeGenerator()
            dashboard = generator.generate_dashboard_markdown()
            self.wfile.write(dashboard.encode())
        except Exception as e:
            error = f"Error generating dashboard: {str(e)}"
            self.wfile.write(error.encode())

    def serve_individual_badge(self, badge_type):
        """Serve individual badge URL"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        try:
            from generate_status_badges import StatusBadgeGenerator

            generator = StatusBadgeGenerator()
            badges = generator.generate_badges()

            if badge_type in badges:
                result = {
                    "badge_type": badge_type,
                    "url": badges[badge_type],
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                result = {
                    "error": f"Badge type '{badge_type}' not found",
                    "available": list(badges.keys()),
                }

            self.wfile.write(json.dumps(result, indent=2).encode())
        except Exception as e:
            error = {"error": f"Failed to get badge: {str(e)}"}
            self.wfile.write(json.dumps(error).encode())

    def serve_api_info(self):
        """Serve API information"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        api_info = {
            "name": "Claude Code Agent Status API",
            "version": "1.0.0",
            "endpoints": {
                "/status": "Complete agent orchestration status",
                "/badges": "All status badge URLs",
                "/health": "Simple health check",
                "/dashboard": "Dashboard markdown",
                "/badge/{type}": "Individual badge URL",
            },
            "badge_types": [
                "system_status",
                "active_agents",
                "memory",
                "task_queue",
                "health",
                "last_updated",
            ],
            "timestamp": datetime.now().isoformat(),
        }
        self.wfile.write(json.dumps(api_info, indent=2).encode())

    def log_message(self, format, *args):
        """Custom log format"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.client_address[0]} - {format % args}")


class AgentStatusServer:
    """Real-time agent status server"""

    def __init__(self, port=8080, host="localhost"):
        self.port = port
        self.host = host
        self.server = None
        self.status_monitor = None
        self.start_time = datetime.now()

    def setup_status_monitor(self):
        """Setup the status monitor"""
        try:
            import sys

            sys.path.append(str(Path(__file__).parent))
            from agent_monitor import AgentMonitor

            self.status_monitor = AgentMonitor()
            self.status_monitor.uptime = 0
        except Exception as e:
            print(f"⚠️  Could not setup status monitor: {e}")

    def create_handler(self):
        """Create HTTP handler with status monitor"""
        status_monitor = self.status_monitor

        class StatusHandler(AgentStatusHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, status_monitor=status_monitor, **kwargs)

        return StatusHandler

    def start(self):
        """Start the status server"""
        self.setup_status_monitor()

        handler_class = self.create_handler()
        self.server = HTTPServer((self.host, self.port), handler_class)

        print(f"🌐 Agent Status Server starting on http://{self.host}:{self.port}")
        print(f"📊 Endpoints available:")
        print(f"   • http://{self.host}:{self.port}/status")
        print(f"   • http://{self.host}:{self.port}/badges")
        print(f"   • http://{self.host}:{self.port}/health")
        print(f"   • http://{self.host}:{self.port}/dashboard")
        print(f"   • http://{self.host}:{self.port}/badge/system_status")

        # Update uptime in background
        def update_uptime():
            while True:
                if self.status_monitor:
                    self.status_monitor.uptime = (
                        datetime.now() - self.start_time
                    ).total_seconds()
                time.sleep(1)

        uptime_thread = threading.Thread(target=update_uptime, daemon=True)
        uptime_thread.start()

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Agent Status Server stopped")
            self.server.shutdown()

    def stop(self):
        """Stop the status server"""
        if self.server:
            self.server.shutdown()


def main():
    """Start the agent status server"""
    import argparse

    parser = argparse.ArgumentParser(description="Real-time Agent Status Server")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Server port")
    parser.add_argument("--host", type=str, default="localhost", help="Server host")

    args = parser.parse_args()

    server = AgentStatusServer(port=args.port, host=args.host)
    server.start()


if __name__ == "__main__":
    main()
