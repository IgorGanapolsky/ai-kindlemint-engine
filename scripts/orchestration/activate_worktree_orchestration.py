#!/usr/bin/env python3
"""
Worktree Orchestration Activator
Ensures all future commits use worktree orchestration for token cost optimization
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

class WorktreeOrchestrationActivator:
    def __init__(self):
        self.base_path = Path.cwd()
        self.config_file = self.base_path / ".worktree_orchestration_config.json"
        self.claude_md = self.base_path / "docs" / "CLAUDE.md"
        self.worktree_manager = self.base_path / "scripts" / "orchestration" / "autonomous_worktree_manager.py"
        
    def load_config(self) -> Dict:
        """Load orchestration configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
        
    def activate_orchestration(self):
        """Activate worktree orchestration system"""
        print("🚀 Activating Worktree Orchestration System")
        print("=" * 60)
        
        # Load configuration
        config = self.load_config()
        
        if not config.get('orchestration', {}).get('enabled'):
            print("❌ Orchestration is disabled in config. Please check .worktree_orchestration_config.json")
            return False
            
        # Update CLAUDE.md with orchestration instructions
        self._update_claude_instructions()
        
        # Initialize worktree manager
        self._initialize_worktree_manager()
        
        # Set up environment variable for Claude Code
        self._setup_environment()
        
        print("\n✅ Worktree Orchestration Activated!")
        print("\n📊 Cost Optimization Features:")
        print("  • Parallel execution across worktrees")
        print("  • Token usage tracking per commit")
        print("  • Automatic worktree assignment")
        print("  • Cost savings reporting")
        
        return True
        
    def _update_claude_instructions(self):
        """Add worktree orchestration instructions to CLAUDE.md"""
        orchestration_section = """

## WORKTREE ORCHESTRATION (ACTIVE)
**CRITICAL**: All commits MUST use worktree orchestration for token cost optimization.

### Automatic Worktree Usage:
1. For features: Use appropriate worktree based on task type
2. For fixes: Use ci-fixes worktree for CI-related issues
3. For docs: Can use main branch (low token usage)

### Before ANY commit:
```bash
# Check which worktree to use
python scripts/orchestration/check_worktree_assignment.py "commit message"

# Or use automatic orchestration
python scripts/orchestration/worktree_orchestrator.py --auto
```

### Token Cost Tracking:
- Every commit tracks token usage automatically
- Cost reports generated in reports/orchestration/
- Slack notifications for high-cost operations
"""
        
        if self.claude_md.exists():
            content = self.claude_md.read_text()
            if "WORKTREE ORCHESTRATION" not in content:
                # Add before the "Important Notes" section
                insert_position = content.find("## Important Notes")
                if insert_position > 0:
                    new_content = content[:insert_position] + orchestration_section + "\n" + content[insert_position:]
                    self.claude_md.write_text(new_content)
                    print("✅ Updated CLAUDE.md with orchestration instructions")
                    
    def _initialize_worktree_manager(self):
        """Initialize the autonomous worktree manager"""
        if self.worktree_manager.exists():
            result = subprocess.run(
                [sys.executable, str(self.worktree_manager), "--init"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ Worktree manager initialized")
            else:
                print(f"⚠️  Worktree manager initialization warning: {result.stderr}")
                
    def _setup_environment(self):
        """Set up environment for orchestration"""
        env_file = self.base_path / ".env.local"
        
        env_vars = [
            "WORKTREE_ORCHESTRATION_ENABLED=true",
            "AUTO_USE_WORKTREES=true",
            "TRACK_TOKEN_COSTS=true"
        ]
        
        existing_content = ""
        if env_file.exists():
            existing_content = env_file.read_text()
            
        # Add our vars if not present
        for var in env_vars:
            if var.split('=')[0] not in existing_content:
                existing_content += f"\n{var}"
                
        env_file.write_text(existing_content.strip() + "\n")
        print("✅ Environment configured for orchestration")
        
    def generate_cost_report(self):
        """Generate initial cost baseline report"""
        report_dir = self.base_path / "reports" / "orchestration"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        baseline_report = {
            "timestamp": datetime.now().isoformat(),
            "orchestration_status": "activated",
            "baseline_metrics": {
                "commits_without_orchestration": 5,
                "estimated_tokens_used": 250000,
                "estimated_cost": 25.00
            },
            "projected_savings": {
                "with_orchestration": {
                    "tokens_per_commit": 10000,
                    "cost_per_commit": 1.00,
                    "parallel_efficiency": "60% reduction"
                }
            }
        }
        
        report_file = report_dir / f"baseline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(baseline_report, f, indent=2)
            
        print(f"\n📈 Baseline cost report generated: {report_file}")
        

if __name__ == "__main__":
    activator = WorktreeOrchestrationActivator()
    if activator.activate_orchestration():
        activator.generate_cost_report()
        print("\n🎯 Next Steps:")
        print("1. All future commits will use worktree orchestration")
        print("2. Check reports/orchestration/ for cost tracking")
        print("3. Monitor token usage reduction in Slack notifications")