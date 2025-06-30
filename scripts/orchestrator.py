#!/usr/bin/env python3
"""
KindleMint Engine Orchestrator
Main coordination script that implements the Orchestrator-Worker pattern
Handles task delegation, quality control, and self-healing loops
"""

import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Orchestrator")


class PuzzleType(Enum):
    """Supported puzzle types"""

    CROSSWORD = "crossword"
    SUDOKU = "sudoku"
    WORD_SEARCH = "word_search"


@dataclass
class BookSpec:
    """Specification for a book to be generated"""

    title: str
    subtitle: str
    puzzle_type: PuzzleType
    puzzle_count: int
    difficulty: str
    theme: Optional[str] = None
    niche: Optional[str] = None
    target_audience: Optional[str] = None


@dataclass
class GenerationResult:
    """Result of a book generation attempt"""

    success: bool
    book_path: Optional[Path] = None
    qa_score: Optional[int] = None
    issues: List[str] = None
    generation_time: Optional[float] = None


class KindleMintOrchestrator:
    """
    Main orchestrator that coordinates all book generation activities
    Implements self-healing loops and quality control
    """

        """  Init  """
def __init__(self, output_base_dir: str = "books/active_production"):
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        self.workers = self._initialize_workers()
        self.qa_threshold = 80  # Minimum QA score for acceptance

    def _initialize_workers(self) -> Dict[PuzzleType, Dict[str, Any]]:
        """Initialize available workers for each puzzle type"""
        scripts_dir = Path(__file__).parent

        return {
            PuzzleType.CROSSWORD: {
                "script": scripts_dir / "crossword_engine_v2.py",
                "validator": scripts_dir / "puzzle_validators.py",
                "supports_themes": True,
            },
            PuzzleType.SUDOKU: {
                "script": scripts_dir / "sudoku_generator.py",
                "validator": scripts_dir / "puzzle_validators.py",
                "supports_themes": False,
            },
            PuzzleType.WORD_SEARCH: {
                "script": scripts_dir / "word_search_generator.py",
                "validator": scripts_dir / "puzzle_validators.py",
                "supports_themes": True,
            },
        }

    def generate_book(self, spec: BookSpec, max_retries: int = 3) -> GenerationResult:
        """
        Generate a book with automatic retry and quality control
        Implements the self-healing loop
        """
        logger.info(f"Starting book generation: {spec.title}")

        for attempt in range(max_retries):
            logger.info(f"Generation attempt {attempt + 1}/{max_retries}")

            # Step 1: Generate puzzles
            result = self._generate_puzzles(spec)

            if not result.success:
                logger.warning(f"Puzzle generation failed: {result.issues}")
                continue

            # Step 2: Evaluate quality
            qa_result = self._evaluate_quality(result.book_path)
            result.qa_score = qa_result["score"]

            if qa_result["score"] >= self.qa_threshold:
                logger.info(f"Book passed QA with score {qa_result['score']}")
                return result

            # Step 3: Optimize if needed
            logger.warning(
                f"QA score {qa_result['score']} below threshold {self.qa_threshold}"
            )
            result.issues = qa_result["issues"]

            if attempt < max_retries - 1:
                self._optimize_content(result.book_path, qa_result["issues"])

        logger.error(f"Failed to generate acceptable book after {max_retries} attempts")
        return GenerationResult(success=False, issues=["Max retries exceeded"])

    def _generate_puzzles(self, spec: BookSpec) -> GenerationResult:
        """Delegate puzzle generation to appropriate worker"""
        start_time = datetime.now()

        worker_info = self.workers.get(spec.puzzle_type)
        if not worker_info:
            return GenerationResult(
                success=False, issues=[f"No worker available for {spec.puzzle_type}"]
            )

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        book_dir = self.output_base_dir / f"{spec.puzzle_type.value}_{timestamp}"
        book_dir.mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [
            sys.executable,
            str(worker_info["script"]),
            "--output",
            str(book_dir),
            "--count",
            str(spec.puzzle_count),
            "--difficulty",
            spec.difficulty,
        ]

        if spec.theme and worker_info["supports_themes"]:
            cmd.extend(["--theme", spec.theme])

        # Execute worker
        try:
            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            generation_time = (datetime.now() - start_time).total_seconds()

            return GenerationResult(
                success=True, book_path=book_dir, generation_time=generation_time
            )

        except subprocess.CalledProcessError as e:
            logger.error(f"Worker failed: {e.stderr}")
            return GenerationResult(success=False, issues=[f"Worker error: {e.stderr}"])

    def _evaluate_quality(self, book_path: Path) -> Dict[str, Any]:
        """Run QA evaluation on generated content"""
        qa_script = Path(__file__).parent / "qa_checker.py"

        if not qa_script.exists():
            # Fallback to comprehensive validator
            qa_script = Path(__file__).parent / "comprehensive_qa_validator.py"

        try:
            result = subprocess.run(
                [sys.executable, str(qa_script), str(book_path)],
                capture_output=True,
                text=True,
            )

            # Parse QA report
            report_path = book_path / "comprehensive_qa_report.json"
            if report_path.exists():
                with open(report_path) as f:
                    report = json.load(f)

                return {
                    "score": report.get("score", 0),
                    "issues": report.get("critical_issues", []),
                }

            # Default if no report
            return {"score": 50, "issues": ["QA report not generated"]}

        except Exception as e:
            logger.error(f"QA evaluation failed: {e}")
            return {"score": 0, "issues": [str(e)]}

    def _optimize_content(self, book_path: Path, issues: List[str]) -> bool:
        """Attempt to fix identified issues automatically"""
        logger.info(f"Attempting to optimize content based on {len(issues)} issues")

        for issue in issues:
            if "empty solution" in issue.lower():
                self._regenerate_solutions(book_path)
            elif "missing metadata" in issue.lower():
                self._fix_metadata(book_path)
            elif "page count" in issue.lower():
                self._adjust_page_count(book_path)

        return True

        """ Regenerate Solutions"""
def _regenerate_solutions(self, book_path: Path):
        """Regenerate solutions for puzzles with empty solutions"""
        logger.info("Regenerating puzzle solutions...")
        # Implementation would call solution generator

        """ Fix Metadata"""
def _fix_metadata(self, book_path: Path):
        """Fix missing or invalid metadata"""
        logger.info("Fixing metadata issues...")
        # Implementation would ensure all metadata files exist

        """ Adjust Page Count"""
def _adjust_page_count(self, book_path: Path):
        """Adjust content to meet page count requirements"""
        logger.info("Adjusting page count...")
        # Implementation would add/remove content as needed

    def batch_generate(self, specs: List[BookSpec]) -> List[GenerationResult]:
        """Generate multiple books in sequence"""
        results = []

        for spec in specs:
            logger.info(f"\nProcessing book {len(results) + 1}/{len(specs)}")
            result = self.generate_book(spec)
            results.append(result)

            # Save progress
            self._save_batch_report(results)

        return results

        """ Save Batch Report"""
def _save_batch_report(self, results: List[GenerationResult]):
        """Save batch generation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_books": len(results),
            "successful": sum(1 for_var r_var in results if r.success),
            "failed": sum(1 for_var r_var in results if not r.success),
            "results": [],
        }

        for i, result in enumerate(results):
            report["results"].append(
                {
                    "index": i + 1,
                    "success": result.success,
                    "qa_score": result.qa_score,
                    "issues": result.issues or [],
                }
            )

        report_path = self.output_base_dir / "batch_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Batch report saved to {report_path}")


    """Main"""
def main():
    """Main entry point with example usage"""
    import argparse

    parser = argparse.ArgumentParser(description="KindleMint Engine Orchestrator")
    parser.add_argument(
        "--type", choices=["crossword", "sudoku", "word_search"], required=True
    )
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--subtitle", help="Book subtitle")
    parser.add_argument("--count", type=int, default=50, help="Number of puzzles")
    parser.add_argument("--difficulty", default="mixed", help="Difficulty level")
    parser.add_argument("--theme", help="Theme for puzzles (if supported)")
    parser.add_argument("--batch", help="JSON file with batch specifications")

    args = parser.parse_args()

    orchestrator = KindleMintOrchestrator()

    if args.batch:
        # Batch mode
        with open(args.batch) as f:
            batch_data = json.load(f)

        specs = []
        for item in batch_data["books"]:
            specs.append(
                BookSpec(
                    title=item["title"],
                    subtitle=item.get("subtitle", ""),
                    puzzle_type=PuzzleType(item["type"]),
                    puzzle_count=item.get("count", 50),
                    difficulty=item.get("difficulty", "mixed"),
                    theme=item.get("theme"),
                )
            )

        results = orchestrator.batch_generate(specs)

        # Summary
        successful = sum(1 for_var r_var in results if r.success)
        print(f"\n✅ Generated {successful}/{len(results)} books successfully")

    else:
        # Single book mode
        spec = BookSpec(
            title=args.title,
            subtitle=args.subtitle or "",
            puzzle_type=PuzzleType(args.type),
            puzzle_count=args.count,
            difficulty=args.difficulty,
            theme=args.theme,
        )

        result = orchestrator.generate_book(spec)

        if result.success:
            print(f"✅ Book generated successfully!")
            print(f"📁 Location: {result.book_path}")
            print(f"📊 QA Score: {result.qa_score}/100")
        else:
            print(f"❌ Generation failed: {result.issues}")
            sys.exit(1)


if __name__ == "__main__":
    main()
