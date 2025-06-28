#!/usr/bin/env python3
"""
Update README.md with Live Agent Orchestration Dashboard
Injects real-time agent status into the README
"""

import json
import re
from pathlib import Path
from datetime import datetime

class ReadmeUpdater:
    """Update README with live agent dashboard"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.readme_path = self.base_path / "README.md"
        self.status_path = self.base_path / "agent_status.json"
        
    def load_agent_status(self):
        """Load the latest agent status"""
        if not self.status_path.exists():
            # Generate status if file doesn't exist
            import subprocess
            subprocess.run([
                "python", 
                str(self.base_path / "scripts" / "generate_status_badges.py")
            ])
        
        try:
            with open(self.status_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading status: {e}")
            return None
    
    def generate_fallback_dashboard(self):
        """Generate fallback dashboard when agent system is offline"""
        return """## 🤖 Live Agent Orchestration Dashboard

![System Status](https://img.shields.io/badge/System-Offline-red?style=flat-square)
![Active Agents](https://img.shields.io/badge/Active%20Agents-0-lightgrey?style=flat-square)
![Memory](https://img.shields.io/badge/Memory%20Entries-0-lightgrey?style=flat-square)
![Task Queue](https://img.shields.io/badge/Task%20Queue-Idle-lightgrey?style=flat-square)
![Health](https://img.shields.io/badge/Orchestration-🔴%20Offline-red?style=flat-square)
![Last Updated](https://img.shields.io/badge/Last%20Updated-Unknown-informational?style=flat-square)

### Current Status
- **System:** Agent orchestration system offline
- **Active Agents:** 0
- **Memory Entries:** 0
- **Tasks:** 0 pending, 0 running

### Quick Start Commands
```bash
# Start orchestration system
./claude-flow start --ui --port 3000

# Monitor agents live
python scripts/agent_monitor.py --continuous

# Spawn your first agent
./claude-flow sparc "analyze codebase quality" --mode orchestrator
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
    
    def update_readme(self):
        """Update README with latest agent dashboard"""
        if not self.readme_path.exists():
            print(f"❌ README.md not found at {self.readme_path}")
            return False
        
        # Load current README
        with open(self.readme_path, 'r') as f:
            content = f.read()
        
        # Load agent status
        status_data = self.load_agent_status()
        
        if status_data and 'dashboard_markdown' in status_data:
            dashboard = status_data['dashboard_markdown']
        else:
            print("⚠️  Using fallback dashboard (agent system offline)")
            dashboard = self.generate_fallback_dashboard()
        
        # Define markers for the dashboard section
        start_marker = "<!-- AGENT_DASHBOARD_START -->"
        end_marker = "<!-- AGENT_DASHBOARD_END -->"
        
        # Check if markers exist
        if start_marker in content and end_marker in content:
            # Replace existing dashboard
            pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
            replacement = f"{start_marker}\n{dashboard}\n{end_marker}"
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # Add dashboard section after title
            title_pattern = r"(# [^\n]+\n)"
            if re.search(title_pattern, content):
                replacement = f"\\1\n{start_marker}\n{dashboard}\n{end_marker}\n"
                new_content = re.sub(title_pattern, replacement, content, count=1)
            else:
                # Prepend to beginning if no title found
                new_content = f"{start_marker}\n{dashboard}\n{end_marker}\n\n{content}"
        
        # Write updated README
        with open(self.readme_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ README.md updated with live agent dashboard")
        
        # Save update metadata
        metadata = {
            "last_updated": datetime.now().isoformat(),
            "dashboard_size": len(dashboard),
            "status_available": status_data is not None
        }
        
        metadata_path = self.base_path / "agent_dashboard_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True


def main():
    """Update README with agent dashboard"""
    updater = ReadmeUpdater()
    
    print("🤖 Updating README with Live Agent Orchestration Dashboard...")
    success = updater.update_readme()
    
    if success:
        print("✅ Dashboard update completed successfully!")
    else:
        print("❌ Dashboard update failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())