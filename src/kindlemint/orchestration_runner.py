"""
Orchestration Runner

This script initializes and runs the performance monitoring and business intelligence
orchestration system. It coordinates multiple agents to collect book performance data,
conduct market research, and generate business analytics.

Usage:
    python -m kindlemint.orchestration_runner

The system will:
1. Initialize all orchestration agents
2. Auto-discover books from the books directory
3. Start performance monitoring
4. Begin market research
5. Generate business intelligence reports
6. Coordinate workflows automatically
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import List, Optional

from .agents.automation_coordinator import AutomationCoordinator
from .agents.kdp_performance_agent import KDPPerformanceAgent
from .agents.business_analytics_agent import BusinessAnalyticsAgent
from .agents.market_research_agent import MarketResearchAgent
from .agents.task_system import Task
import uuid


class OrchestrationSystem:
    """Main orchestration system that manages all performance monitoring agents"""
    
    def __init__(self):
        self.logger = logging.getLogger("orchestration_system")
        self.agents: List = []
        self.coordinator: Optional[AutomationCoordinator] = None
        self.running = False
        
    async def initialize(self) -> None:
        """Initialize the orchestration system"""
        self.logger.info("Initializing KindleMint Orchestration System")
        
        try:
            # Initialize agents
            self.kdp_agent = KDPPerformanceAgent()
            self.analytics_agent = BusinessAnalyticsAgent()
            self.research_agent = MarketResearchAgent()
            self.coordinator = AutomationCoordinator()
            
            self.agents = [
                self.kdp_agent,
                self.analytics_agent, 
                self.research_agent,
                self.coordinator
            ]
            
            # Start all agents
            for agent in self.agents:
                await agent.start()
                self.logger.info(f"Started agent: {agent.agent_id}")
            
            self.logger.info("All orchestration agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestration system: {e}")
            raise

    async def run_initial_analysis(self) -> None:
        """Run initial comprehensive analysis"""
        self.logger.info("Running initial comprehensive analysis")
        
        try:
            # Create comprehensive analysis task
            analysis_task = Task(
                task_id=str(uuid.uuid4()),
                task_type="comprehensive_analysis",
                parameters={
                    "type": "comprehensive_analysis",
                    "scope": "initial_setup"
                }
            )
            
            # Execute through coordinator
            result = await self.coordinator._process_task(analysis_task)
            
            if result and result.status == TaskStatus.COMPLETED:
                self.logger.info("Initial comprehensive analysis completed successfully")
                self.logger.info(f"Analysis results: {result.output}")
            else:
                self.logger.error(f"Initial analysis failed: {result.error}")
                
        except Exception as e:
            self.logger.error(f"Error in initial analysis: {e}")

    async def run(self) -> None:
        """Run the orchestration system"""
        self.running = True
        self.logger.info("Starting KindleMint Orchestration System")
        
        try:
            # Run initial analysis
            await self.run_initial_analysis()
            
            # System is now running autonomously through agent workflows
            self.logger.info("Orchestration system is now running autonomously")
            self.logger.info("The following workflows are active:")
            self.logger.info("- Hourly book performance monitoring")
            self.logger.info("- Daily comprehensive analysis (2 AM)")
            self.logger.info("- Weekly market research (Sunday 3 AM)")
            self.logger.info("- Daily coordination summaries (11 PM)")
            
            # Keep the system running
            while self.running:
                # Print status every hour
                await asyncio.sleep(3600)
                await self._print_system_status()
                
        except Exception as e:
            self.logger.error(f"Error in orchestration system: {e}")
            raise

    async def _print_system_status(self) -> None:
        """Print current system status"""
        try:
            if self.coordinator:
                status = self.coordinator.get_coordination_status()
                self.logger.info(f"System Status - Active Workflows: {status['active_workflows']}, "
                               f"Tasks Coordinated: {status['coordination_metrics']['total_tasks_coordinated']}")
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")

    async def shutdown(self) -> None:
        """Gracefully shutdown the orchestration system"""
        self.logger.info("Shutting down KindleMint Orchestration System")
        self.running = False
        
        # Stop all agents
        for agent in self.agents:
            try:
                await agent.stop()
                self.logger.info(f"Stopped agent: {agent.agent_id}")
            except Exception as e:
                self.logger.error(f"Error stopping agent {agent.agent_id}: {e}")
        
        self.logger.info("Orchestration system shutdown complete")

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown")
            asyncio.create_task(self.shutdown())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('orchestration_system.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("main")
    logger.info("Starting KindleMint Performance Monitoring & Business Intelligence System")
    
    # Create and run orchestration system
    system = OrchestrationSystem()
    system.setup_signal_handlers()
    
    try:
        await system.initialize()
        await system.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Orchestration system error: {e}")
    finally:
        await system.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
        sys.exit(0)