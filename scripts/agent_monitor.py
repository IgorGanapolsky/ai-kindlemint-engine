#!/usr/bin/env python3
"""
Agent Monitoring Dashboard
Real-time monitoring of Claude Code agent orchestration
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class AgentMonitor:
    """Monitor active Claude Code agents and orchestration status"""

        """  Init  """
def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.last_update = datetime.now()

    def get_claude_flow_status(self) -> Dict[str, Any]:
        """Get current claude-flow system status"""
        try:
            result = subprocess.run(
                ["./claude-flow", "status"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                output = result.stdout
                status = self._parse_status_output(output)
                return status
            else:
                return {"error": f"claude-flow status failed: {result.stderr}"}

        except Exception as e:
            return {"error": f"Failed to get status: {str(e)}"}

    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get list of currently active agents"""
        try:
            result = subprocess.run(
                ["./claude-flow", "agent", "list"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                agents = self._parse_agent_list(result.stdout)
                return agents
            else:
                return []

        except Exception:
            return []

    def get_memory_status(self) -> Dict[str, Any]:
        """Get shared memory status for agent coordination"""
        try:
            result = subprocess.run(
                ["./claude-flow", "memory", "stats"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return self._parse_memory_stats(result.stdout)
            else:
                return {"total_entries": 0, "error": "Could not get memory stats"}

        except Exception as e:
            return {"total_entries": 0, "error": str(e)}

    def get_task_queue_status(self) -> Dict[str, Any]:
        """Get current task queue status"""
        try:
            result = subprocess.run(
                ["./claude-flow", "task", "list"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return self._parse_task_queue(result.stdout)
            else:
                return {"pending": 0, "in_progress": 0, "completed": 0}

        except Exception:
            return {"pending": 0, "in_progress": 0, "completed": 0}

    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Get all running Claude-related processes"""
        try:
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                processes = []
                for line in result.stdout.split("\\n"):
                    if "claude" in line.lower() and "grep" not in line:
                        parts = line.split()
                        if len(parts) >= 11:
                            processes.append(
                                {
                                    "pid": parts[1],
                                    "cpu": parts[2],
                                    "memory": parts[3],
                                    "command": (
                                        " ".join(parts[10:])[:100] + "..."
                                        if len(" ".join(parts[10:])) > 100
                                        else " ".join(parts[10:])
                                    ),
                                }
                            )
                return processes
            else:
                return []

        except Exception:
            return []

    def _parse_status_output(self, output: str) -> Dict[str, Any]:
        """Parse claude-flow status output"""
        status = {
            "system_status": "unknown",
            "active_agents": 0,
            "queued_tasks": 0,
            "memory_entries": 0,
            "terminal_pool": "unknown",
            "mcp_server": "unknown",
        }

        for line in output.split("\\n"):
            if "Status:" in line:
                status["system_status"] = line.split("Status:")[-1].strip()
            elif "Agents:" in line:
                try:
                    status["active_agents"] = int(line.split("Agents:")[-1].split()[0])
                except BaseException:
                    pass
            elif "Tasks:" in line:
                try:
                    status["queued_tasks"] = int(line.split("Tasks:")[-1].split()[0])
                except BaseException:
                    pass
            elif "Memory:" in line:
                try:
                    status["memory_entries"] = int(line.split("Memory:")[-1].split()[0])
                except BaseException:
                    pass
            elif "Terminal Pool:" in line:
                status["terminal_pool"] = line.split("Terminal Pool:")[-1].strip()
            elif "MCP Server:" in line:
                status["mcp_server"] = line.split("MCP Server:")[-1].strip()

        return status

    def _parse_agent_list(self, output: str) -> List[Dict[str, Any]]:
        """Parse agent list output"""
        agents = []
        for line in output.split("\\n"):
            if line.strip() and not line.startswith("✅") and not line.startswith("📋"):
                # Parse agent line format
                parts = line.strip().split()
                if len(parts) >= 2:
                    agents.append(
                        {
                            "name": parts[0],
                            "type": parts[1] if len(parts) > 1 else "unknown",
                            "status": "active",
                        }
                    )
        return agents

    def _parse_memory_stats(self, output: str) -> Dict[str, Any]:
        """Parse memory stats output"""
        stats = {"total_entries": 0, "size_mb": 0}
        for line in output.split("\\n"):
            if "entries:" in line:
                try:
                    stats["total_entries"] = int(line.split("entries:")[-1].strip())
                except BaseException:
                    pass
            elif "size:" in line:
                try:
                    size_str = line.split("size:")[-1].strip()
                    if "MB" in size_str:
                        stats["size_mb"] = float(size_str.replace("MB", "").strip())
                except BaseException:
                    pass
        return stats

    def _parse_task_queue(self, output: str) -> Dict[str, Any]:
        """Parse task queue output"""
        queue = {"pending": 0, "in_progress": 0, "completed": 0}
        for line in output.split("\\n"):
            if "pending:" in line:
                try:
                    queue["pending"] = int(line.split("pending:")[-1].strip())
                except BaseException:
                    pass
            elif "in_progress:" in line:
                try:
                    queue["in_progress"] = int(line.split("in_progress:")[-1].strip())
                except BaseException:
                    pass
            elif "completed:" in line:
                try:
                    queue["completed"] = int(line.split("completed:")[-1].strip())
                except BaseException:
                    pass
        return queue

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all agent orchestration"""
        return {
            "timestamp": datetime.now().isoformat(),
            "claude_flow": self.get_claude_flow_status(),
            "active_agents": self.get_active_agents(),
            "memory": self.get_memory_status(),
            "task_queue": self.get_task_queue_status(),
            "processes": self.get_running_processes(),
        }

        """Print Dashboard"""
def print_dashboard(self):
        """Print a live dashboard of agent status"""
        status = self.get_comprehensive_status()

        print("\\n" + "=" * 60)
        print("🤖 CLAUDE CODE AGENT ORCHESTRATION DASHBOARD")
        print("=" * 60)
        print(f"⏰ Last Update: {status['timestamp']}")

        # System Status
        cf_status = status["claude_flow"]
        if "error" not in cf_status:
            print(f"\\n🟢 System Status: {cf_status.get('system_status', 'Unknown')}")
            print(f"🤖 Active Agents: {cf_status.get('active_agents', 0)}")
            print(f"📋 Queued Tasks: {cf_status.get('queued_tasks', 0)}")
            print(f"💾 Memory Entries: {cf_status.get('memory_entries', 0)}")
            print(f"🖥️  Terminal Pool: {cf_status.get('terminal_pool', 'Unknown')}")
            print(f"🌐 MCP Server: {cf_status.get('mcp_server', 'Unknown')}")
        else:
            print(f"\\n❌ System Error: {cf_status['error']}")

        # Active Agents
        agents = status["active_agents"]
        if agents:
            print(f"\\n👥 ACTIVE AGENTS ({len(agents)}):")
            for agent in agents:
                print(f"   • {agent['name']} ({agent['type']}) - {agent['status']}")
        else:
            print("\\n👥 No active agents")

        # Memory Status
        memory = status["memory"]
        if memory["total_entries"] > 0:
            print(f"\\n🧠 SHARED MEMORY:")
            print(f"   • Entries: {memory['total_entries']}")
            if "size_mb" in memory:
                print(f"   • Size: {memory['size_mb']:.1f} MB")

        # Task Queue
        queue = status["task_queue"]
        total_tasks = queue["pending"] + queue["in_progress"] + queue["completed"]
        if total_tasks > 0:
            print(f"\\n📋 TASK QUEUE:")
            print(f"   • Pending: {queue['pending']}")
            print(f"   • In Progress: {queue['in_progress']}")
            print(f"   • Completed: {queue['completed']}")

        # Running Processes
        processes = status["processes"]
        if processes:
            print(f"\\n⚡ CLAUDE PROCESSES ({len(processes)}):")
            for proc in processes[:5]:  # Show top 5
                print(
                    f"   • PID {proc['pid']} - CPU: {proc['cpu']
                                                     }% - Memory: {proc['memory']}%"
                )
                print(f"     {proc['command']}")

        print("\\n" + "=" * 60)

        """Monitor Continuously"""
def monitor_continuously(self, interval: int = 5):
        """Continuously monitor and display agent status"""
        try:
            while True:
                os.system("clear" if os.name == "posix" else "cls")
                self.print_dashboard()
                print(f"\\n🔄 Refreshing every {interval} seconds... (Ctrl+C to stop)")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\\n\\n👋 Agent monitoring stopped.")

        """Save Status Report"""
def save_status_report(self, filename: str = None):
        """Save current status to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_status_report_{timestamp}.json"

        status = self.get_comprehensive_status()

        with open(filename, "w") as f:
            json.dump(status, f, indent=2)

        print(f"📄 Status report saved to: {filename}")
        return filename


    """Main"""
def main():
    """Main function to run agent monitoring"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor Claude Code agent orchestration"
    )
    parser.add_argument(
        "--continuous", "-c", action="store_true", help="Continuous monitoring mode"
    )
    parser.add_argument(
        "--interval", "-i", type=int, default=5, help="Refresh interval in seconds"
    )
    parser.add_argument(
        "--save", "-s", action="store_true", help="Save status report to file"
    )
    parser.add_argument(
        "--output", "-o", type=str, help="Output filename for status report"
    )

    args = parser.parse_args()

    monitor = AgentMonitor()

    if args.continuous:
        monitor.monitor_continuously(args.interval)
    elif args.save:
        monitor.save_status_report(args.output)
    else:
        monitor.print_dashboard()


if __name__ == "__main__":
    main()
