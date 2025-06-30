#!/usr/bin/env python3
"""
Multi-Agent System Demo for KindleMint Engine

This script demonstrates the new multi-agent architecture in action,
showing how specialized agents coordinate to generate books efficiently.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kindlemint.agents import (
    AgentRegistry,
    HealthMonitor,
    TaskCoordinator,
    create_book_generation_workflow,
    create_pdf_layout_task,
    create_puzzle_generation_task,
    create_qa_validation_task,
)
from kindlemint.agents.content_agents import (
    EPUBGeneratorAgent,
    PDFLayoutAgent,
    PuzzleGeneratorAgent,
    QualityAssuranceAgent,
)
from kindlemint.agents.task_system import TaskPriority


class MultiAgentBookGenerator:
    """
    Demonstrates the multi-agent book generation system
    """

    def __init__(self):
        """Initialize the multi-agent system"""
        # Core systems
        self.health_monitor = HealthMonitor(check_interval=30)
        self.agent_registry = AgentRegistry(self.health_monitor)
        self.task_coordinator = TaskCoordinator(self.agent_registry)

        # Agents
        self.agents = []

        # Metrics
        self.demo_metrics = {
            "start_time": None,
            "end_time": None,
            "books_processed": 0,
            "books_succeeded": 0,
            "books_failed": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "agent_performance": {},
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger("multi_agent_demo")

    async def start_system(self) -> None:
        """Start all system components"""
        self.logger.info("🚀 Starting Multi-Agent Book Generation System")

        # Start core systems
        await self.agent_registry.start()
        await self.task_coordinator.start()

        # Create and start agents
        await self._create_agents()
        await self._start_agents()

        # Register standard workflows
        await self._register_workflows()

        self.logger.info("✅ Multi-Agent system started successfully")

        # Display system status
        await self._display_system_status()

    async def stop_system(self) -> None:
        """Stop all system components"""
        self.logger.info("🛑 Stopping Multi-Agent system")

        # Stop agents
        for agent in self.agents:
            await agent.stop()

        # Stop core systems
        await self.task_coordinator.stop()
        await self.agent_registry.stop()

        self.logger.info("✅ Multi-Agent system stopped")

    async def generate_book_individual_tasks(self, book_config: Dict) -> bool:
        """
        Generate a book using individual task submission
        (Demonstrates fine-grained control)
        """
        self.logger.info(
            f"📚 Generating book with individual tasks: {book_config['title']}"
        )

        try:
            book_id = book_config.get("id", f"book_{datetime.now().strftime('%H%M%S')}")

            # Task 1: Generate puzzles
            puzzle_task = create_puzzle_generation_task(
                puzzle_type=book_config["puzzle_type"],
                count=book_config["puzzle_count"],
                difficulty=book_config.get("difficulty", "mixed"),
                theme=book_config.get("theme"),
                priority=TaskPriority.HIGH,
            )

            # Add book-specific context
            puzzle_task.input_data.update(
                {
                    "series_name": book_config.get("series_name", "Demo_Series"),
                    "volume": book_config.get("volume", 1),
                    "book_id": book_id,
                }
            )

            puzzle_task_id = await self.task_coordinator.submit_task(puzzle_task)
            self.logger.info(f"📝 Submitted puzzle generation task: {puzzle_task_id}")

            # Wait for puzzle generation to complete
            await self._wait_for_task_completion(puzzle_task_id, timeout=300)
            puzzle_result = await self.task_coordinator.get_task_result(puzzle_task_id)

            if not puzzle_result or not puzzle_result.success:
                self.logger.error("❌ Puzzle generation failed")
                return False

            # Task 2: Create PDF layout
            pdf_task = create_pdf_layout_task(
                title=book_config["title"],
                input_dir=puzzle_result.artifacts["puzzles_dir"],
                output_dir=puzzle_result.artifacts["puzzles_dir"].replace(
                    "/puzzles", "/paperback"
                ),
                author=book_config.get("author", "KindleMint Publishing"),
                priority=TaskPriority.HIGH,
            )

            pdf_task.input_data.update(
                {
                    "puzzle_type": book_config["puzzle_type"],
                    "book_id": book_id,
                }
            )

            pdf_task_id = await self.task_coordinator.submit_task(pdf_task)
            self.logger.info(f"📄 Submitted PDF layout task: {pdf_task_id}")

            # Wait for PDF creation to complete
            await self._wait_for_task_completion(pdf_task_id, timeout=300)
            pdf_result = await self.task_coordinator.get_task_result(pdf_task_id)

            if not pdf_result or not pdf_result.success:
                self.logger.error("❌ PDF layout failed")
                return False

            # Task 3: Run QA validation
            qa_task = create_qa_validation_task(
                file_path=pdf_result.artifacts["interior_pdf"],
                validation_type="comprehensive",
                priority=TaskPriority.HIGH,
            )

            qa_task.input_data.update(
                {
                    "puzzle_type": book_config["puzzle_type"],
                    "puzzles_dir": puzzle_result.artifacts["puzzles_dir"],
                    "book_id": book_id,
                }
            )

            qa_task_id = await self.task_coordinator.submit_task(qa_task)
            self.logger.info(f"✅ Submitted QA validation task: {qa_task_id}")

            # Wait for QA to complete
            await self._wait_for_task_completion(qa_task_id, timeout=180)
            qa_result = await self.task_coordinator.get_task_result(qa_task_id)

            if not qa_result or not qa_result.success:
                self.logger.error("❌ QA validation failed")
                return False

            # Display results
            self.logger.info("🎉 Book generation completed successfully!")
            self.logger.info(f"   📁 PDF: {pdf_result.artifacts['interior_pdf']}")
            self.logger.info(
                f"   🎯 QA Score: {qa_result.output_data['overall_score']}/100"
            )
            self.logger.info(
                f"   ✅ Publish Ready: {qa_result.output_data['publish_ready']}"
            )

            return True

        except Exception as e:
            self.logger.error(f"❌ Book generation failed: {e}")
            return False

    async def generate_book_workflow(self, book_config: Dict) -> bool:
        """
        Generate a book using workflow orchestration
        (Demonstrates high-level coordination)
        """
        self.logger.info(f"📚 Generating book with workflow: {book_config['title']}")

        try:
            # Execute the book generation workflow
            execution_id = await self.task_coordinator.execute_workflow(
                workflow_id="book_generation_standard", input_data=book_config
            )

            self.logger.info(f"🔄 Started workflow execution: {execution_id}")

            # Monitor workflow progress
            await self._monitor_workflow_progress(execution_id, timeout=600)

            # Get workflow result
            result = await self.task_coordinator.get_workflow_result(execution_id)

            if result:
                self.logger.info("🎉 Workflow completed successfully!")
                self.logger.info(f"   📊 Results: {len(result)} steps completed")
                return True
            else:
                self.logger.error("❌ Workflow execution failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {e}")
            return False

    async def run_performance_demo(self) -> None:
        """
        Run a performance demonstration with multiple books
        """
        self.logger.info("🏃 Starting Performance Demo - Processing Multiple Books")

        self.demo_metrics["start_time"] = datetime.now()

        # Define multiple books for parallel processing
        books = [
            {
                "id": "crossword_easy",
                "title": "Easy Crossword Puzzles",
                "puzzle_type": "crossword",
                "puzzle_count": 25,
                "difficulty": "easy",
                "theme": "animals",
                "author": "Multi-Agent Publishing",
            },
            {
                "id": "sudoku_medium",
                "title": "Medium Sudoku Challenge",
                "puzzle_type": "sudoku",
                "puzzle_count": 30,
                "difficulty": "medium",
                "author": "Multi-Agent Publishing",
            },
            {
                "id": "wordsearch_hard",
                "title": "Hard Word Search Collection",
                "puzzle_type": "word_search",
                "puzzle_count": 20,
                "difficulty": "hard",
                "theme": "science",
                "author": "Multi-Agent Publishing",
            },
        ]

        # Process books in parallel using individual tasks
        tasks = []
        for book in books:
            task = asyncio.create_task(self.generate_book_individual_tasks(book))
            tasks.append(task)

        # Wait for all books to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate metrics
        self.demo_metrics["end_time"] = datetime.now()
        self.demo_metrics["books_processed"] = len(books)
        self.demo_metrics["books_succeeded"] = sum(1 for r in results if r is True)
        self.demo_metrics["books_failed"] = (
            len(books) - self.demo_metrics["books_succeeded"]
        )

        # Display performance summary
        await self._display_performance_summary()

    async def _create_agents(self) -> None:
        """Create specialized agents"""
        # Create content creation agents
        puzzle_agent = PuzzleGeneratorAgent(
            agent_id="puzzle_generator_01",
            supported_puzzle_types=["crossword", "sudoku", "word_search"],
            max_concurrent_tasks=2,
        )

        pdf_agent = PDFLayoutAgent(agent_id="pdf_layout_01", max_concurrent_tasks=1)

        epub_agent = EPUBGeneratorAgent(
            agent_id="epub_generator_01", max_concurrent_tasks=2
        )

        qa_agent = QualityAssuranceAgent(
            agent_id="qa_validator_01", max_concurrent_tasks=3
        )

        self.agents = [puzzle_agent, pdf_agent, epub_agent, qa_agent]

        # Register agents with registry
        for agent in self.agents:
            await self.agent_registry.register_agent(
                agent_id=agent.agent_id,
                agent_type=agent.agent_type,
                capabilities=list(agent.capabilities),
                max_concurrent_tasks=agent.max_concurrent_tasks,
            )

    async def _start_agents(self) -> None:
        """Start all agents"""
        start_tasks = [agent.start() for agent in self.agents]
        await asyncio.gather(*start_tasks)

        # Link agents to registry for message routing
        for agent in self.agents:
            agent.agent_registry = self.agent_registry

    async def _register_workflows(self) -> None:
        """Register standard workflows"""
        book_workflow = create_book_generation_workflow()
        self.task_coordinator.register_workflow(book_workflow)

    async def _wait_for_task_completion(self, task_id: str, timeout: int = 300) -> None:
        """Wait for a task to complete"""
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            status = await self.task_coordinator.get_task_status(task_id)

            if status and status.value in ["completed", "failed", "cancelled"]:
                return

            await asyncio.sleep(2)

        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")

    async def _monitor_workflow_progress(
        self, execution_id: str, timeout: int = 600
    ) -> None:
        """Monitor workflow execution progress"""
        start_time = datetime.now()
        last_status = None

        while (datetime.now() - start_time).total_seconds() < timeout:
            status = await self.task_coordinator.get_workflow_status(execution_id)

            if status != last_status:
                self.logger.info(
                    f"   📋 Workflow status: {status.value if status else 'unknown'}"
                )
                last_status = status

            if status and status.value in ["completed", "failed", "cancelled"]:
                return

            await asyncio.sleep(5)

        raise TimeoutError(
            f"Workflow {execution_id} did not complete within {timeout} seconds"
        )

    async def _display_system_status(self) -> None:
        """Display current system status"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 MULTI-AGENT SYSTEM STATUS")
        self.logger.info("=" * 60)

        # Agent status
        agents_info = self.agent_registry.get_all_agents()
        self.logger.info(f"🤖 Active Agents: {len(agents_info)}")

        for agent_info in agents_info:
            if agent_info:
                capabilities = ", ".join(agent_info["capabilities"])
                self.logger.info(
                    f"   • {agent_info['agent_id']}: {agent_info['status']} "
                    f"({capabilities})"
                )

        # System metrics
        system_status = self.agent_registry.get_system_status()
        coordination_metrics = self.task_coordinator.get_coordination_metrics()

        self.logger.info(f"⚡ System Utilization: {system_status['utilization']:.1f}%")
        self.logger.info(f"📋 Active Tasks: {coordination_metrics['active_tasks']}")
        self.logger.info(
            f"✅ Completed Tasks: {coordination_metrics['completed_tasks']}"
        )
        self.logger.info("=" * 60)

    async def _display_performance_summary(self) -> None:
        """Display performance demonstration summary"""
        duration = (
            self.demo_metrics["end_time"] - self.demo_metrics["start_time"]
        ).total_seconds()

        self.logger.info("\n" + "=" * 60)
        self.logger.info("🏆 PERFORMANCE DEMO SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"📚 Books Processed: {self.demo_metrics['books_processed']}")
        self.logger.info(f"✅ Successful: {self.demo_metrics['books_succeeded']}")
        self.logger.info(f"❌ Failed: {self.demo_metrics['books_failed']}")
        self.logger.info(f"⏱️ Total Duration: {duration:.1f} seconds")
        self.logger.info(
            f"📈 Books per Minute: {(self.demo_metrics['books_processed'] / duration * 60):.1f}"
        )

        success_rate = (
            self.demo_metrics["books_succeeded"]
            / self.demo_metrics["books_processed"]
            * 100
        )
        self.logger.info(f"🎯 Success Rate: {success_rate:.1f}%")

        # Agent performance
        self.logger.info("\n🤖 Agent Performance:")
        coordination_metrics = self.task_coordinator.get_coordination_metrics()

        if coordination_metrics.get("task_metrics"):
            for agent_id, metrics in coordination_metrics["task_metrics"].items():
                self.logger.info(f"   • {agent_id}: {metrics}")

        self.logger.info("=" * 60)


async def main():
    """Main demo function"""
    print("🚀 KindleMint Multi-Agent System Demo")
    print("=" * 50)

    demo = MultiAgentBookGenerator()

    try:
        # Start the multi-agent system
        await demo.start_system()

        # Demo 1: Individual task submission
        print("\n📝 DEMO 1: Individual Task Coordination")
        print("-" * 40)

        sample_book = {
            "id": "demo_crossword",
            "title": "Demo Crossword Collection",
            "puzzle_type": "crossword",
            "puzzle_count": 10,
            "difficulty": "mixed",
            "theme": "technology",
            "author": "Multi-Agent Demo",
            "series_name": "Demo_Series",
            "volume": 1,
        }

        success = await demo.generate_book_individual_tasks(sample_book)
        print(f"Result: {'✅ Success' if success else '❌ Failed'}")

        # Demo 2: Performance test with multiple books
        print("\n🏃 DEMO 2: Performance Test - Multiple Books")
        print("-" * 40)

        await demo.run_performance_demo()

        # Final system status
        await demo._display_system_status()

    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Clean shutdown
        await demo.stop_system()
        print("\n👋 Demo completed")


if __name__ == "__main__":
    # Add required dependencies check
    try:
        pass
    except ImportError:
        print("❌ Missing required dependency: psutil")
        print("Install with: pip install psutil")
        sys.exit(1)

    # Run the demo
    asyncio.run(main())
