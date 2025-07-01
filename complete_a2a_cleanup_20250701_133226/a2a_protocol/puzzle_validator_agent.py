#!/usr/bin/env python3
"""
Puzzle Validator Agent - A2A implementation for validating Sudoku puzzles
"""

import json
import logging

# Add parent directory to Python path
import sys
from pathlib import Path
from typing import Any, Dict, List

from .base_agent import A2AAgent, A2AMessage, AgentCapability
from .sudoku_validator import SudokuValidator

sys.path.append(str(Path(__file__).parent.parent))

# Import existing validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PuzzleValidatorAgent(A2AAgent):
    """A2A Agent for validating puzzles"""

        """  Init  """


def __init__(self):
        super().__init__(
            agent_id="puzzle-validator-001",
            agent_type="validator",
            name="Puzzle Validator",
            description="Validates Sudoku puzzles for correctness and quality",
            version="1.0.0",
        )

        # Initialize the actual validator
        self.validator = SudokuValidator()

    def _define_capabilities(self) -> List[AgentCapability]:
        """Define what this agent can do"""
        return [
            AgentCapability(
                name="validate_puzzle",
                description="Validate a single Sudoku puzzle for correctness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "puzzle_grid": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 9,
                                },
                            },
                            "minItems": 9,
                            "maxItems": 9,
                        },
                        "solution_grid": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 9,
                                },
                            },
                            "minItems": 9,
                            "maxItems": 9,
                        },
                    },
                    "required": ["puzzle_grid", "solution_grid"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "errors": {"type": "array", "items": {"type": "string"}},
                        "quality_score": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                        },
                    },
                },
            ),
            AgentCapability(
                name="validate_batch",
                description="Validate multiple puzzles in batch",
                input_schema={
                    "type": "object",
                    "properties": {
                        "puzzles": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "puzzle_grid": {"type": "array"},
                                    "solution_grid": {"type": "array"},
                                },
                            },
                        }
                    },
                    "required": ["puzzles"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "total_puzzles": {"type": "integer"},
                        "valid_puzzles": {"type": "integer"},
                        "invalid_puzzles": {"type": "integer"},
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "valid": {"type": "boolean"},
                                    "errors": {"type": "array"},
                                },
                            },
                        },
                    },
                },
            ),
            AgentCapability(
                name="check_puzzle_quality",
                description="Check puzzle quality metrics (clue distribution, difficulty, etc.)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "puzzle_grid": {"type": "array"},
                        "difficulty": {
                            "type": "string",
                            "enum": ["easy", "medium", "hard"],
                        },
                    },
                    "required": ["puzzle_grid"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "clue_count": {"type": "integer"},
                        "clue_coverage": {"type": "number"},
                        "has_unique_solution": {"type": "boolean"},
                        "difficulty_appropriate": {"type": "boolean"},
                        "visual_balance": {"type": "number"},
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            ),
        ]

    def _register_handlers(self) -> Dict[str, Any]:
        """Register message handlers for each capability"""
        return {
            "validate_puzzle": self._handle_validate_puzzle,
            "validate_batch": self._handle_validate_batch,
            "check_puzzle_quality": self._handle_check_puzzle_quality,
        }

    def _handle_validate_puzzle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle single puzzle validation request"""
        puzzle_grid = payload.get("puzzle_grid")
        solution_grid = payload.get("solution_grid")

        if not puzzle_grid or not solution_grid:
            raise ValueError("Missing required fields: puzzle_grid and solution_grid")

        # Validate the puzzle
        errors = []
        valid = True

        # Check if puzzle has clues (not blank)
        clue_count = sum(1 for row in puzzle_grid for cell in row if cell != 0)
        if clue_count == 0:
            errors.append("Puzzle is completely blank - no clues provided")
            valid = False
        elif clue_count < 17:  # Minimum for unique solution
            errors.append(
                f"Too few clues ({
                    clue_count}) - minimum 17 required for unique solution"
            )
            valid = False

        # Validate solution correctness
        solution_valid, solution_errors = self.validator.validate_solution(
            solution_grid
        )
        if not solution_valid:
            errors.extend(solution_errors)
            valid = False

        # Check if puzzle matches solution
        if valid:
            matches, match_errors = self.validator.validate_puzzle_solution_match(
                puzzle_grid, solution_grid
            )
            if not matches:
                errors.extend(match_errors)
                valid = False

        # Calculate quality score
        quality_score = self._calculate_quality_score(puzzle_grid, solution_grid)

        return {"valid": valid, "errors": errors, "quality_score": quality_score}

    def _handle_validate_batch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch validation request"""
        puzzles = payload.get("puzzles", [])

        results = []
        valid_count = 0

        for puzzle in puzzles:
            puzzle_id = puzzle.get("id", "unknown")
            try:
                validation_result = self._handle_validate_puzzle(
                    {
                        "puzzle_grid": puzzle.get("puzzle_grid"),
                        "solution_grid": puzzle.get("solution_grid"),
                    }
                )

                results.append(
                    {
                        "id": puzzle_id,
                        "valid": validation_result["valid"],
                        "errors": validation_result.get("errors", []),
                    }
                )

                if validation_result["valid"]:
                    valid_count += 1

            except Exception as e:
                results.append(
                    {
                        "id": puzzle_id,
                        "valid": False,
                        "errors": [f"Validation error: {str(e)}"],
                    }
                )

        return {
            "total_puzzles": len(puzzles),
            "valid_puzzles": valid_count,
            "invalid_puzzles": len(puzzles) - valid_count,
            "results": results,
        }

    def _handle_check_puzzle_quality(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Check puzzle quality metrics"""
        puzzle_grid = payload.get("puzzle_grid")
        difficulty = payload.get("difficulty", "medium")

        if not puzzle_grid:
            raise ValueError("Missing required field: puzzle_grid")

        # Count clues
        clue_count = sum(1 for row in puzzle_grid for cell in row if cell != 0)
        total_cells = 81
        clue_coverage = (clue_count / total_cells) * 100

        # Check difficulty appropriateness
        difficulty_ranges = {
            "easy": (40, 50),  # Updated based on user feedback
            "medium": (32, 40),
            "hard": (26, 32),
        }

        min_clues, max_clues = difficulty_ranges.get(difficulty, (30, 40))
        difficulty_appropriate = min_clues <= clue_count <= max_clues

        # Check visual balance (distribution of clues)
        visual_balance = self._calculate_visual_balance(puzzle_grid)

        # Generate recommendations
        recommendations = []

        if clue_count == 0:
            recommendations.append("CRITICAL: Puzzle is completely blank - add clues!")
        elif clue_count < 17:
            recommendations.append(
                "Add more clues - minimum 17 required for unique solution"
            )
        elif not difficulty_appropriate:
            if clue_count < min_clues:
                recommendations.append(
                    f"Add {min_clues - clue_count} more clues for {difficulty} difficulty"
                )
            else:
                recommendations.append(
                    f"Remove {clue_count - max_clues} clues for {difficulty} difficulty"
                )

        if visual_balance < 0.7:
            recommendations.append(
                "Improve clue distribution for better visual balance"
            )

        # Check for customer instructions (this would normally check the PDF)
        recommendations.append(
            "Ensure puzzle includes clear instructions for customers"
        )

        return {
            "clue_count": clue_count,
            "clue_coverage": round(clue_coverage, 1),
            "has_unique_solution": clue_count >= 17,
            "difficulty_appropriate": difficulty_appropriate,
            "visual_balance": round(visual_balance, 2),
            "recommendations": recommendations,
        }

    def _calculate_quality_score(
        self, puzzle_grid: List[List[int]], solution_grid: List[List[int]]
    ) -> float:
        """Calculate overall quality score for a puzzle"""
        score = 100.0

        # Clue count check
        clue_count = sum(1 for row in puzzle_grid for cell in row if cell != 0)
        if clue_count == 0:
            return 0.0  # Blank puzzle
        elif clue_count < 17:
            score -= 30  # Too few clues
        elif clue_count > 60:
            score -= 10  # Too many clues (too easy)

        # Visual balance
        balance = self._calculate_visual_balance(puzzle_grid)
        if balance < 0.7:
            score -= 20

        # Check for repeated patterns (simplified)
        if self._has_obvious_patterns(puzzle_grid):
            score -= 15

        return max(0, score)

    def _calculate_visual_balance(self, puzzle_grid: List[List[int]]) -> float:
        """Calculate how well distributed the clues are"""
        # Check each 3x3 box
        box_clues = []
        for box_row in range(3):
            for box_col in range(3):
                clues = 0
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        if puzzle_grid[row][col] != 0:
                            clues += 1
                box_clues.append(clues)

        # Calculate standard deviation
        avg_clues = sum(box_clues) / len(box_clues)
        if avg_clues == 0:
            return 0.0

        variance = sum((x - avg_clues) ** 2 for x_var in box_clues) / len(box_clues)
        std_dev = variance**0.5

        # Lower std_dev means better balance
        balance = 1.0 - (std_dev / avg_clues) if avg_clues > 0 else 0.0
        return min(1.0, max(0.0, balance))

    def _has_obvious_patterns(self, puzzle_grid: List[List[int]]) -> bool:
        """Check for obvious patterns that make puzzle too easy"""
        # Check for complete rows or columns
        for i in range(9):
            row_clues = sum(1 for j in range(9) if puzzle_grid[i][j] != 0)
            col_clues = sum(1 for j in range(9) if puzzle_grid[j][i] != 0)
            if row_clues >= 8 or col_clues >= 8:
                return True
        return False


# Example usage and testing
if __name__ == "__main__":
    # Create the validator agent
    validator = PuzzleValidatorAgent()

    # Test with a sample message
    from base_agent import A2AMessage

    # Create a validation request
    test_puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    test_solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]

    # Create message
    message = A2AMessage.create_request(
        sender_id="orchestrator-001",
        receiver_id="puzzle-validator-001",
        action="validate_puzzle",
        payload={"puzzle_grid": test_puzzle, "solution_grid": test_solution},
    )

    # Process message
    response = validator.process_message(message)

    print(f"Response type: {response.message_type}")
    print(f"Validation result: {json.dumps(response.payload, indent=2)}")

    # Test quality check
    quality_message = A2AMessage.create_request(
        sender_id="orchestrator-001",
        receiver_id="puzzle-validator-001",
        action="check_puzzle_quality",
        payload={"puzzle_grid": test_puzzle, "difficulty": "medium"},
    )

    quality_response = validator.process_message(quality_message)
    print(f"\nQuality check result: {json.dumps(quality_response.payload, indent=2)}")
