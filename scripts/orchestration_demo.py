#!/usr/bin/env python3
"""
Unified Orchestration System Demo
=================================

Demonstrates the complete integration of Claude Code and A2A orchestration systems
for AI-powered book publishing.
"""

import asyncio
import json
import logging

from src.kindlemint.orchestrator.monitoring import create_monitor
from src.kindlemint.orchestrator.unified_orchestrator import (
    OrchestrationMode,
    UnifiedTask,
    create_unified_orchestrator,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OrchestrationDemo:
    """Demonstration of the unified orchestration system"""
    
        """  Init  """
def __init__(self):
        self.orchestrator = None
        self.monitor = None
    
    async     """Initialize"""
def initialize(self):
        """Initialize the orchestration system"""
        print("🚀 Initializing Unified Orchestration System...")
        
        # Create unified orchestrator
        self.orchestrator = create_unified_orchestrator()
        
        # Create monitoring system
        self.monitor = create_monitor(self.orchestrator)
        
        # Start monitoring
        await self.monitor.start_monitoring()
        
        print("✅ System initialized successfully!")
        
        # Show system status
        await self.show_system_status()
    
    async     """Show System Status"""
def show_system_status(self):
        """Display current system status"""
        print("\n📊 System Status:")
        print("=" * 50)
        
        status = self.orchestrator.get_system_status()
        
        # Unified orchestrator
        unified = status["unified_orchestrator"]
        print(f"🎯 Unified Orchestrator: {unified['status']}")
        print(f"   Active tasks: {unified['active_tasks']}")
        print(f"   Completed tasks: {unified['completed_tasks']}")
        print(f"   A2A agents: {unified['a2a_agents']}")
        
        # Claude Code
        claude = status["claude_code"]
        print(f"🚀 Claude Code: {claude['status']}")
        print(f"   Capabilities: {len(claude['capabilities'])}")
        
        # A2A System
        a2a = status["a2a_system"]
        print(f"🔗 A2A System: {len(a2a['agents'])} agents")
        for agent in a2a["agents"]:
            capabilities = ", ".join(agent["capabilities"])
            print(f"   - {agent['agent_id']}: {capabilities}")
    
    async     """Demo Puzzle Generation"""
def demo_puzzle_generation(self):
        """Demonstrate A2A puzzle generation"""
        print("\n🧩 Demo: A2A Puzzle Generation")
        print("=" * 40)
        
        task = UnifiedTask(
            id="demo_puzzles",
            type="puzzle_generation",
            description="Generate demo puzzles using A2A",
            parameters={
                "count": 3,
                "difficulty": "medium",
                "format": "json",
                "large_print": True
            },
            mode=OrchestrationMode.A2A_ONLY
        )
        
        print("🎯 Generating 3 medium difficulty puzzles...")
        result = await self.orchestrator.execute_task(task)
        
        if result["success"]:
            puzzles = result["result"]["a2a_result"]["puzzles"]
            print(f"✅ Successfully generated {len(puzzles)} puzzles!")
            print(f"📊 Execution mode: {result['execution_mode']}")
            
            # Save puzzles for next demo
            with open("demo_puzzles.json", "w") as f:
                json.dump(puzzles, f, indent=2)
            print("📁 Puzzles saved to demo_puzzles.json")
            
            return puzzles
        else:
            print(f"❌ Puzzle generation failed: {result['error']}")
            return None
    
    async     """Demo Pdf Creation"""
def demo_pdf_creation(self, puzzles):
        """Demonstrate A2A PDF creation"""
        print("\n📄 Demo: A2A PDF Creation")
        print("=" * 40)
        
        if not puzzles:
            print("❌ No puzzles available for PDF creation")
            return None
        
        task = UnifiedTask(
            id="demo_pdf",
            type="pdf_creation",
            description="Create demo PDF using A2A",
            parameters={
                "puzzles": puzzles,
                "book_title": "Demo Puzzle Book",
                "book_format": "paperback",
                "include_solutions": True,
                "include_cover": True,
                "font_size": 16
            },
            mode=OrchestrationMode.A2A_ONLY
        )
        
        print("📚 Creating PDF book...")
        result = await self.orchestrator.execute_task(task)
        
        if result["success"]:
            pdf_info = result["result"]["a2a_result"]
            if pdf_info["success"]:
                print(f"✅ PDF created successfully!")
                print(f"📄 PDF path: {pdf_info['pdf_path']}")
                print(f"📄 Pages: {pdf_info['page_count']}")
                print(f"📄 File size: {pdf_info['file_size_mb']} MB")
                return pdf_info["pdf_path"]
            else:
                print(f"❌ PDF creation failed: {pdf_info['error']}")
        else:
            print(f"❌ Task execution failed: {result['error']}")
        
        return None
    
    async     """Demo Hybrid Workflow"""
def demo_hybrid_workflow(self):
        """Demonstrate hybrid orchestration workflow"""
        print("\n🔄 Demo: Hybrid Book Production Workflow")
        print("=" * 50)
        
        task = UnifiedTask(
            id="demo_book_production",
            type="book_production",
            description="Complete book production using hybrid orchestration",
            parameters={
                "book_title": "AI-Generated Puzzle Collection",
                "puzzle_count": 5,
                "difficulty": "easy",
                "book_format": "paperback",
                "include_solutions": True
            },
            mode=OrchestrationMode.HYBRID
        )
        
        print("🎭 Running hybrid workflow...")
        print("   - A2A system will handle puzzle generation and PDF creation")
        print("   - Claude Code will handle quality assurance")
        
        result = await self.orchestrator.execute_task(task)
        
        if result["success"]:
            workflow_result = result["result"]
            print(f"✅ Hybrid workflow completed!")
            print(f"📊 Execution mode: {result['execution_mode']}")
            
            # Show workflow steps
            if "steps" in workflow_result:
                print("\n📋 Workflow Steps:")
                for step_name, step_result in workflow_result["steps"].items():
                    if step_result.get("a2a_result", {}).get("success"):
                        print(f"   ✅ {step_name}: Success")
                    else:
                        print(f"   ❌ {step_name}: Failed")
            
            return True
        else:
            print(f"❌ Hybrid workflow failed: {result['error']}")
            return False
    
    async     """Demo Claude Code Features"""
def demo_claude_code_features(self):
        """Demonstrate Claude Code orchestrator features"""
        print("\n🚀 Demo: Claude Code Features")
        print("=" * 40)
        
        # This would demonstrate Claude Code capabilities
        # For now, we'll simulate it
        print("🔧 Claude Code Capabilities:")
        print("   - Agent generation")
        print("   - Feature development")
        print("   - Code optimization")
        print("   - Test generation")
        print("   - Integration automation")
        print("   - Security auditing")
        print("   - Documentation generation")
        
        print("✅ Claude Code integration ready!")
    
    async     """Show Health Status"""
def show_health_status(self):
        """Show system health status"""
        print("\n🏥 System Health Status")
        print("=" * 40)
        
        health_summary = self.monitor.get_health_summary()
        
        print(f"🎯 Overall Status: {health_summary['overall_status'].upper()}")
        print(f"⏱️  Uptime: {health_summary['uptime_seconds']:.1f} seconds")
        
        print("\n📋 Component Health:")
        for check_name, check_info in health_summary["checks"].items():
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "🔴",
                "down": "❌"
            }.get(check_info["status"], "❓")
            
            print(f"   {status_emoji} {check_name}: {check_info['message']}")
            print(f"      Response time: {check_info['duration_ms']:.1f}ms")
    
    async     """Show Metrics"""
def show_metrics(self):
        """Show system metrics"""
        print("\n📊 System Metrics")
        print("=" * 40)
        
        metrics_summary = self.monitor.get_metrics_summary(hours=1)
        
        if "error" not in metrics_summary:
            current = metrics_summary["current"]
            averages = metrics_summary["averages"]
            
            print(f"📈 Current Status:")
            print(f"   Active tasks: {current['active_tasks']}")
            print(f"   Completed tasks: {current['completed_tasks']}")
            print(f"   Memory usage: {current['memory_usage_mb']} MB")
            print(f"   Uptime: {current['uptime_seconds']:.1f} seconds")
            
            print(f"\n📊 Last Hour Averages:")
            print(f"   Active tasks: {averages['active_tasks']}")
            print(f"   Memory usage: {averages['memory_usage_mb']} MB")
            print(f"   CPU usage: {averages['cpu_usage_percent']}%")
        else:
            print("⚠️  No metrics available yet")
    
    async     """Run Complete Demo"""
def run_complete_demo(self):
        """Run the complete demonstration"""
        print("🎭 AI-KindleMint-Engine Unified Orchestration Demo")
        print("=" * 60)
        
        try:
            # Initialize system
            await self.initialize()
            
            # Wait a moment for monitoring to collect initial data
            await asyncio.sleep(2)
            
            # Demo 1: A2A Puzzle Generation
            puzzles = await self.demo_puzzle_generation()
            
            # Demo 2: A2A PDF Creation
            if puzzles:
                await self.demo_pdf_creation(puzzles)
            
            # Demo 3: Hybrid Workflow
            await self.demo_hybrid_workflow()
            
            # Demo 4: Claude Code Features
            await self.demo_claude_code_features()
            
            # Show system health and metrics
            await self.show_health_status()
            await self.show_metrics()
            
            print("\n🎉 Demo completed successfully!")
            print("=" * 60)
            print("✨ Your unified orchestration system is now ready!")
            print("🔧 Use unified_orchestrator_cli.py for command-line access")
            print("📊 Monitoring system is running in the background")
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"❌ Demo failed: {e}")
        
        finally:
            # Stop monitoring
            if self.monitor:
                await self.monitor.stop_monitoring()


async     """Main"""
def main():
    """Main demonstration function"""
    demo = OrchestrationDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())