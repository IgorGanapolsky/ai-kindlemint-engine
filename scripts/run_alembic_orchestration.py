#!/usr/bin/env python3
"""
Run Alembic Causal AI Orchestration

This script integrates the Alembic system into your daily autonomous workflow.
It can be run manually or added to your existing orchestration schedule.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.orchestration.alembic_orchestrator import AlembicOrchestrator
from scripts.orchestration.autonomous_worktree_manager import AutonomousWorktreeManager


async def run_alembic_with_worktrees():
    """Run Alembic orchestration integrated with worktree system"""
    
    print("🧪 Starting Alembic Causal AI System...")
    print("=" * 50)
    
    # Initialize systems
    worktree_manager = AutonomousWorktreeManager()
    alembic = AlembicOrchestrator()
    
    # Ensure worktree infrastructure is ready
    print("📦 Initializing worktree infrastructure...")
    await worktree_manager.initialize_worktree_infrastructure()
    
    # Run different Alembic components in parallel
    print("\n🚀 Launching Alembic components:")
    
    tasks = []
    
    # 1. Event Monitoring (10 minute cycle)
    print("  ⚡ Event monitoring system")
    event_task = asyncio.create_task(
        run_with_timeout(alembic._event_monitoring_loop(), 600)
    )
    tasks.append(event_task)
    
    # 2. Causal Analysis (run once)
    print("  🧪 Causal analysis engine")
    causal_task = asyncio.create_task(
        run_causal_analysis(alembic)
    )
    tasks.append(causal_task)
    
    # 3. Data Collection (run once)
    print("  🔐 Private data pipeline")
    data_task = asyncio.create_task(
        run_data_collection(alembic)
    )
    tasks.append(data_task)
    
    # 4. Decision Execution (5 minute cycle)
    print("  🎯 Decision execution engine")
    decision_task = asyncio.create_task(
        run_with_timeout(alembic._decision_execution_loop(), 300)
    )
    tasks.append(decision_task)
    
    # Wait for all tasks
    print("\n⏳ Running Alembic systems...")
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Report results
    print("\n📊 Alembic Execution Summary:")
    print("=" * 50)
    
    # Get insights
    insights = await alembic._generate_causal_insights()
    
    print(f"✅ Events processed: {insights['total_events_processed']}")
    print(f"✅ Actions triggered: {insights['total_actions_triggered']}")
    print(f"✅ Causal relationships: {insights.get('causal_relationships_discovered', 0)}")
    
    # Save insights
    await alembic._save_insights_report(insights)
    
    print("\n💡 Key Recommendations:")
    for i, rec in enumerate(insights.get('recommendations', [])[:3], 1):
        print(f"  {i}. {rec}")
    
    print("\n✨ Alembic orchestration complete!")
    
    return insights


async def run_with_timeout(coro, timeout_seconds):
    """Run a coroutine with timeout"""
    try:
        await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        # Expected - we run loops for limited time
        pass
    except Exception as e:
        print(f"Error in task: {e}")
        return str(e)


async def run_causal_analysis(alembic):
    """Run all causal analysis tasks"""
    try:
        await alembic._analyze_campaign_effectiveness()
        await alembic._analyze_price_elasticity()
        await alembic._analyze_series_impact()
        return "Causal analysis complete"
    except Exception as e:
        return f"Causal analysis error: {e}"


async def run_data_collection(alembic):
    """Run data collection tasks"""
    try:
        await alembic._collect_kdp_analytics()
        await alembic._collect_website_analytics()
        await alembic._process_reader_surveys()
        
        # Export for ML
        ml_data = alembic.data_pipeline.export_for_ml()
        await alembic._save_ml_training_data(ml_data)
        
        return "Data collection complete"
    except Exception as e:
        return f"Data collection error: {e}"


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Alembic Causal AI Orchestration")
    parser.add_argument("--continuous", action="store_true", 
                       help="Run continuously (for production)")
    parser.add_argument("--test", action="store_true",
                       help="Run in test mode with shorter cycles")
    
    args = parser.parse_args()
    
    if args.continuous:
        print("🔄 Running in continuous mode...")
        # This would run forever in production
        asyncio.run(AlembicOrchestrator().start())
    else:
        # Run once for testing/development
        asyncio.run(run_alembic_with_worktrees())


if __name__ == "__main__":
    main()