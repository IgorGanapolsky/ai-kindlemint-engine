#!/usr/bin/env python3
"""
Enhanced Multi-Agent Orchestrator with Communication and Shared Knowledge
Adds A2A-lite features to our worktree-based system
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid
from queue import PriorityQueue
import threading
import time

from multi_agent_orchestrator import MultiAgentOrchestrator, WorktreeAgent

class EnhancedWorkTreeAgent(WorktreeAgent):
    """Enhanced agent with communication and learning capabilities"""
    
    def __init__(self, agent_id: str, task: str, branch_name: str, capabilities: List[str] = None):
        super().__init__(agent_id, task, branch_name)
        self.capabilities = capabilities or ["general"]
        self.message_inbox = Path(f"agent_messages/inbox_{agent_id}")
        self.message_inbox.mkdir(parents=True, exist_ok=True)
        self.learnings = []
        
    def send_message(self, to_agent_id: str, message: Dict[str, Any]):
        """Send message to another agent"""
        msg_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        full_message = {
            "id": msg_id,
            "from": self.agent_id,
            "to": to_agent_id,
            "timestamp": timestamp,
            "message": message
        }
        
        # Write to recipient's inbox
        recipient_inbox = Path(f"agent_messages/inbox_{to_agent_id}")
        recipient_inbox.mkdir(parents=True, exist_ok=True)
        
        msg_file = recipient_inbox / f"msg_{msg_id}.json"
        with open(msg_file, 'w') as f:
            json.dump(full_message, f, indent=2)
        
        self.log_progress(f"Sent message to agent {to_agent_id}: {message.get('type', 'general')}")
        
    def check_messages(self) -> List[Dict]:
        """Check inbox for new messages"""
        messages = []
        
        for msg_file in self.message_inbox.glob("msg_*.json"):
            with open(msg_file) as f:
                message = json.load(f)
            messages.append(message)
            
            # Mark as read by moving to processed
            processed_dir = self.message_inbox / "processed"
            processed_dir.mkdir(exist_ok=True)
            msg_file.rename(processed_dir / msg_file.name)
        
        return messages
    
    def share_learning(self, insight: Dict[str, Any]):
        """Share learning with the collective knowledge base"""
        learning = {
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "task": self.task,
            "insight": insight,
            "confidence": insight.get("confidence", 0.5)
        }
        
        # Add to agent's learnings
        self.learnings.append(learning)
        
        # Write to shared knowledge base
        kb_dir = Path("shared_knowledge")
        kb_dir.mkdir(exist_ok=True)
        
        kb_file = kb_dir / f"learning_{self.agent_id}_{len(self.learnings)}.json"
        with open(kb_file, 'w') as f:
            json.dump(learning, f, indent=2)
        
        self.log_progress(f"Shared learning: {insight.get('type', 'general')}")
        
    def query_collective_knowledge(self, query: str) -> List[Dict]:
        """Query the collective knowledge base"""
        kb_dir = Path("shared_knowledge")
        if not kb_dir.exists():
            return []
        
        relevant_learnings = []
        
        # Simple keyword matching (in production, use vector similarity)
        query_terms = query.lower().split()
        
        for kb_file in kb_dir.glob("learning_*.json"):
            with open(kb_file) as f:
                learning = json.load(f)
            
            # Check if learning is relevant
            insight_text = json.dumps(learning["insight"]).lower()
            if any(term in insight_text for term in query_terms):
                relevant_learnings.append(learning)
        
        # Sort by confidence
        relevant_learnings.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return relevant_learnings[:5]  # Top 5 results
    
    def execute_enhanced_task(self):
        """Execute task with communication and learning"""
        self.status = "working"
        self.log_progress(f"Starting enhanced task: {self.task}")
        
        # Check for relevant prior knowledge
        prior_knowledge = self.query_collective_knowledge(self.task)
        if prior_knowledge:
            self.log_progress(f"Found {len(prior_knowledge)} relevant prior learnings")
            
            # Use prior knowledge to inform approach
            for knowledge in prior_knowledge:
                self.log_progress(f"Applying insight from agent {knowledge['agent_id']}")
        
        # Simulate task execution
        time.sleep(2)
        
        # Check messages during execution
        messages = self.check_messages()
        for msg in messages:
            self.log_progress(f"Received message from {msg['from']}: {msg['message'].get('type', 'general')}")
            
            # Respond if needed
            if msg['message'].get('type') == 'assistance_request':
                self.send_message(msg['from'], {
                    "type": "assistance_response",
                    "data": "Here's my insight on that..."
                })
        
        # Generate insights from task
        if "revenue" in self.task.lower():
            self.share_learning({
                "type": "revenue_optimization",
                "strategy": "Dynamic pricing increased conversion by 23%",
                "confidence": 0.85,
                "applicable_to": ["pricing", "conversion", "optimization"]
            })
        elif "traffic" in self.task.lower():
            self.share_learning({
                "type": "traffic_generation",
                "strategy": "Morning posts get 3x engagement",
                "confidence": 0.92,
                "applicable_to": ["posting_schedule", "engagement", "timing"]
            })
        
        # Complete task
        self.create_enhanced_implementation()
        
        self.status = "completed"
        self.log_progress("Enhanced task completed with learning shared")
    
    def create_enhanced_implementation(self):
        """Create implementation with collective knowledge integration"""
        script_path = self.worktree_path / "scripts" / f"enhanced_{self.agent_id}.py"
        script_path.parent.mkdir(exist_ok=True)
        
        # Get relevant knowledge
        knowledge = self.query_collective_knowledge("revenue optimization")
        
        script_content = f'''#!/usr/bin/env python3
"""
Enhanced Implementation by Agent {self.agent_id}
Task: {self.task}
Capabilities: {', '.join(self.capabilities)}

Integrated Knowledge:
{json.dumps([k['insight'] for k in knowledge[:3]], indent=2)}
"""

class EnhancedSolution:
    def __init__(self):
        self.agent_id = "{self.agent_id}"
        self.capabilities = {self.capabilities}
        
    def execute(self):
        """Execute with collective intelligence"""
        print(f"Agent {self.agent_id} executing with enhanced capabilities")
        
        # Apply learnings from other agents
        optimizations = {json.dumps(knowledge[:2], indent=8)}
        
        for optimization in optimizations:
            self.apply_optimization(optimization)
    
    def apply_optimization(self, optimization):
        """Apply learned optimization"""
        print(f"Applying: {{optimization}}")
        
    def collaborate_with_agents(self, agent_ids):
        """Collaborate with other specialists"""
        # Inter-agent collaboration logic
        pass

if __name__ == "__main__":
    solution = EnhancedSolution()
    solution.execute()
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        self.log_progress("Created enhanced implementation with collective knowledge")

class TaskQueue:
    """Dynamic task queue for agent coordination"""
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.claimed_tasks = {}
        self.completed_tasks = []
        
    def add_task(self, task: str, priority: int = 5, required_capabilities: List[str] = None):
        """Add task to queue with priority"""
        task_id = str(uuid.uuid4())[:8]
        task_item = {
            "id": task_id,
            "task": task,
            "priority": priority,
            "required_capabilities": required_capabilities or ["general"],
            "added_at": datetime.now().isoformat()
        }
        
        # Lower number = higher priority
        self.queue.put((priority, task_id, task_item))
        return task_id
    
    def claim_task(self, agent_id: str, agent_capabilities: List[str]) -> Optional[Dict]:
        """Agent claims a suitable task"""
        # Try to find a task matching agent capabilities
        temp_queue = []
        claimed_task = None
        
        while not self.queue.empty():
            priority, task_id, task_item = self.queue.get()
            
            # Check if agent has required capabilities
            required = set(task_item["required_capabilities"])
            agent_caps = set(agent_capabilities)
            
            if required.intersection(agent_caps) and task_id not in self.claimed_tasks:
                # Agent can do this task
                claimed_task = task_item
                self.claimed_tasks[task_id] = {
                    "agent_id": agent_id,
                    "claimed_at": datetime.now().isoformat()
                }
                break
            else:
                # Put back in queue
                temp_queue.append((priority, task_id, task_item))
        
        # Restore unclaimed tasks
        for item in temp_queue:
            self.queue.put(item)
        
        return claimed_task
    
    def complete_task(self, task_id: str, agent_id: str, results: Dict):
        """Mark task as completed"""
        if task_id in self.claimed_tasks and self.claimed_tasks[task_id]["agent_id"] == agent_id:
            self.completed_tasks.append({
                "task_id": task_id,
                "agent_id": agent_id,
                "completed_at": datetime.now().isoformat(),
                "results": results
            })
            del self.claimed_tasks[task_id]
            return True
        return False

class EnhancedMultiAgentOrchestrator(MultiAgentOrchestrator):
    """Enhanced orchestrator with A2A-lite features"""
    
    def __init__(self):
        super().__init__()
        self.task_queue = TaskQueue()
        self.agent_registry = {}  # agent_id -> capabilities mapping
        self.performance_metrics = {}
        
        # Create directories
        Path("agent_messages").mkdir(exist_ok=True)
        Path("shared_knowledge").mkdir(exist_ok=True)
        Path("performance_metrics").mkdir(exist_ok=True)
    
    def spawn_enhanced_agent(self, task: str, capabilities: List[str] = None) -> str:
        """Spawn enhanced agent with capabilities"""
        agent_id = str(uuid.uuid4())[:8]
        branch_name = f"agent/{agent_id}/{task.lower().replace(' ', '-')[:30]}"
        
        agent = EnhancedWorkTreeAgent(agent_id, task, branch_name, capabilities)
        self.agents[agent_id] = agent
        self.agent_registry[agent_id] = capabilities or ["general"]
        
        # Start agent work
        thread = threading.Thread(target=self.run_enhanced_agent, args=(agent,))
        thread.start()
        
        self.log_orchestration(f"Spawned enhanced agent {agent_id} with capabilities: {capabilities}")
        
        return agent_id
    
    def run_enhanced_agent(self, agent: EnhancedWorkTreeAgent):
        """Run enhanced agent workflow"""
        try:
            # Setup worktree
            if not agent.setup_worktree():
                return
            
            # Execute enhanced task
            agent.execute_enhanced_task()
            
            # Record performance
            self.record_agent_performance(agent)
            
            # Commit changes
            agent.commit_changes()
            
            # Push branch
            agent.push_branch()
            
            # Create PR
            agent.create_pull_request()
            
            # Cleanup
            agent.cleanup_worktree()
            
        except Exception as e:
            agent.log_progress(f"Enhanced agent failed: {str(e)}")
            agent.status = "failed"
    
    def spawn_specialist_team(self, project: str, team_composition: Dict[str, List[str]]) -> List[str]:
        """Spawn a team of specialist agents"""
        agent_ids = []
        
        print(f"\n🚀 Spawning specialist team for: {project}")
        
        for role, capabilities in team_composition.items():
            task = f"{role} for {project}"
            agent_id = self.spawn_enhanced_agent(task, capabilities)
            agent_ids.append(agent_id)
            print(f"  • {role} agent {agent_id}: {', '.join(capabilities)}")
        
        # Enable team communication
        self.setup_team_communication(agent_ids)
        
        return agent_ids
    
    def setup_team_communication(self, team_agent_ids: List[str]):
        """Setup communication channels for a team"""
        team_config = {
            "team_id": str(uuid.uuid4())[:8],
            "members": team_agent_ids,
            "created_at": datetime.now().isoformat()
        }
        
        # Broadcast team membership
        for agent_id in team_agent_ids:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                
                # Notify about team members
                for other_id in team_agent_ids:
                    if other_id != agent_id:
                        agent.send_message(other_id, {
                            "type": "team_introduction",
                            "team_config": team_config,
                            "my_capabilities": self.agent_registry.get(agent_id, [])
                        })
    
    def record_agent_performance(self, agent: EnhancedWorkTreeAgent):
        """Record agent performance metrics"""
        metrics = {
            "agent_id": agent.agent_id,
            "task": agent.task,
            "capabilities": agent.capabilities,
            "start_time": agent.progress_log[0]["timestamp"] if agent.progress_log else None,
            "end_time": datetime.now().isoformat(),
            "status": agent.status,
            "learnings_shared": len(agent.learnings),
            "messages_sent": len([p for p in agent.progress_log if "Sent message" in p["message"]]),
            "knowledge_queries": len([p for p in agent.progress_log if "prior learnings" in p["message"]])
        }
        
        self.performance_metrics[agent.agent_id] = metrics
        
        # Save to file
        metrics_file = Path("performance_metrics") / f"agent_{agent.agent_id}.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def get_collective_intelligence_summary(self) -> Dict:
        """Get summary of collective knowledge and performance"""
        kb_dir = Path("shared_knowledge")
        
        summary = {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status == "working"]),
            "completed_tasks": len(self.task_queue.completed_tasks),
            "shared_learnings": len(list(kb_dir.glob("learning_*.json"))) if kb_dir.exists() else 0,
            "performance_summary": self._calculate_performance_summary(),
            "top_insights": self._get_top_insights()
        }
        
        return summary
    
    def _calculate_performance_summary(self) -> Dict:
        """Calculate overall performance metrics"""
        if not self.performance_metrics:
            return {}
        
        total_tasks = len(self.performance_metrics)
        successful = len([m for m in self.performance_metrics.values() if m["status"] == "completed"])
        
        return {
            "success_rate": successful / total_tasks if total_tasks > 0 else 0,
            "avg_learnings_per_agent": sum(m["learnings_shared"] for m in self.performance_metrics.values()) / total_tasks if total_tasks > 0 else 0,
            "total_knowledge_queries": sum(m["knowledge_queries"] for m in self.performance_metrics.values()),
            "inter_agent_messages": sum(m["messages_sent"] for m in self.performance_metrics.values())
        }
    
    def _get_top_insights(self, limit: int = 5) -> List[Dict]:
        """Get top insights from collective knowledge"""
        kb_dir = Path("shared_knowledge")
        if not kb_dir.exists():
            return []
        
        all_insights = []
        
        for kb_file in kb_dir.glob("learning_*.json"):
            with open(kb_file) as f:
                learning = json.load(f)
            all_insights.append(learning)
        
        # Sort by confidence
        all_insights.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return all_insights[:limit]

def demo_enhanced_system():
    """Demo the enhanced multi-agent system"""
    print("🚀 Enhanced Multi-Agent System Demo")
    print("=" * 50)
    
    orchestrator = EnhancedMultiAgentOrchestrator()
    
    # Add tasks to the queue
    print("\n📋 Adding tasks to dynamic queue...")
    
    tasks = [
        ("Optimize Reddit posting algorithm", 3, ["algorithm", "reddit", "optimization"]),
        ("Create viral Pinterest templates", 5, ["design", "pinterest", "viral"]),
        ("Build email automation system", 4, ["automation", "email", "backend"]),
        ("Implement A/B testing framework", 2, ["testing", "analytics", "framework"]),
        ("Research competitor strategies", 6, ["research", "analysis"])
    ]
    
    task_ids = []
    for task, priority, capabilities in tasks:
        task_id = orchestrator.task_queue.add_task(task, priority, capabilities)
        task_ids.append(task_id)
        print(f"  • Added: {task} (priority: {priority})")
    
    # Spawn specialist team
    print("\n👥 Spawning specialist team...")
    
    team_composition = {
        "Algorithm Specialist": ["algorithm", "optimization", "analytics"],
        "Content Creator": ["design", "viral", "pinterest", "reddit"],
        "Backend Engineer": ["backend", "automation", "framework"],
        "Research Analyst": ["research", "analysis", "strategy"]
    }
    
    team_ids = orchestrator.spawn_specialist_team("Revenue Optimization Project", team_composition)
    
    print(f"\n⏳ Team of {len(team_ids)} specialists working collaboratively...")
    
    # Wait for completion
    orchestrator.wait_for_agents(team_ids, timeout=300)
    
    # Get collective intelligence summary
    summary = orchestrator.get_collective_intelligence_summary()
    
    print("\n📊 Collective Intelligence Summary:")
    print(f"  • Total agents: {summary['total_agents']}")
    print(f"  • Completed tasks: {summary['completed_tasks']}")
    print(f"  • Shared learnings: {summary['shared_learnings']}")
    print(f"  • Success rate: {summary['performance_summary'].get('success_rate', 0)*100:.0f}%")
    
    print("\n💡 Top Insights:")
    for insight in summary['top_insights'][:3]:
        print(f"  • {insight['insight'].get('strategy', 'Unknown')} (confidence: {insight['confidence']*100:.0f}%)")
    
    print("\n✅ Enhanced multi-agent system demo complete!")

if __name__ == "__main__":
    demo_enhanced_system()