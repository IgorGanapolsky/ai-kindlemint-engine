#!/usr/bin/env python3
"""
Spawn a single agent for a specific task
"""

import sys
sys.path.append('.')

from scripts.multi_agent_orchestrator import MultiAgentOrchestrator
import time

def spawn_single_agent(url, task_description):
    """Spawn a single agent for a specific task"""
    
    print(f"🤖 Spawning Agent for: {url}")
    print("=" * 60)
    
    orchestrator = MultiAgentOrchestrator()
    
    # Create full task description
    full_task = f"{task_description} (URL: {url})"
    
    # Spawn the agent
    print(f"\n🚀 Creating agent...")
    agent_id = orchestrator.spawn_agent(full_task)
    print(f"✓ Agent {agent_id} spawned")
    
    print(f"\n⏳ Agent {agent_id} is working on:")
    print(f"   {task_description}")
    print(f"\nThe agent will:")
    print("   • Create its own worktree")
    print("   • Research the resource")
    print("   • Implement findings")
    print("   • Update documentation")
    print("   • Create a pull request")
    
    # Wait for completion
    print(f"\n⌛ Waiting for agent to complete (timeout: 5 minutes)...")
    orchestrator.wait_for_agents([agent_id], timeout=300)
    
    # Get final status
    status = orchestrator.get_agent_status(agent_id)
    
    print(f"\n📊 Agent Status:")
    print(f"   ID: {agent_id}")
    print(f"   Status: {status['status']}")
    print(f"   Branch: {status['branch']}")
    
    if status['status'] == 'pr_created':
        print("\n✅ Pull request created successfully!")
        print("   Check GitHub for the new PR")
    elif status['status'] == 'failed':
        print("\n❌ Agent failed to complete task")
        print("   Check logs for details")
    else:
        print(f"\n⚠️ Agent ended with status: {status['status']}")
    
    return agent_id, status

if __name__ == "__main__":
    # Spawn agent for the requested Snipd episode with a different focus
    url = "https://share.snipd.com/episode/93f9c717-ec18-4590-9958-def02c4aaec7"
    task = "Deep dive into Snipd episode - extract specific implementation tactics for immediate revenue impact"
    
    agent_id, status = spawn_single_agent(url, task)
    
    print("\n🎉 Agent spawning complete!")
    print(f"Agent {agent_id} has finished its work.")