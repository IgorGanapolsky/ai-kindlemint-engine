#!/usr/bin/env python3
"""
QA Validation Strategy - Automated resolution for QA validation failures
Handles puzzle book validation errors and other QA-related issues
"""

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

from .resolution_strategies import ResolutionStrategy, StrategyResult

logger = logging.getLogger("QAValidationStrategy")


class QAValidationStrategy(ResolutionStrategy):
    """Strategy for resolving QA validation failures in puzzle books"""

    def __init__(self):
        super().__init__(
            name="QA Validation Resolution",
            description="Resolve puzzle book QA validation failures",
            confidence=0.75,
            safety_level="safe",
        )

    async def execute(self, error_context: Dict[str, Any]) -> StrategyResult:
        start_time = time.time()
        actions_taken = []

        try:
            # Extract validation details from error
            error_context.get("validation_type", "unknown")
            book_info = error_context.get("book_info", {})
            failures = error_context.get("failures", [])

            logger.info(
                f"Processing QA validation failure for {
                    book_info.get('title', 'unknown book')}"
            )

            # Step 1: Identify specific validation failures
            failure_types = self._categorize_failures(failures)
            actions_taken.append(
                f"Identified {len(failure_types)} failure types")

            # Step 2: Execute appropriate fixes based on failure types
            fixes_applied = 0

            if "missing_metadata" in failure_types:
                if await self._fix_missing_metadata(book_info):
                    fixes_applied += 1
                    actions_taken.append("Fixed missing metadata")

            if "incorrect_page_count" in failure_types:
                if await self._regenerate_book(book_info):
                    fixes_applied += 1
                    actions_taken.append(
                        "Regenerated book with correct page count")

            if "puzzle_rendering_errors" in failure_types:
                if await self._fix_puzzle_rendering(book_info):
                    fixes_applied += 1
                    actions_taken.append("Fixed puzzle rendering issues")

            if "missing_solutions" in failure_types:
                if await self._generate_missing_solutions(book_info):
                    fixes_applied += 1
                    actions_taken.append("Generated missing solutions")

            # Step 3: Re-run validation
            if fixes_applied > 0:
                validation_passed = await self._rerun_validation(book_info)
                actions_taken.append("Re-ran QA validation")

                if validation_passed:
                    return StrategyResult(
                        success=True,
                        message=f"QA validation fixed: {fixes_applied} issues resolved",
                        actions_taken=actions_taken,
                        time_taken=time.time() - start_time,
                        rollback_info={
                            "book_path": book_info.get("path"),
                            "fixes_applied": fixes_applied,
                        },
                    )

            return StrategyResult(
                success=False,
                message=f"Unable to fully resolve QA validation: {
                    len(failure_types) - fixes_applied} issues remain",
                actions_taken=actions_taken,
                time_taken=time.time() - start_time,
            )

        except Exception as e:
            logger.error(f"Error executing QA validation strategy: {e}")
            return StrategyResult(
                success=False,
                message=f"Strategy execution failed: {str(e)}",
                actions_taken=actions_taken,
                time_taken=time.time() - start_time,
            )

    async def validate(self, error_context: Dict[str, Any]) -> bool:
        """Check if this strategy applies to the error"""
        error_message = error_context.get("message", "").lower()
        error_category = error_context.get("category", "").lower()

        # Check for QA validation keywords
        qa_keywords = [
            "qa",
            "validation",
            "failed",
            "puzzle",
            "book",
            "crossword",
            "sudoku",
        ]

        return error_category == "validation" or any(
            keyword in error_message for keyword in qa_keywords
        )

    async def rollback(self, rollback_info: Dict[str, Any]) -> bool:
        """Rollback QA fixes if needed"""
        try:
            book_path = rollback_info.get("book_path")
            if book_path and Path(book_path + ".backup").exists():
                # Restore from backup
                os.rename(book_path + ".backup", book_path)
                logger.info(f"Rolled back changes to {book_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def _categorize_failures(self, failures: List[str]) -> List[str]:
        """Categorize validation failures"""
        categories = []

        failure_mapping = {
            "metadata": ["missing metadata", "invalid metadata", "collection.json"],
            "page_count": ["page count", "expected 156", "incorrect pages"],
            "puzzle_rendering": ["rendering", "visual", "clue", "cell", "pdf"],
            "solutions": ["missing solution", "no solution", "answer key"],
        }

        for failure in failures:
            failure_lower = failure.lower()
            for category, keywords in failure_mapping.items():
                if any(keyword in failure_lower for keyword in keywords):
                    categories.append(category)
                    break

        return list(set(categories))

    async def _fix_missing_metadata(self, book_info: Dict) -> bool:
        """Fix missing metadata files"""
        try:
            book_path = Path(book_info.get("path", ""))
            metadata_path = book_path.parent / "metadata" / "collection.json"

            if not metadata_path.exists():
                # Generate basic metadata
                metadata = {
                    "title": book_info.get("title", "Unknown Title"),
                    "volume": book_info.get("volume", 1),
                    "puzzles": 50,
                    "difficulty": "mixed",
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }

                metadata_path.parent.mkdir(parents=True, exist_ok=True)
                import json

                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)

                logger.info(f"Created missing metadata at {metadata_path}")
                return True

        except Exception as e:
            logger.error(f"Failed to fix metadata: {e}")

        return False

    async def _regenerate_book(self, book_info: Dict) -> bool:
        """Regenerate book with correct specifications"""
        try:
            book_type = book_info.get("type", "crossword")
            volume = book_info.get("volume", 1)

            # Backup current book
            book_path = Path(book_info.get("path", ""))
            if book_path.exists():
                os.rename(book_path, str(book_path) + ".backup")

            # Run regeneration command
            cmd = [
                "python",
                "scripts/batch_processor.py",
                "--book-type",
                book_type,
                "--volumes",
                str(volume),
                "--fix-mode",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(
                    f"Successfully regenerated {book_type} volume {volume}")
                return True
            else:
                logger.error(f"Regeneration failed: {result.stderr}")

        except Exception as e:
            logger.error(f"Failed to regenerate book: {e}")

        return False

    async def _fix_puzzle_rendering(self, book_info: Dict) -> bool:
        """Fix puzzle rendering issues"""
        try:
            # Use canvas renderer for better visual distinction
            book_path = Path(book_info.get("path", ""))

            if book_path.suffix == ".pdf":
                # Re-render with canvas renderer
                cmd = [
                    "python",
                    "scripts/sudoku_canvas_renderer.py",
                    "--input",
                    str(book_path.parent),
                    "--output",
                    str(book_path),
                    "--fix-clues",
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info("Fixed puzzle rendering with canvas renderer")
                    return True

        except Exception as e:
            logger.error(f"Failed to fix rendering: {e}")

        return False

    async def _generate_missing_solutions(self, book_info: Dict) -> bool:
        """Generate missing solution pages"""
        try:
            book_path = Path(book_info.get("path", ""))
            solutions_dir = book_path.parent / "solutions"

            if not solutions_dir.exists() or not list(solutions_dir.glob("*.json")):
                # Generate solutions
                cmd = [
                    "python",
                    "scripts/generate_solutions.py",
                    "--book-path",
                    str(book_path),
                    "--output-dir",
                    str(solutions_dir),
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info("Generated missing solutions")
                    return True

        except Exception as e:
            logger.error(f"Failed to generate solutions: {e}")

        return False

    async def _rerun_validation(self, book_info: Dict) -> bool:
        """Re-run QA validation after fixes"""
        try:
            book_path = book_info.get("path", "")

            # Run validation
            cmd = ["python", "-m", "kindlemint.validators.sudoku_book_qa", book_path]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Failed to re-run validation: {e}")
            return False


# Register the strategy
def register_qa_strategies(registry):
    """Register QA validation strategies with the registry"""
    registry.register(QAValidationStrategy())
    logger.info("Registered QA validation resolution strategy")
