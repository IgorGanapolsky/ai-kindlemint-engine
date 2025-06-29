#!/usr/bin/env python3
"""
Multi-Agent Integration with Existing KindleMint Batch Processor

This script demonstrates how to integrate the new multi-agent architecture
with the existing batch processing system for backward compatibility
and gradual migration.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kindlemint.agents import (
    AgentRegistry,
    HealthMonitor,
    Task,
    TaskCoordinator,
    TaskPriority,
    TaskType,
)
from kindlemint.agents.content_agents import (
    EPUBGeneratorAgent,
    PDFLayoutAgent,
    PuzzleGeneratorAgent,
    QualityAssuranceAgent,
)


class MultiAgentBatchProcessor:
    """
    Enhanced batch processor using multi-agent architecture

    This class provides backward compatibility with the existing
    batch processor while leveraging the new multi-agent system
    for improved performance and scalability.
    """

    def __init__(self, enable_multi_agent: bool = True):
        """
        Initialize the enhanced batch processor

        Args:
            enable_multi_agent: Whether to use multi-agent system
        """
        self.enable_multi_agent = enable_multi_agent
        self.logger = logging.getLogger("multi_agent_batch")

        # Multi-agent components (only if enabled)
        if self.enable_multi_agent:
            self.health_monitor = HealthMonitor()
            self.agent_registry = AgentRegistry(self.health_monitor)
            self.task_coordinator = TaskCoordinator(self.agent_registry)
            self.agents = []
            self.system_started = False

        # Compatibility metrics
        self.batch_metrics = {
            "start_time": None,
            "books_processed": 0,
            "books_succeeded": 0,
            "books_failed": 0,
            "processing_mode": "multi_agent" if enable_multi_agent else "legacy",
            "performance_improvement": 0.0,
        }

    async def start_system(self) -> None:
        """Start the multi-agent system"""
        if not self.enable_multi_agent or self.system_started:
            return

        self.logger.info("🚀 Starting enhanced multi-agent batch processing system")

        # Start core components
        await self.agent_registry.start()
        await self.task_coordinator.start()

        # Create and register agents
        await self._setup_agents()

        self.system_started = True
        self.logger.info("✅ Multi-agent system ready for batch processing")

    async def stop_system(self) -> None:
        """Stop the multi-agent system"""
        if not self.enable_multi_agent or not self.system_started:
            return

        self.logger.info("🛑 Stopping multi-agent system")

        # Stop agents
        for agent in self.agents:
            await agent.stop()

        # Stop core components
        await self.task_coordinator.stop()
        await self.agent_registry.stop()

        self.system_started = False
        self.logger.info("✅ Multi-agent system stopped")

    async def process_batch_config(self, config_path: str) -> Dict[str, Any]:
        """
        Process a batch configuration file (compatible with existing format)

        Args:
            config_path: Path to batch configuration JSON file

        Returns:
            Batch processing results
        """
        self.logger.info(f"📋 Processing batch configuration: {config_path}")

        # Load configuration
        with open(config_path, "r") as f:
            batch_config = json.load(f)

        # Validate configuration
        if "books" not in batch_config:
            raise ValueError("Invalid batch configuration: missing 'books' section")

        # Start system if using multi-agent
        if self.enable_multi_agent:
            await self.start_system()

        try:
            # Process books
            self.batch_metrics["start_time"] = datetime.now()
            results = await self._process_books(batch_config["books"])

            # Generate batch report
            return await self._generate_batch_report(results, batch_config)

        finally:
            # Stop system
            if self.enable_multi_agent:
                await self.stop_system()

    async def process_single_book(self, book_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single book (compatible with existing book config format)

        Args:
            book_config: Book configuration dictionary

        Returns:
            Book processing result
        """
        book_id = book_config.get("id", f"book_{datetime.now().strftime('%H%M%S')}")

        self.logger.info(f"📚 Processing book: {book_config.get('title', book_id)}")

        if self.enable_multi_agent and not self.system_started:
            await self.start_system()

        try:
            if self.enable_multi_agent:
                return await self._process_book_multi_agent(book_config)
            else:
                return await self._process_book_legacy(book_config)
        except Exception as e:
            self.logger.error(f"❌ Book processing failed: {e}")
            return {
                "id": book_id,
                "title": book_config.get("title", book_id),
                "status": "failed",
                "error": str(e),
                "processing_mode": self.batch_metrics["processing_mode"],
            }

    async def _setup_agents(self) -> None:
        """Setup and register agents"""
        # Create specialized agents
        agents_config = [
            {
                "class": PuzzleGeneratorAgent,
                "args": {
                    "agent_id": "puzzle_generator_batch",
                    "max_concurrent_tasks": 3,
                },
            },
            {
                "class": PDFLayoutAgent,
                "args": {"agent_id": "pdf_layout_batch", "max_concurrent_tasks": 2},
            },
            {
                "class": EPUBGeneratorAgent,
                "args": {"agent_id": "epub_generator_batch", "max_concurrent_tasks": 2},
            },
            {
                "class": QualityAssuranceAgent,
                "args": {"agent_id": "qa_validator_batch", "max_concurrent_tasks": 4},
            },
        ]

        # Create and start agents
        for agent_config in agents_config:
            agent = agent_config["class"](**agent_config["args"])
            self.agents.append(agent)

            # Register with registry
            await self.agent_registry.register_agent(
                agent_id=agent.agent_id,
                agent_type=agent.agent_type,
                capabilities=list(agent.capabilities),
                max_concurrent_tasks=agent.max_concurrent_tasks,
            )

            # Start agent
            await agent.start()
            agent.agent_registry = self.agent_registry

    async def _process_books(
        self, books_config: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process multiple books"""
        results = []

        if self.enable_multi_agent:
            # Process books in parallel using multi-agent system
            tasks = []
            for book_config in books_config:
                task = asyncio.create_task(self._process_book_multi_agent(book_config))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to error results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    book_id = books_config[i].get("id", f"book_{i}")
                    results[i] = {
                        "id": book_id,
                        "title": books_config[i].get("title", book_id),
                        "status": "failed",
                        "error": str(result),
                        "processing_mode": "multi_agent",
                    }
        else:
            # Process books sequentially using legacy mode
            for book_config in books_config:
                result = await self._process_book_legacy(book_config)
                results.append(result)

        return results

    async def _process_book_multi_agent(
        self, book_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a book using multi-agent system"""
        book_id = book_config.get("id", f"book_{datetime.now().strftime('%H%M%S')}")
        start_time = datetime.now()

        book_result = {
            "id": book_id,
            "title": book_config.get("title", book_id),
            "start_time": start_time.isoformat(),
            "processing_mode": "multi_agent",
            "status": "in_progress",
            "steps_completed": [],
            "artifacts": {},
        }

        try:
            # Step 1: Generate puzzles
            puzzle_task = Task(
                task_type=TaskType.GENERATE_PUZZLES,
                name=f"Generate puzzles for {book_id}",
                input_data={
                    "puzzle_type": book_config.get("puzzle_type", "crossword"),
                    "count": book_config.get("puzzle_count", 50),
                    "difficulty": book_config.get("difficulty", "mixed"),
                    "theme": book_config.get("theme"),
                    "series_name": book_config.get("series_name", "Batch_Series"),
                    "volume": book_config.get("volume", 1),
                    "book_id": book_id,
                },
                priority=TaskPriority.HIGH,
            )

            puzzle_task_id = await self.task_coordinator.submit_task(puzzle_task)
            await self._wait_for_task(puzzle_task_id)
            puzzle_result = await self.task_coordinator.get_task_result(puzzle_task_id)

            if not puzzle_result or not puzzle_result.success:
                raise RuntimeError(
                    f"Puzzle generation failed: {puzzle_result.error_message if puzzle_result else 'Unknown error'}"
                )

            book_result["steps_completed"].append("generate_puzzles")
            book_result["artifacts"].update(puzzle_result.artifacts)

            # Step 2: Create PDF layout
            pdf_task = Task(
                task_type=TaskType.CREATE_PDF_LAYOUT,
                name=f"Create PDF for {book_id}",
                input_data={
                    "title": book_config.get("title", f"Book {book_id}"),
                    "author": book_config.get("author", "KindleMint Publishing"),
                    "input_dir": puzzle_result.artifacts["puzzles_dir"],
                    "output_dir": puzzle_result.artifacts["puzzles_dir"].replace(
                        "/puzzles", "/paperback"
                    ),
                    "puzzle_type": book_config.get("puzzle_type", "crossword"),
                    "book_id": book_id,
                },
                priority=TaskPriority.HIGH,
            )

            pdf_task_id = await self.task_coordinator.submit_task(pdf_task)
            await self._wait_for_task(pdf_task_id)
            pdf_result = await self.task_coordinator.get_task_result(pdf_task_id)

            if not pdf_result or not pdf_result.success:
                raise RuntimeError(
                    f"PDF layout failed: {pdf_result.error_message if pdf_result else 'Unknown error'}"
                )

            book_result["steps_completed"].append("create_pdf")
            book_result["artifacts"].update(pdf_result.artifacts)

            # Step 3: Run QA validation
            qa_task = Task(
                task_type=TaskType.RUN_QA_TESTS,
                name=f"QA validation for {book_id}",
                input_data={
                    "file_path": pdf_result.artifacts["interior_pdf"],
                    "validation_type": "comprehensive",
                    "puzzle_type": book_config.get("puzzle_type", "crossword"),
                    "puzzles_dir": puzzle_result.artifacts["puzzles_dir"],
                    "book_id": book_id,
                },
                priority=TaskPriority.HIGH,
            )

            qa_task_id = await self.task_coordinator.submit_task(qa_task)
            await self._wait_for_task(qa_task_id)
            qa_result = await self.task_coordinator.get_task_result(qa_task_id)

            if not qa_result or not qa_result.success:
                raise RuntimeError(
                    f"QA validation failed: {qa_result.error_message if qa_result else 'Unknown error'}"
                )

            book_result["steps_completed"].append("run_qa")
            book_result["artifacts"].update(qa_result.artifacts)

            # Mark as completed
            book_result["status"] = "completed"
            book_result["qa_score"] = qa_result.output_data.get("overall_score", 0)
            book_result["publish_ready"] = qa_result.output_data.get(
                "publish_ready", False
            )

        except Exception as e:
            book_result["status"] = "failed"
            book_result["error"] = str(e)

        finally:
            book_result["end_time"] = datetime.now().isoformat()
            book_result["duration_seconds"] = (
                datetime.now() - start_time
            ).total_seconds()

        return book_result

    async def _process_book_legacy(self, book_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process a book using legacy system (compatibility mode)"""
        book_id = book_config.get("id", f"book_{datetime.now().strftime('%H%M%S')}")
        start_time = datetime.now()

        # Simulate legacy processing (would call existing scripts)
        self.logger.info(f"📖 Processing {book_id} in legacy mode")

        # This would normally call the existing batch processor
        # For demo purposes, we'll simulate the processing
        await asyncio.sleep(2)  # Simulate processing time

        return {
            "id": book_id,
            "title": book_config.get("title", book_id),
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "processing_mode": "legacy",
            "status": "completed",  # Assume success for demo
            "steps_completed": ["legacy_processing"],
            "artifacts": {"note": "Legacy processing - artifacts not tracked"},
        }

    async def _wait_for_task(self, task_id: str, timeout: int = 300) -> None:
        """Wait for a task to complete"""
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            status = await self.task_coordinator.get_task_status(task_id)

            if status and status.value in ["completed", "failed", "cancelled"]:
                return

            await asyncio.sleep(1)

        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")

    async def _generate_batch_report(
        self, results: List[Dict[str, Any]], batch_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate batch processing report"""
        end_time = datetime.now()
        duration = (end_time - self.batch_metrics["start_time"]).total_seconds()

        # Calculate metrics
        successful = sum(1 for r in results if r.get("status") == "completed")
        failed = len(results) - successful

        # Calculate performance improvement (if applicable)
        avg_duration = (
            sum(r.get("duration_seconds", 0) for r in results) / len(results)
            if results
            else 0
        )

        batch_report = {
            "batch_id": f"batch_{self.batch_metrics['start_time'].strftime('%Y%m%d_%H%M%S')}",
            "start_time": self.batch_metrics["start_time"].isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration_seconds": duration,
            "processing_mode": self.batch_metrics["processing_mode"],
            "books_processed": len(results),
            "books_succeeded": successful,
            "books_failed": failed,
            "success_rate": (successful / len(results) * 100) if results else 0,
            "average_book_duration": avg_duration,
            "books_per_hour": (len(results) / duration * 3600) if duration > 0 else 0,
            "book_results": results,
        }

        # Add multi-agent specific metrics
        if self.enable_multi_agent and self.system_started:
            system_status = self.agent_registry.get_system_status()
            coordination_metrics = self.task_coordinator.get_coordination_metrics()

            batch_report.update(
                {
                    "multi_agent_metrics": {
                        "active_agents": system_status["total_agents"],
                        "system_utilization": system_status["utilization"],
                        "tasks_processed": coordination_metrics["completed_tasks"],
                        "agent_performance": system_status.get("agent_performance", {}),
                    }
                }
            )

        self.logger.info(
            f"📊 Batch processing completed: {successful}/{len(results)} books successful"
        )
        return batch_report


async def main():
    """Demo of multi-agent integration"""
    print("🔄 KindleMint Multi-Agent Integration Demo")
    print("=" * 50)

    # Create sample batch configuration
    batch_config = {
        "books": [
            {
                "id": "integration_test_1",
                "title": "Multi-Agent Crossword Collection",
                "puzzle_type": "crossword",
                "puzzle_count": 15,
                "difficulty": "mixed",
                "author": "Integration Test",
                "series_name": "Integration_Test",
                "volume": 1,
            },
            {
                "id": "integration_test_2",
                "title": "Multi-Agent Sudoku Challenge",
                "puzzle_type": "sudoku",
                "puzzle_count": 20,
                "difficulty": "medium",
                "author": "Integration Test",
                "series_name": "Integration_Test",
                "volume": 2,
            },
        ]
    }

    # Save test configuration
    config_path = "test_batch_config.json"
    with open(config_path, "w") as f:
        json.dump(batch_config, f, indent=2)

    try:
        # Test multi-agent processing
        print("\n🚀 Testing Multi-Agent Processing")
        print("-" * 40)

        multi_agent_processor = MultiAgentBatchProcessor(enable_multi_agent=True)
        ma_results = await multi_agent_processor.process_batch_config(config_path)

        print(f"✅ Multi-Agent Results:")
        print(
            f"   📚 Books: {ma_results['books_succeeded']}/{ma_results['books_processed']}"
        )
        print(f"   ⏱️ Duration: {ma_results['total_duration_seconds']:.1f}s")
        print(f"   📈 Rate: {ma_results['books_per_hour']:.1f} books/hour")

        # Test legacy processing (for comparison)
        print("\n📖 Testing Legacy Processing (Simulation)")
        print("-" * 40)

        legacy_processor = MultiAgentBatchProcessor(enable_multi_agent=False)
        legacy_results = await legacy_processor.process_batch_config(config_path)

        print(f"✅ Legacy Results:")
        print(
            f"   📚 Books: {legacy_results['books_succeeded']}/{legacy_results['books_processed']}"
        )
        print(f"   ⏱️ Duration: {legacy_results['total_duration_seconds']:.1f}s")
        print(f"   📈 Rate: {legacy_results['books_per_hour']:.1f} books/hour")

        # Performance comparison
        print("\n📊 Performance Comparison")
        print("-" * 40)

        if legacy_results["total_duration_seconds"] > 0:
            improvement = (
                (
                    legacy_results["total_duration_seconds"]
                    - ma_results["total_duration_seconds"]
                )
                / legacy_results["total_duration_seconds"]
                * 100
            )
            print(f"⚡ Multi-Agent Performance Improvement: {improvement:.1f}%")

        print(f"🤖 Multi-Agent Features:")
        if "multi_agent_metrics" in ma_results:
            metrics = ma_results["multi_agent_metrics"]
            print(f"   • Active Agents: {metrics['active_agents']}")
            print(f"   • System Utilization: {metrics['system_utilization']:.1f}%")
            print(f"   • Tasks Processed: {metrics['tasks_processed']}")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Cleanup
        try:
            Path(config_path).unlink()
        except:
            pass
        print("\n✅ Integration demo completed")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run demo
    asyncio.run(main())
