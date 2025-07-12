#!/usr/bin/env python3
"""
MCP Server Management Tools
Tools for managing, testing, and monitoring the MCP server deployment
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime
import subprocess
import time

# MCP Server Configuration
MCP_SERVER_IP = "44.201.249.255"
MCP_SERVER_PORT = "8080"
MCP_SERVER_URL = f"http://{MCP_SERVER_IP}:{MCP_SERVER_PORT}"
GITHUB_APP_ID = os.environ.get('GITHUB_APP_ID', 'YOUR_APP_ID')

class MCPServerTools:
    def __init__(self):
        self.server_url = MCP_SERVER_URL
        self.github_app_id = GITHUB_APP_ID
        
    def check_server_status(self):
        """Check if the MCP server is running and responsive"""
        print(f"Checking MCP server status at {self.server_url}...")
        
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ MCP server is running and healthy")
                return True
            else:
                print(f"⚠️ MCP server responded with status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to MCP server at {self.server_url}")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ Connection timeout to MCP server")
            return False
            
    def test_webhook_endpoint(self):
        """Test the webhook endpoint with a sample payload"""
        print(f"\nTesting webhook endpoint at {self.server_url}/webhook...")
        
        # Sample GitHub webhook payload (ping event)
        test_payload = {
            "zen": "Design for failure.",
            "hook_id": 12345,
            "hook": {
                "type": "App",
                "id": 12345,
                "name": "web",
                "active": True,
                "events": ["push", "pull_request"],
                "config": {
                    "content_type": "json",
                    "url": f"{self.server_url}/webhook",
                    "insecure_ssl": "0"
                },
                "updated_at": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "app_id": int(self.github_app_id)
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-GitHub-Event": "ping",
            "X-GitHub-Delivery": f"test-{int(time.time())}"
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/webhook",
                json=test_payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Webhook endpoint responded successfully")
                print(f"Response: {response.text}")
                return True
            else:
                print(f"⚠️ Webhook endpoint responded with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing webhook endpoint: {str(e)}")
            return False
            
    def create_test_pr_event(self):
        """Create a test PR event to trigger automation"""
        print(f"\nCreating test PR event...")
        
        # Sample PR opened event
        pr_payload = {
            "action": "opened",
            "number": 999,
            "pull_request": {
                "id": 123456789,
                "number": 999,
                "state": "open",
                "title": "Test PR for MCP automation",
                "body": "This is a test PR to verify MCP server webhook handling",
                "user": {
                    "login": "test-user",
                    "id": 12345
                },
                "head": {
                    "ref": "test-branch",
                    "sha": "abc123"
                },
                "base": {
                    "ref": "main",
                    "sha": "def456"
                },
                "html_url": "https://github.com/IgorGanapolsky/ai-kindlemint-engine/pull/999",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            "repository": {
                "id": 987654321,
                "name": "ai-kindlemint-engine",
                "full_name": "IgorGanapolsky/ai-kindlemint-engine",
                "private": False,
                "owner": {
                    "login": "IgorGanapolsky",
                    "id": 54321
                }
            },
            "sender": {
                "login": "test-user",
                "id": 12345
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": f"test-pr-{int(time.time())}"
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/webhook",
                json=pr_payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Test PR event sent successfully")
                print(f"Response: {response.text}")
                return True
            else:
                print(f"⚠️ Server responded with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending test PR event: {str(e)}")
            return False
            
    def ssh_to_server(self):
        """Provide SSH command to connect to the EC2 instance"""
        print(f"\nTo SSH into the MCP server EC2 instance:")
        print(f"ssh -i /path/to/your-key.pem ec2-user@{MCP_SERVER_IP}")
        print(f"\nOnce connected, you can check Docker logs with:")
        print("docker logs $(docker ps -q)")
        print("\nOr follow logs in real-time:")
        print("docker logs -f $(docker ps -q)")
        
    def check_docker_status(self):
        """Check Docker container status via SSH (requires key)"""
        print("\nTo check Docker container status on the server:")
        print("1. SSH into the server")
        print("2. Run: docker ps")
        print("3. Check logs: docker logs [container-id]")
        
    def monitor_webhooks(self, duration=60):
        """Monitor webhook activity for a specified duration"""
        print(f"\nMonitoring webhook activity for {duration} seconds...")
        print("Press Ctrl+C to stop monitoring")
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                # In a real implementation, this would tail logs or use a monitoring endpoint
                print(".", end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
            
def main():
    parser = argparse.ArgumentParser(description="MCP Server Management Tools")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    subparsers.add_parser("status", help="Check MCP server status")
    
    # Test webhook command
    subparsers.add_parser("test-webhook", help="Test webhook endpoint")
    
    # Test PR event command
    subparsers.add_parser("test-pr", help="Send test PR event")
    
    # SSH info command
    subparsers.add_parser("ssh", help="Show SSH connection info")
    
    # Docker info command
    subparsers.add_parser("docker", help="Show Docker status commands")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor webhook activity")
    monitor_parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    
    # All command
    subparsers.add_parser("all", help="Run all checks")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    tools = MCPServerTools()
    
    if args.command == "status":
        tools.check_server_status()
    elif args.command == "test-webhook":
        tools.test_webhook_endpoint()
    elif args.command == "test-pr":
        tools.create_test_pr_event()
    elif args.command == "ssh":
        tools.ssh_to_server()
    elif args.command == "docker":
        tools.check_docker_status()
    elif args.command == "monitor":
        tools.monitor_webhooks(args.duration)
    elif args.command == "all":
        tools.check_server_status()
        tools.test_webhook_endpoint()
        tools.create_test_pr_event()
        tools.ssh_to_server()

if __name__ == "__main__":
    main()