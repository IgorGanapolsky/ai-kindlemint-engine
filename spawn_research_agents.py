#!/usr/bin/env python3
"""
Spawn multiple research agents to investigate various resources
Each agent works in its own worktree and creates a PR
"""

import sys
sys.path.append('.')

from scripts.multi_agent_orchestrator import MultiAgentOrchestrator
import time

def main():
    print("🤖 Spawning Research Agents")
    print("=" * 60)
    
    orchestrator = MultiAgentOrchestrator()
    
    # Define research tasks based on user requests
    research_tasks = [
        {
            "url": "https://agntcy.org/",
            "task": "Research agntcy.org automation platform and integrate insights for revenue automation"
        },
        {
            "url": "https://podcasts.apple.com/us/podcast/the-startup-ideas-podcast/id1593424985?i=1000716529591",
            "task": "Extract startup ideas from podcast and identify revenue opportunities for puzzle book business"
        },
        {
            "url": "https://github.com/cvs-health/uqlm",
            "task": "Analyze CVS Health UQLM repository and extract applicable patterns for our system"
        },
        {
            "url": "https://hamel.dev/blog/posts/evals-faq/",
            "task": "Study LLM evaluation best practices and implement evaluation framework for our AI agents"
        },
        {
            "url": "https://share.snipd.com/episode/0da1c24c-0b54-4109-be93-717a98ca93d2",
            "task": "Analyze Snipd episode content and extract actionable business insights"
        },
        {
            "url": "https://music.youtube.com/watch?v=vbWQrV5pgzg",
            "task": "Research YouTube content strategy and create viral content templates"
        },
        {
            "url": "https://share.snipd.com/episode/080c41dc-1a6a-4c8e-b936-8f06f17cd014",
            "task": "Extract insights from second Snipd episode for revenue optimization"
        },
        {
            "url": "https://ai.pydantic.dev/",
            "task": "Integrate Pydantic AI framework for better type safety and validation in our system"
        },
        {
            "url": "https://share.snipd.com/episode/b706c6ce-85f8-44b5-b97c-13de59d37b1e",
            "task": "Analyze third Snipd episode for business growth strategies and automation insights"
        },
        {
            "url": "https://share.snipd.com/episode/36314ebe-fe06-4209-9c92-49b6ec30924c",
            "task": "Extract insights from fourth Snipd episode for scaling and optimization strategies"
        },
        {
            "url": "https://share.snipd.com/episode/93f9c717-ec18-4590-9958-def02c4aaec7",
            "task": "Research fifth Snipd episode for advanced monetization and passive income strategies"
        }
    ]
    
    # Spawn agents for each task
    agent_ids = []
    
    print(f"\n🚀 Spawning {len(research_tasks)} research agents...\n")
    
    for i, task_info in enumerate(research_tasks, 1):
        task = f"{task_info['task']} (URL: {task_info['url']})"
        print(f"{i}. Spawning agent for: {task_info['url']}")
        
        agent_id = orchestrator.spawn_agent(task)
        agent_ids.append(agent_id)
        
        print(f"   ✓ Agent {agent_id} spawned")
        time.sleep(1)  # Small delay between spawns
    
    print(f"\n⏳ {len(agent_ids)} agents working in parallel...")
    print("\nAgents are:")
    print("- Creating their own worktrees")
    print("- Researching assigned resources")
    print("- Implementing findings")
    print("- Updating documentation")
    print("- Creating pull requests")
    
    # Wait for all agents to complete
    print("\n⌛ Waiting for agents to complete (timeout: 10 minutes)...")
    orchestrator.wait_for_agents(agent_ids, timeout=600)
    
    # Summary
    print("\n📊 Final Status Summary:")
    print("=" * 60)
    
    all_status = orchestrator.get_all_status()
    
    completed = 0
    failed = 0
    pr_created = 0
    
    for agent_id, status in all_status.items():
        print(f"\nAgent {agent_id}:")
        print(f"  Task: {status['task'][:60]}...")
        print(f"  Status: {status['status']}")
        print(f"  Branch: {status['branch']}")
        
        if status['status'] == 'pr_created':
            pr_created += 1
            completed += 1
        elif status['status'] == 'completed':
            completed += 1
        elif status['status'] in ['failed', 'pr_failed']:
            failed += 1
    
    print(f"\n✅ Summary:")
    print(f"  - Total agents: {len(agent_ids)}")
    print(f"  - Completed: {completed}")
    print(f"  - PRs created: {pr_created}")
    print(f"  - Failed: {failed}")
    
    print("\n📝 Next Steps:")
    print("1. Review pull requests on GitHub")
    print("2. Check docs/ folder for agent research")
    print("3. Review plan.md for progress tracking")
    print("4. Merge valuable findings into main branch")
    
    print("\n🎉 Research agent spawning complete!")

if __name__ == "__main__":
    main()