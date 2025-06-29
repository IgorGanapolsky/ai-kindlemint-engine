#!/usr/bin/env python3
"""
End-to-End Market Research to Publishing Pipeline
Orchestrates the entire flow from market analysis to book publication
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))


class MarketToPublishOrchestrator:
    """Orchestrates the complete pipeline from market research to publishing"""

    def __init__(self):
        self.pipeline_stages = [
            "market_research",
            "opportunity_analysis",
            "content_planning",
            "content_generation",
            "quality_assurance",
            "publishing_preparation",
            "final_review",
        ]
        self.current_stage = None
        self.pipeline_state = {}

    async def run_pipeline(self, config: Dict = None):
        """Run the complete pipeline"""
        print("🚀 MARKET TO PUBLISH PIPELINE")
        print("=" * 50)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        # Initialize pipeline state
        self.pipeline_state = {
            "start_time": datetime.now().isoformat(),
            "config": config or {},
            "stages": {},
            "selected_niches": [],
            "generated_content": [],
            "status": "running",
        }

        try:
            # Stage 1: Market Research
            await self._run_market_research()

            # Stage 2: Opportunity Analysis
            await self._analyze_opportunities()

            # Stage 3: Content Planning
            await self._plan_content()

            # Stage 4: Content Generation
            await self._generate_content()

            # Stage 5: Quality Assurance
            await self._run_quality_assurance()

            # Stage 6: Publishing Preparation
            await self._prepare_for_publishing()

            # Stage 7: Final Review
            await self._final_review()

            self.pipeline_state["status"] = "completed"
            self.pipeline_state["end_time"] = datetime.now().isoformat()

            # Save pipeline results
            self._save_pipeline_results()

            print("\n✅ PIPELINE COMPLETED SUCCESSFULLY!")

        except Exception as e:
            self.pipeline_state["status"] = "failed"
            self.pipeline_state["error"] = str(e)
            print(f"\n❌ PIPELINE FAILED: {e}")
            raise

    async def _run_market_research(self):
        """Stage 1: Run market research"""
        print("\n📊 Stage 1: Market Research")
        print("-" * 30)

        self.current_stage = "market_research"
        stage_data = {"start_time": datetime.now().isoformat(), "status": "running"}

        try:
            # Trigger market research script
            result = await self._run_subprocess(
                [
                    "python",
                    "scripts/synthetic_market_research.py",
                    "--output",
                    "research",
                    "--niches",
                    "20",
                ]
            )

            # Find generated files
            today = datetime.now().strftime("%Y-%m-%d")
            research_dir = Path("research") / today

            if research_dir.exists():
                stage_data["files"] = {
                    "csv": str(research_dir / "market_analysis.csv"),
                    "json": str(research_dir / "summary.json"),
                    "report": str(research_dir / "report.md"),
                }
                stage_data["status"] = "completed"
                print("✅ Market research completed")
            else:
                raise Exception("Research files not found")

        except Exception as e:
            stage_data["status"] = "failed"
            stage_data["error"] = str(e)
            raise

        finally:
            stage_data["end_time"] = datetime.now().isoformat()
            self.pipeline_state["stages"][self.current_stage] = stage_data

    async def _analyze_opportunities(self):
        """Stage 2: Analyze market opportunities"""
        print("\n🔍 Stage 2: Opportunity Analysis")
        print("-" * 30)

        self.current_stage = "opportunity_analysis"
        stage_data = {"start_time": datetime.now().isoformat(), "status": "running"}

        try:
            # Run the auto-reviewer
            result = await self._run_subprocess(
                ["python", "scripts/market_research_auto_reviewer.py", "--auto"]
            )

            # Load selected niches from task queue
            tasks_file = Path("tasks") / "content_generation_queue.json"
            if tasks_file.exists():
                with open(tasks_file, "r") as f:
                    tasks = json.load(f)
                    self.pipeline_state["selected_niches"] = [
                        task["niche"]
                        for task in tasks
                        if task.get("status") == "pending"
                    ]

            stage_data["selected_count"] = len(self.pipeline_state["selected_niches"])
            stage_data["status"] = "completed"
            print(
                f"✅ Selected {stage_data['selected_count']} niches for content generation"
            )

        except Exception as e:
            stage_data["status"] = "failed"
            stage_data["error"] = str(e)
            raise

        finally:
            stage_data["end_time"] = datetime.now().isoformat()
            self.pipeline_state["stages"][self.current_stage] = stage_data

    async def _plan_content(self):
        """Stage 3: Plan content for selected niches"""
        print("\n📝 Stage 3: Content Planning")
        print("-" * 30)

        self.current_stage = "content_planning"
        stage_data = {
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "content_plans": [],
        }

        try:
            for niche in self.pipeline_state["selected_niches"][
                :3
            ]:  # Limit to 3 for demo
                print(f"  Planning content for: {niche}")

                # Create content plan
                plan = {
                    "niche": niche,
                    "book_type": self._determine_book_type(niche),
                    "target_audience": self._identify_target_audience(niche),
                    "content_structure": self._design_content_structure(niche),
                }

                stage_data["content_plans"].append(plan)

            stage_data["status"] = "completed"
            print(f"✅ Created {len(stage_data['content_plans'])} content plans")

        except Exception as e:
            stage_data["status"] = "failed"
            stage_data["error"] = str(e)
            raise

        finally:
            stage_data["end_time"] = datetime.now().isoformat()
            self.pipeline_state["stages"][self.current_stage] = stage_data

    async def _generate_content(self):
        """Stage 4: Generate content for planned books"""
        print("\n🎨 Stage 4: Content Generation")
        print("-" * 30)

        self.current_stage = "content_generation"
        stage_data = {
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "generated_books": [],
        }

        try:
            content_plans = self.pipeline_state["stages"]["content_planning"][
                "content_plans"
            ]

            for plan in content_plans:
                print(f"  Generating: {plan['niche']}")

                # Simulate content generation (in real implementation, call actual generators)
                book_data = {
                    "title": f"{plan['niche']} Mastery Guide",
                    "niche": plan["niche"],
                    "type": plan["book_type"],
                    "status": "generated",
                    "file_path": f"books/generated/{plan['niche'].lower().replace(' ', '_')}.pdf",
                }

                stage_data["generated_books"].append(book_data)
                self.pipeline_state["generated_content"].append(book_data)

            stage_data["status"] = "completed"
            print(f"✅ Generated {len(stage_data['generated_books'])} books")

        except Exception as e:
            stage_data["status"] = "failed"
            stage_data["error"] = str(e)
            raise

        finally:
            stage_data["end_time"] = datetime.now().isoformat()
            self.pipeline_state["stages"][self.current_stage] = stage_data

    async def _run_quality_assurance(self):
        """Stage 5: Run QA on generated content"""
        print("\n✓ Stage 5: Quality Assurance")
        print("-" * 30)

        self.current_stage = "quality_assurance"
        stage_data = {
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "qa_results": [],
        }

        try:
            # Run QA on each generated book
            for book in self.pipeline_state["generated_content"]:
                print(f"  QA check: {book['title']}")

                # Run the QA validator
                qa_result = {"book": book["title"], "checks_passed": True, "issues": []}

                # In real implementation, call actual QA scripts
                stage_data["qa_results"].append(qa_result)

            stage_data["status"] = "completed"
            print(f"✅ QA completed for {len(stage_data['qa_results'])} books")

        except Exception as e:
            stage_data["status"] = "failed"
            stage_data["error"] = str(e)
            raise

        finally:
            stage_data["end_time"] = datetime.now().isoformat()
            self.pipeline_state["stages"][self.current_stage] = stage_data

    async def _prepare_for_publishing(self):
        """Stage 6: Prepare books for publishing"""
        print("\n📚 Stage 6: Publishing Preparation")
        print("-" * 30)

        self.current_stage = "publishing_preparation"
        stage_data = {
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "prepared_books": [],
        }

        try:
            qa_results = self.pipeline_state["stages"]["quality_assurance"][
                "qa_results"
            ]

            for i, book in enumerate(self.pipeline_state["generated_content"]):
                if qa_results[i]["checks_passed"]:
                    print(f"  Preparing: {book['title']}")

                    # Prepare metadata, covers, etc.
                    prepared = {
                        "title": book["title"],
                        "metadata_complete": True,
                        "cover_generated": True,
                        "kdp_ready": True,
                    }

                    stage_data["prepared_books"].append(prepared)

            stage_data["status"] = "completed"
            print(
                f"✅ Prepared {len(stage_data['prepared_books'])} books for publishing"
            )

        except Exception as e:
            stage_data["status"] = "failed"
            stage_data["error"] = str(e)
            raise

        finally:
            stage_data["end_time"] = datetime.now().isoformat()
            self.pipeline_state["stages"][self.current_stage] = stage_data

    async def _final_review(self):
        """Stage 7: Final review before publishing"""
        print("\n🎯 Stage 7: Final Review")
        print("-" * 30)

        self.current_stage = "final_review"
        stage_data = {
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "approved_for_publishing": [],
        }

        try:
            prepared_books = self.pipeline_state["stages"]["publishing_preparation"][
                "prepared_books"
            ]

            for book in prepared_books:
                print(f"  Final review: {book['title']}")

                # Final checks
                if book["kdp_ready"]:
                    stage_data["approved_for_publishing"].append(book["title"])

            stage_data["status"] = "completed"
            print(
                f"✅ {len(stage_data['approved_for_publishing'])} books approved for publishing"
            )

        except Exception as e:
            stage_data["status"] = "failed"
            stage_data["error"] = str(e)
            raise

        finally:
            stage_data["end_time"] = datetime.now().isoformat()
            self.pipeline_state["stages"][self.current_stage] = stage_data

    def _determine_book_type(self, niche: str) -> str:
        """Determine the best book type for a niche"""
        # Simple logic - in real implementation, use AI analysis
        if "puzzle" in niche.lower() or "sudoku" in niche.lower():
            return "puzzle_book"
        elif "journal" in niche.lower() or "planner" in niche.lower():
            return "low_content"
        else:
            return "guide_book"

    def _identify_target_audience(self, niche: str) -> str:
        """Identify target audience for the niche"""
        # Simple logic - in real implementation, use market data
        if "kids" in niche.lower() or "children" in niche.lower():
            return "children"
        elif "senior" in niche.lower() or "elderly" in niche.lower():
            return "seniors"
        else:
            return "general_adult"

    def _design_content_structure(self, niche: str) -> Dict:
        """Design content structure for the book"""
        # Simple template - in real implementation, use AI
        return {
            "chapters": 10,
            "pages": 100,
            "format": "8.5x11" if "puzzle" in niche.lower() else "6x9",
        }

    async def _run_subprocess(self, cmd: List[str]) -> str:
        """Run a subprocess asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Command failed: {stderr.decode()}")

        return stdout.decode()

    def _save_pipeline_results(self):
        """Save pipeline results to file"""
        results_dir = Path("pipeline_results")
        results_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"pipeline_run_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(self.pipeline_state, f, indent=2)

        print(f"\n📄 Pipeline results saved to: {results_file}")


async def main():
    """Main entry point"""
    orchestrator = MarketToPublishOrchestrator()

    # Run with default config
    config = {"max_niches": 5, "auto_publish": False, "quality_threshold": 0.8}

    await orchestrator.run_pipeline(config)


if __name__ == "__main__":
    asyncio.run(main())
