"""
Automation Coordinator Agent

This agent orchestrates the entire performance monitoring and business intelligence pipeline.
It coordinates between:
- KDP Performance Agent (book performance monitoring)
- Business Analytics Agent (business intelligence and reporting)
- Market Research Agent (competitive analysis and market research)

The coordinator schedules tasks, manages workflows, and ensures data flows between agents.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .agent_types import AgentCapability
from .base_agent import BaseAgent
from .task_system import Task, TaskResult, TaskStatus


class AutomationCoordinator(BaseAgent):
    """Central coordinator for performance monitoring and business intelligence"""

    def __init__(
        self,
        coordination_data_path: str = "books/coordination_data",
        workflow_config_path: str = "books/workflow_config.json",
    ):
        super().__init__(
            agent_type="automation_coordinator",
            capabilities=[
                AgentCapability.TASK_COORDINATION,
                AgentCapability.RESOURCE_MANAGEMENT,
                AgentCapability.BUSINESS_INTELLIGENCE,
                AgentCapability.PERFORMANCE_MONITORING,
            ],
            max_concurrent_tasks=10,
            heartbeat_interval=300,  # 5 minutes
        )

        self.coordination_data_path = Path(coordination_data_path)
        self.workflow_config_path = Path(workflow_config_path)

        # Workflow management
        self.active_workflows: Dict[str, Dict] = {}
        self.scheduled_tasks: List[Dict] = []
        self.workflow_history: List[Dict] = []

        # Agent coordination
        self.connected_agents: Dict[str, str] = {}  # agent_type -> agent_id
        self.agent_health: Dict[str, Dict] = {}

        # Performance tracking
        self.coordination_metrics: Dict[str, Any] = {
            "workflows_executed": 0,
            "workflows_failed": 0,
            "total_tasks_coordinated": 0,
            "average_workflow_time": 0.0,
        }

        # Create storage directory
        self.coordination_data_path.mkdir(parents=True, exist_ok=True)

    async def _initialize(self) -> None:
        """Initialize the automation coordinator"""
        self.logger.info("Initializing Automation Coordinator")

        # Load workflow configuration
        await self._load_workflow_config()

        # Load coordination data
        await self._load_coordination_data()

        # Start workflow scheduler
        asyncio.create_task(self._workflow_scheduler())

        # Start agent health monitoring
        asyncio.create_task(self._monitor_agent_health())

        # Start daily reporting workflow
        asyncio.create_task(self._daily_reporting_workflow())

        self.logger.info("Automation Coordinator initialized")

    async def _cleanup(self) -> None:
        """Cleanup coordination resources"""
        await self._save_coordination_data()

    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute coordination task"""
        try:
            task_type = task.task_data.get("type")

            if task_type == "execute_workflow":
                return await self._execute_workflow(task)
            elif task_type == "schedule_workflow":
                return await self._schedule_workflow(task)
            elif task_type == "monitor_book_performance":
                return await self._coordinate_book_performance_monitoring(task)
            elif task_type == "generate_business_report":
                return await self._coordinate_business_report_generation(task)
            elif task_type == "research_market":
                return await self._coordinate_market_research(task)
            elif task_type == "comprehensive_analysis":
                return await self._execute_comprehensive_analysis(task)
            else:
                return TaskResult(
                    success=False, error=f"Unknown coordination task type: {task_type}"
                )

        except Exception as e:
            self.logger.error(f"Coordination task execution failed: {e}")
            return TaskResult(success=False, error=str(e))

    async def _execute_comprehensive_analysis(self, task: Task) -> TaskResult:
        """Execute comprehensive analysis workflow across all agents"""
        workflow_id = f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            self.logger.info(
                f"Starting comprehensive analysis workflow: {workflow_id}")

            workflow_results = {
                "workflow_id": workflow_id,
                "started_at": datetime.now().isoformat(),
                "tasks_executed": [],
                "results": {},
            }

            # Phase 1: Book Performance Monitoring
            self.logger.info("Phase 1: Book Performance Monitoring")
            performance_task = Task(
                task_type="monitor_all_books",
                task_data={"type": "monitor_book",
                           "scope": "all_active_books"},
                required_capabilities=[AgentCapability.PERFORMANCE_MONITORING],
            )

            performance_result = await self._delegate_task_to_agent(
                "kdp_performance_monitor", performance_task
            )
            workflow_results["tasks_executed"].append(
                "book_performance_monitoring")
            workflow_results["results"]["performance_monitoring"] = performance_result

            # Phase 2: Market Research
            self.logger.info("Phase 2: Market Research")

            # Get active book niches for research
            active_niches = await self._get_active_book_niches()

            for niche in active_niches[:3]:  # Limit to top 3 niches
                research_task = Task(
                    task_type="research_niche",
                    task_data={
                        "type": "research_niche",
                        "niche": niche,
                        "depth": "standard",
                    },
                    required_capabilities=[AgentCapability.MARKET_RESEARCH],
                )

                research_result = await self._delegate_task_to_agent(
                    "market_research", research_task
                )
                workflow_results["tasks_executed"].append(
                    f"market_research_{niche}")
                workflow_results["results"][
                    f"market_research_{niche}"
                ] = research_result

                # Delay between research tasks
                await asyncio.sleep(10)

            # Phase 3: Business Analytics
            self.logger.info("Phase 3: Business Intelligence Analysis")
            analytics_task = Task(
                task_type="generate_business_report",
                task_data={
                    "type": "generate_business_report",
                    "report_type": "comprehensive",
                    "time_period": "30d",
                },
                required_capabilities=[AgentCapability.BUSINESS_INTELLIGENCE],
            )

            analytics_result = await self._delegate_task_to_agent(
                "business_analytics", analytics_task
            )
            workflow_results["tasks_executed"].append("business_analytics")
            workflow_results["results"]["business_analytics"] = analytics_result

            # Phase 4: Generate Comprehensive Summary
            self.logger.info("Phase 4: Generating Comprehensive Summary")
            summary = await self._generate_workflow_summary(workflow_results)
            workflow_results["comprehensive_summary"] = summary

            workflow_results["completed_at"] = datetime.now().isoformat()
            workflow_results["success"] = True

            # Save workflow results
            results_file = self.coordination_data_path / \
                f"{workflow_id}_results.json"
            with open(results_file, "w") as f:
                json.dump(workflow_results, f, indent=2)

            # Update coordination metrics
            self.coordination_metrics["workflows_executed"] += 1
            self.coordination_metrics["total_tasks_coordinated"] += len(
                workflow_results["tasks_executed"]
            )

            self.logger.info(
                f"Comprehensive analysis workflow completed: {workflow_id}"
            )

            return TaskResult(
                success=True,
                data={
                    "workflow_id": workflow_id,
                    "results": workflow_results,
                    "results_file": str(results_file),
                },
            )

        except Exception as e:
            self.logger.error(f"Comprehensive analysis workflow failed: {e}")
            self.coordination_metrics["workflows_failed"] += 1
            return TaskResult(success=False, error=str(e))

    async def _delegate_task_to_agent(
        self, agent_type: str, task: Task
    ) -> Dict[str, Any]:
        """Delegate a task to a specific agent type"""
        try:
            # This is a placeholder for actual agent delegation
            # In a real implementation, this would use the agent registry
            # to find and delegate to the appropriate agent

            self.logger.info(
                f"Delegating task to {agent_type}: {task.task_type}")

            # Simulate task execution (placeholder)
            await asyncio.sleep(2)

            return {
                "agent_type": agent_type,
                "task_type": task.task_type,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "simulated": True,
                "message": f"Task delegated to {agent_type} - actual implementation would use agent registry",
            }

        except Exception as e:
            self.logger.error(f"Task delegation failed for {agent_type}: {e}")
            return {
                "agent_type": agent_type,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _get_active_book_niches(self) -> List[str]:
        """Get list of active book niches for research"""
        try:
            # Load active books data
            performance_data_path = Path("books/performance_data")
            active_books_file = performance_data_path / "active_books.json"

            if active_books_file.exists():
                with open(active_books_file, "r") as f:
                    active_books = json.load(f)

                # Extract unique series/niches
                niches = set()
                for book_data in active_books.values():
                    series = book_data.get("series", "")
                    if series:
                        # Convert series name to niche
                        niche = self._series_to_niche(series)
                        niches.add(niche)

                return list(niches)
            else:
                # Default niches if no active books data
                return ["crossword puzzles", "sudoku puzzles", "brain games"]

        except Exception as e:
            self.logger.error(f"Error getting active niches: {e}")
            return ["puzzle books", "brain training", "adult activity books"]

    def _series_to_niche(self, series_name: str) -> str:
        """Convert series name to market research niche"""
        niche_mapping = {
            "Large_Print_Crossword_Masters": "large print crossword puzzles",
            "Large_Print_Sudoku_Masters": "large print sudoku puzzles",
            "Crossword_Masters": "crossword puzzles",
            "Sudoku_Masters": "sudoku puzzles",
        }

        return niche_mapping.get(series_name, series_name.lower().replace("_", " "))

    async def _generate_workflow_summary(
        self, workflow_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive summary of workflow results"""
        summary = {
            "workflow_overview": {
                "workflow_id": workflow_results["workflow_id"],
                "total_tasks": len(workflow_results["tasks_executed"]),
                "execution_time": self._calculate_execution_time(
                    workflow_results["started_at"], workflow_results.get(
                        "completed_at")
                ),
                "success_rate": self._calculate_task_success_rate(
                    workflow_results["results"]
                ),
            },
            "key_findings": [],
            "recommendations": [],
            "action_items": [],
        }

        # Analyze performance monitoring results
        if "performance_monitoring" in workflow_results["results"]:
            summary["key_findings"].append(
                "Book performance monitoring completed")

        # Analyze market research results
        market_research_count = sum(
            1
            for key in workflow_results["results"].keys()
            if key.startswith("market_research_")
        )
        if market_research_count > 0:
            summary["key_findings"].append(
                f"Market research completed for {market_research_count} niches"
            )

        # Analyze business analytics results
        if "business_analytics" in workflow_results["results"]:
            summary["key_findings"].append(
                "Business intelligence analysis completed")

        # Generate recommendations
        summary["recommendations"] = [
            "Review individual agent reports for detailed insights",
            "Monitor performance trends over time",
            "Consider expanding successful niches",
            "Address any identified market gaps",
        ]

        # Generate action items
        summary["action_items"] = [
            "Schedule follow-up analysis in 7 days",
            "Update book metadata based on market research",
            "Optimize pricing based on competitive analysis",
            "Plan new book releases for identified opportunities",
        ]

        return summary

    def _calculate_execution_time(
        self, start_time: str, end_time: Optional[str]
    ) -> float:
        """Calculate workflow execution time in seconds"""
        if not end_time:
            return 0.0

        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return (end - start).total_seconds()
        except:
            return 0.0

    def _calculate_task_success_rate(self, results: Dict[str, Any]) -> float:
        """Calculate success rate of tasks in workflow"""
        if not results:
            return 0.0

        successful_tasks = sum(
            1 for result in results.values() if result.get("status") == "completed"
        )
        return (successful_tasks / len(results)) * 100

    async def _coordinate_book_performance_monitoring(self, task: Task) -> TaskResult:
        """Coordinate book performance monitoring across all books"""
        try:
            # Get list of books to monitor
            books_to_monitor = await self._get_books_for_monitoring()

            monitoring_results = {
                "started_at": datetime.now().isoformat(),
                "books_monitored": [],
                "monitoring_summary": {},
            }

            # Monitor each book
            for book_id, book_info in books_to_monitor.items():
                if book_info.get("asin"):
                    monitor_task = Task(
                        task_type="monitor_book",
                        task_data={
                            "type": "monitor_book",
                            "book_id": book_id,
                            "asin": book_info["asin"],
                        },
                        required_capabilities=[
                            AgentCapability.PERFORMANCE_MONITORING],
                    )

                    result = await self._delegate_task_to_agent(
                        "kdp_performance_monitor", monitor_task
                    )
                    monitoring_results["books_monitored"].append(
                        {"book_id": book_id, "result": result}
                    )

                    # Rate limiting
                    await asyncio.sleep(5)

            monitoring_results["completed_at"] = datetime.now().isoformat()
            monitoring_results["monitoring_summary"] = {
                "total_books": len(books_to_monitor),
                "successfully_monitored": sum(
                    1
                    for book in monitoring_results["books_monitored"]
                    if book["result"].get("status") == "completed"
                ),
            }

            return TaskResult(success=True, data=monitoring_results)

        except Exception as e:
            return TaskResult(success=False, error=str(e))

    async def _get_books_for_monitoring(self) -> Dict[str, Dict]:
        """Get list of books that need performance monitoring"""
        try:
            performance_data_path = Path("books/performance_data")
            active_books_file = performance_data_path / "active_books.json"

            if active_books_file.exists():
                with open(active_books_file, "r") as f:
                    return json.load(f)
            else:
                return {}

        except Exception as e:
            self.logger.error(f"Error loading books for monitoring: {e}")
            return {}

    async def _workflow_scheduler(self) -> None:
        """Background workflow scheduler"""
        while self.status.value != "shutdown":
            try:
                # Check for scheduled workflows
                current_time = datetime.now()

                # Daily comprehensive analysis at 2 AM
                if current_time.hour == 2 and current_time.minute < 10:
                    await self._schedule_daily_comprehensive_analysis()

                # Weekly market research on Sundays at 3 AM
                if current_time.weekday() == 6 and current_time.hour == 3:
                    await self._schedule_weekly_market_research()

                # Hourly performance monitoring
                if current_time.minute < 10:
                    await self._schedule_performance_monitoring()

                # Wait 10 minutes before next check
                await asyncio.sleep(600)

            except Exception as e:
                self.logger.error(f"Error in workflow scheduler: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _schedule_daily_comprehensive_analysis(self) -> None:
        """Schedule daily comprehensive analysis"""
        task = Task(
            task_type="comprehensive_analysis",
            task_data={"type": "comprehensive_analysis",
                       "scope": "daily_report"},
            required_capabilities=[AgentCapability.TASK_COORDINATION],
        )

        await self._process_task(task)

    async def _schedule_weekly_market_research(self) -> None:
        """Schedule weekly market research"""
        niches = await self._get_active_book_niches()

        for niche in niches:
            research_task = Task(
                task_type="research_market",
                task_data={"type": "research_niche",
                           "niche": niche, "depth": "deep"},
                required_capabilities=[AgentCapability.MARKET_RESEARCH],
            )

            await self._delegate_task_to_agent("market_research", research_task)
            await asyncio.sleep(300)  # 5 minutes between research tasks

    async def _schedule_performance_monitoring(self) -> None:
        """Schedule regular performance monitoring"""
        monitoring_task = Task(
            task_type="monitor_book_performance",
            task_data={"type": "monitor_book_performance",
                       "scope": "all_active"},
            required_capabilities=[AgentCapability.PERFORMANCE_MONITORING],
        )

        await self._process_task(monitoring_task)

    async def _daily_reporting_workflow(self) -> None:
        """Daily reporting workflow"""
        while self.status.value != "shutdown":
            try:
                # Generate daily summary at end of day
                current_time = datetime.now()
                if current_time.hour == 23:  # 11 PM
                    await self._generate_daily_summary()

                # Wait 1 hour
                await asyncio.sleep(3600)

            except Exception as e:
                self.logger.error(f"Error in daily reporting workflow: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error

    async def _generate_daily_summary(self) -> None:
        """Generate daily coordination summary"""
        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "coordination_metrics": self.coordination_metrics.copy(),
            "active_workflows": len(self.active_workflows),
            "agent_health_status": self.agent_health.copy(),
            "scheduled_tasks": len(self.scheduled_tasks),
        }

        # Save daily summary
        summary_file = (
            self.coordination_data_path
            / f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        self.logger.info(
            f"Generated daily coordination summary: {summary_file}")

    async def _monitor_agent_health(self) -> None:
        """Monitor health of connected agents"""
        while self.status.value != "shutdown":
            try:
                # Check agent health (placeholder)
                # In real implementation, this would check actual agent status
                self.agent_health = {
                    "kdp_performance_monitor": {
                        "status": "healthy",
                        "last_check": datetime.now().isoformat(),
                    },
                    "business_analytics": {
                        "status": "healthy",
                        "last_check": datetime.now().isoformat(),
                    },
                    "market_research": {
                        "status": "healthy",
                        "last_check": datetime.now().isoformat(),
                    },
                }

                # Wait 5 minutes between health checks
                await asyncio.sleep(300)

            except Exception as e:
                self.logger.error(f"Error in agent health monitoring: {e}")
                await asyncio.sleep(60)

    async def _load_workflow_config(self) -> None:
        """Load workflow configuration"""
        if self.workflow_config_path.exists():
            try:
                with open(self.workflow_config_path, "r") as f:
                    config = json.load(f)

                self.workflow_config = config
                self.logger.info("Loaded workflow configuration")

            except Exception as e:
                self.logger.error(f"Error loading workflow config: {e}")
                self._create_default_workflow_config()
        else:
            self._create_default_workflow_config()

    def _create_default_workflow_config(self) -> None:
        """Create default workflow configuration"""
        default_config = {
            "workflows": {
                "comprehensive_analysis": {
                    "schedule": "daily_2am",
                    "enabled": True,
                    "timeout_minutes": 60,
                },
                "performance_monitoring": {
                    "schedule": "hourly",
                    "enabled": True,
                    "timeout_minutes": 30,
                },
                "market_research": {
                    "schedule": "weekly_sunday_3am",
                    "enabled": True,
                    "timeout_minutes": 120,
                },
            },
            "agent_coordination": {
                "max_concurrent_tasks": 5,
                "task_timeout_minutes": 30,
                "retry_attempts": 3,
            },
        }

        with open(self.workflow_config_path, "w") as f:
            json.dump(default_config, f, indent=2)

        self.workflow_config = default_config
        self.logger.info("Created default workflow configuration")

    async def _load_coordination_data(self) -> None:
        """Load coordination data from storage"""
        try:
            # Load active workflows
            workflows_file = self.coordination_data_path / "active_workflows.json"
            if workflows_file.exists():
                with open(workflows_file, "r") as f:
                    self.active_workflows = json.load(f)

            # Load coordination metrics
            metrics_file = self.coordination_data_path / "coordination_metrics.json"
            if metrics_file.exists():
                with open(metrics_file, "r") as f:
                    saved_metrics = json.load(f)
                    self.coordination_metrics.update(saved_metrics)

            self.logger.info("Loaded coordination data")

        except Exception as e:
            self.logger.error(f"Error loading coordination data: {e}")

    async def _save_coordination_data(self) -> None:
        """Save coordination data to storage"""
        try:
            # Save active workflows
            workflows_file = self.coordination_data_path / "active_workflows.json"
            with open(workflows_file, "w") as f:
                json.dump(self.active_workflows, f, indent=2)

            # Save coordination metrics
            metrics_file = self.coordination_data_path / "coordination_metrics.json"
            with open(metrics_file, "w") as f:
                json.dump(self.coordination_metrics, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving coordination data: {e}")

    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status"""
        return {
            "coordinator_id": self.agent_id,
            "active_workflows": len(self.active_workflows),
            "scheduled_tasks": len(self.scheduled_tasks),
            "coordination_metrics": self.coordination_metrics.copy(),
            "agent_health": self.agent_health.copy(),
            "last_updated": datetime.now().isoformat(),
        }
