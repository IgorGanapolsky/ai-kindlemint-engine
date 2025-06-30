"""
A2A Puzzle Generator Agent - Generates Sudoku puzzles with specified difficulty
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..engines.sudoku import SudokuGenerator as SudokuEngine
from .agent import A2AAgent
from .skill import Skill


@dataclass
class PuzzleRequest:
    """Request structure for puzzle generation"""

    difficulty: str  # "easy", "medium", "hard", "expert"
    count: int = 1
    puzzle_type: str = "sudoku"
    format: str = "json"  # "json", "png", "both"
    large_print: bool = True
    font_size: int = 16


@dataclass
class PuzzleResponse:
    """Response structure for puzzle generation"""

    success: bool
    puzzles: List[Dict[str, Any]]
    error: Optional[str] = None
    generated_at: str = None
    metadata: Dict[str, Any] = None


class PuzzleGeneratorAgent(A2AAgent):
    """A2A Agent that generates Sudoku puzzles with validation"""

    def __init__(self, registry):
        super().__init__("puzzle_generator", registry)
        self.sudoku_engine = SudokuEngine()
        self.logger = logging.getLogger(__name__)

        # Register capabilities
        self.add_skill(
            "generate_single_puzzle",
            self._generate_single_puzzle,
            "Generate a single Sudoku puzzle with specified difficulty",
        )
        self.add_skill(
            "generate_puzzle_batch",
            self._generate_puzzle_batch,
            "Generate multiple Sudoku puzzles in batch",
        )
        self.add_skill(
            "regenerate_failed_puzzle",
            self._regenerate_failed_puzzle,
            "Regenerate a puzzle that failed validation",
        )
        self.add_skill(
            "validate_puzzle_request",
            self._validate_puzzle_request,
            "Validate puzzle generation request parameters",
        )

    def add_skill(self, name: str, handler, description: str):
        """Add a skill to the agent"""
        self.skills[name] = Skill(name, handler, description)

    async def _generate_single_puzzle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single Sudoku puzzle"""
        try:
            # Parse request
            puzzle_req = PuzzleRequest(**request)

            # Validate request
            validation_result = await self._validate_puzzle_request(request)
            if not validation_result["valid"]:
                return PuzzleResponse(
                    success=False,
                    puzzles=[],
                    error=f"Invalid request: {validation_result['error']}",
                ).__dict__

            # Generate puzzle
            puzzle_data = self.sudoku_engine.generate_puzzle(
                difficulty=puzzle_req.difficulty
            )

            # Validate generated puzzle
            if not self._validate_puzzle_structure(puzzle_data):
                return PuzzleResponse(
                    success=False,
                    puzzles=[],
                    error="Generated puzzle failed validation",
                ).__dict__

            # Format response
            puzzles = [self._format_puzzle_output(puzzle_data, puzzle_req)]

            return PuzzleResponse(
                success=True,
                puzzles=puzzles,
                generated_at=datetime.now().isoformat(),
                metadata={
                    "difficulty": puzzle_req.difficulty,
                    "large_print": puzzle_req.large_print,
                    "font_size": puzzle_req.font_size,
                },
            ).__dict__

        except Exception as e:
            self.logger.error(f"Error generating single puzzle: {e}")
            return PuzzleResponse(success=False, puzzles=[], error=str(e)).__dict__

    async def _generate_puzzle_batch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multiple puzzles in batch"""
        try:
            puzzle_req = PuzzleRequest(**request)

            # Validate request
            validation_result = await self._validate_puzzle_request(request)
            if not validation_result["valid"]:
                return PuzzleResponse(
                    success=False,
                    puzzles=[],
                    error=f"Invalid request: {validation_result['error']}",
                ).__dict__

            puzzles = []
            failed_count = 0

            for i in range(puzzle_req.count):
                try:
                    # Generate individual puzzle
                    puzzle_data = self.sudoku_engine.generate_puzzle(
                        difficulty=puzzle_req.difficulty
                    )

                    # Validate puzzle
                    if self._validate_puzzle_structure(puzzle_data):
                        formatted_puzzle = self._format_puzzle_output(
                            puzzle_data, puzzle_req
                        )
                        formatted_puzzle["batch_index"] = i + 1
                        puzzles.append(formatted_puzzle)
                    else:
                        failed_count += 1
                        self.logger.warning(
                            f"Puzzle {
                                i + 1} failed validation, skipping"
                        )

                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"Error generating puzzle {i + 1}: {e}")

            success = len(puzzles) > 0
            error = (
                f"Failed to generate {failed_count} puzzles"
                if failed_count > 0
                else None
            )

            return PuzzleResponse(
                success=success,
                puzzles=puzzles,
                error=error,
                generated_at=datetime.now().isoformat(),
                metadata={
                    "requested_count": puzzle_req.count,
                    "generated_count": len(puzzles),
                    "failed_count": failed_count,
                    "difficulty": puzzle_req.difficulty,
                },
            ).__dict__

        except Exception as e:
            self.logger.error(f"Error generating puzzle batch: {e}")
            return PuzzleResponse(success=False, puzzles=[], error=str(e)).__dict__

    async def _regenerate_failed_puzzle(
        self, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate a puzzle that failed validation"""
        try:
            # Add retry logic with different parameters
            max_retries = request.get("max_retries", 3)
            original_request = request.get("original_request", {})

            for attempt in range(max_retries):
                self.logger.info(
                    f"Regeneration attempt {attempt + 1}/{max_retries}")

                # Try with slightly modified parameters
                modified_request = original_request.copy()
                if attempt > 0:
                    # Adjust difficulty slightly for retry
                    difficulty_map = {
                        "expert": "hard",
                        "hard": "medium",
                        "medium": "easy",
                    }
                    current_diff = modified_request.get("difficulty", "medium")
                    if current_diff in difficulty_map:
                        modified_request["difficulty"] = difficulty_map[current_diff]

                result = await self._generate_single_puzzle(modified_request)

                if result["success"]:
                    result["metadata"]["regeneration_attempt"] = attempt + 1
                    return result

            return PuzzleResponse(
                success=False,
                puzzles=[],
                error=f"Failed to regenerate puzzle after {max_retries} attempts",
            ).__dict__

        except Exception as e:
            self.logger.error(f"Error regenerating puzzle: {e}")
            return PuzzleResponse(success=False, puzzles=[], error=str(e)).__dict__

    async def _validate_puzzle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate puzzle generation request"""
        try:
            # Check required fields
            if "difficulty" not in request:
                return {"valid": False, "error": "Missing required field: difficulty"}

            # Validate difficulty
            valid_difficulties = ["easy", "medium", "hard", "expert"]
            if request["difficulty"] not in valid_difficulties:
                return {
                    "valid": False,
                    "error": f"Invalid difficulty. Must be one of: {valid_difficulties}",
                }

            # Validate count
            count = request.get("count", 1)
            if not isinstance(count, int) or count < 1 or count > 1000:
                return {
                    "valid": False,
                    "error": "Count must be an integer between 1 and 1000",
                }

            # Validate puzzle type
            puzzle_type = request.get("puzzle_type", "sudoku")
            if puzzle_type != "sudoku":
                return {
                    "valid": False,
                    "error": "Only 'sudoku' puzzle type is currently supported",
                }

            return {"valid": True, "error": None}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    def _validate_puzzle_structure(self, puzzle_data: Dict[str, Any]) -> bool:
        """Validate that generated puzzle has correct structure"""
        try:
            # Check required fields
            required_fields = ["grid", "solution", "difficulty", "clue_count"]
            for field in required_fields:
                if field not in puzzle_data:
                    self.logger.error(f"Missing required field: {field}")
                    return False

            # Check puzzle grid
            puzzle = puzzle_data["grid"]
            solution = puzzle_data["solution"]

            if not isinstance(puzzle, list) or len(puzzle) != 9:
                self.logger.error("Invalid puzzle grid structure")
                return False

            # Check each row
            for row in puzzle:
                if not isinstance(row, list) or len(row) != 9:
                    self.logger.error("Invalid puzzle row structure")
                    return False

            # Check that puzzle is not completely empty or completely filled
            filled_cells = sum(
                1 for row in puzzle for cell in row if cell != 0)
            if filled_cells == 0:
                self.logger.error("Puzzle is completely empty")
                return False
            if filled_cells == 81:
                self.logger.error(
                    "Puzzle is completely filled (solution, not puzzle)")
                return False

            # Check solution is complete
            solution_filled = sum(
                1 for row in solution for cell in row if cell != 0)
            if solution_filled != 81:
                self.logger.error("Solution is not complete")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating puzzle structure: {e}")
            return False

    def _format_puzzle_output(
        self, puzzle_data: Dict[str, Any], request: PuzzleRequest
    ) -> Dict[str, Any]:
        """Format puzzle data according to request specifications"""
        output = {
            "puzzle_id": f"sudoku_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "difficulty": request.difficulty,
            "puzzle_type": request.puzzle_type,
            "large_print": request.large_print,
            "generated_at": datetime.now().isoformat(),
        }

        if request.format in ["json", "both"]:
            output.update(
                {
                    "puzzle": puzzle_data["grid"],
                    "solution": puzzle_data["solution"],
                    "clue_count": puzzle_data["clue_count"],
                    "metadata": puzzle_data.get("metadata", {}),
                }
            )

        if request.format in ["png", "both"]:
            # Note: PNG generation would be handled by PDFLayoutAgent
            output["png_required"] = True
            output["font_size"] = request.font_size

        return output


# Factory function for easy instantiation
def create_puzzle_generator_agent(registry):
    """Create and return a configured PuzzleGeneratorAgent"""
    return PuzzleGeneratorAgent(registry)
