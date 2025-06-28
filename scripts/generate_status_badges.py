#!/usr/bin/env python3
"""
Generate Live Agent Orchestration Status Badges
Creates dynamic SVG badges showing real-time agent status
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

class StatusBadgeGenerator:
    """Generate dynamic status badges for agent orchestration"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        
    def get_agent_status(self):
        """Get current agent orchestration status"""
        try:
            from agent_monitor import AgentMonitor
            monitor = AgentMonitor()
            return monitor.get_comprehensive_status()
        except Exception as e:
            return {
                "error": str(e),
                "claude_flow": {"active_agents": 0, "system_status": "Unknown"},
                "active_agents": [],
                "memory": {"total_entries": 0},
                "task_queue": {"pending": 0, "in_progress": 0, "completed": 0}
            }
    
    def generate_shield_url(self, label, message, color="blue", style="flat-square"):
        """Generate shields.io badge URL"""
        label_encoded = quote(label)
        message_encoded = quote(str(message))
        return f"https://img.shields.io/badge/{label_encoded}-{message_encoded}-{color}?style={style}"
    
    def get_status_color(self, status, value=None):
        """Get appropriate color for status"""
        if isinstance(status, str):
            status = status.lower()
            if "running" in status or "active" in status:
                return "brightgreen"
            elif "stopped" in status or "inactive" in status:
                return "red"
            elif "partially" in status:
                return "yellow"
        
        if isinstance(value, int):
            if value == 0:
                return "lightgrey"
            elif value < 5:
                return "yellow"
            else:
                return "brightgreen"
        
        return "blue"
    
    def generate_badges(self):
        """Generate all status badges"""
        status = self.get_agent_status()
        
        badges = {}
        
        # System Status Badge
        cf_status = status.get('claude_flow', {})
        system_status = cf_status.get('system_status', 'Unknown')
        badges['system_status'] = self.generate_shield_url(
            "System", 
            system_status, 
            self.get_status_color(system_status)
        )
        
        # Active Agents Badge
        active_agents = cf_status.get('active_agents', 0)
        badges['active_agents'] = self.generate_shield_url(
            "Active Agents", 
            active_agents, 
            self.get_status_color(None, active_agents)
        )
        
        # Memory Entries Badge
        memory_entries = status.get('memory', {}).get('total_entries', 0)
        badges['memory'] = self.generate_shield_url(
            "Memory Entries", 
            memory_entries, 
            self.get_status_color(None, memory_entries)
        )
        
        # Task Queue Badge
        queue = status.get('task_queue', {})
        pending = queue.get('pending', 0)
        in_progress = queue.get('in_progress', 0)
        completed = queue.get('completed', 0)
        
        if in_progress > 0:
            queue_status = f"{in_progress} Running"
            color = "yellow"
        elif pending > 0:
            queue_status = f"{pending} Queued"
            color = "blue"
        else:
            queue_status = "Idle"
            color = "lightgrey"
        
        badges['task_queue'] = self.generate_shield_url(
            "Task Queue", 
            queue_status, 
            color
        )
        
        # Last Updated Badge
        now = datetime.now().strftime("%H:%M:%S UTC")
        badges['last_updated'] = self.generate_shield_url(
            "Last Updated", 
            now, 
            "informational"
        )
        
        # Orchestration Health Badge
        if active_agents > 0:
            health = "🟢 Orchestrating"
            color = "brightgreen"
        elif system_status == "Partially Running":
            health = "🟡 Ready"
            color = "yellow"
        else:
            health = "🔴 Offline"
            color = "red"
        
        badges['health'] = self.generate_shield_url(
            "Orchestration", 
            health, 
            color
        )
        
        return badges
    
    def generate_dashboard_markdown(self):
        """Generate markdown for the agent dashboard"""
        badges = self.generate_badges()
        status = self.get_agent_status()
        
        dashboard = f"""## 🤖 Live Agent Orchestration Dashboard

![System Status]({badges['system_status']})
![Active Agents]({badges['active_agents']})
![Memory]({badges['memory']})
![Task Queue]({badges['task_queue']})
![Health]({badges['health']})
![Last Updated]({badges['last_updated']})

### Current Status
- **System:** {status.get('claude_flow', {}).get('system_status', 'Unknown')}
- **Active Agents:** {status.get('claude_flow', {}).get('active_agents', 0)}
- **Memory Entries:** {status.get('memory', {}).get('total_entries', 0)}
- **Tasks:** {status.get('task_queue', {}).get('pending', 0)} pending, {status.get('task_queue', {}).get('in_progress', 0)} running

### Quick Commands
```bash
# Monitor agents live
python scripts/agent_monitor.py --continuous

# Start orchestration
./claude-flow start --ui --port 3000

# Spawn agents
./claude-flow sparc "task description" --mode orchestrator
./claude-flow swarm "complex task" --strategy development --parallel
```

### Agent Types Available
- 🔍 **Research Agents** - Market analysis, data gathering
- 💻 **Code Agents** - Development, testing, debugging  
- 📊 **QA Agents** - Quality validation, testing
- 🎯 **Orchestrator Agents** - Multi-agent coordination
- 🧠 **Memory Agents** - Data storage and retrieval

---
*Dashboard auto-updates every 5 minutes via GitHub Actions*
"""
        return dashboard
    
    def save_status_json(self):
        """Save current status to JSON for GitHub Actions"""
        status = self.get_agent_status()
        badges = self.generate_badges()
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "badges": badges,
            "dashboard_markdown": self.generate_dashboard_markdown()
        }
        
        output_file = self.base_path / "agent_status.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        return output_file


def main():
    """Generate status badges and dashboard"""
    generator = StatusBadgeGenerator()
    
    # Generate badges
    badges = generator.generate_badges()
    print("🎯 Generated Status Badges:")
    for name, url in badges.items():
        print(f"  {name}: {url}")
    
    # Generate dashboard markdown
    dashboard = generator.generate_dashboard_markdown()
    print(f"\n📊 Dashboard Markdown ({len(dashboard)} chars):")
    print(dashboard[:500] + "..." if len(dashboard) > 500 else dashboard)
    
    # Save status JSON
    output_file = generator.save_status_json()
    print(f"\n💾 Status saved to: {output_file}")


if __name__ == "__main__":
    main()