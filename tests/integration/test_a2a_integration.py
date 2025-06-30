#!/usr/bin/env python3
"""Integration tests for A2A Protocol - testing the full flow"""

import asyncio
import json
from pathlib import Path

import pytest

from scripts.a2a_protocol.message_bus import A2AMessageBus, A2AOrchestrator
from scripts.a2a_protocol.puzzle_validator_agent import PuzzleValidatorAgent
from scripts.a2a_protocol.sudoku_validator import SudokuValidator


class TestA2AIntegration:
    """Integration tests for A2A protocol"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_validation_workflow(self):
        """Test complete validation workflow with real puzzles"""
        # Create message bus and orchestrator
        bus = A2AMessageBus()
        orchestrator = A2AOrchestrator(bus)

        # Register agents
        validator = PuzzleValidatorAgent()
        bus.register_agent(validator)

        # Start the message bus
        bus_task = asyncio.create_task(bus.start())

        try:
            # Load real puzzle data if available
            puzzle_path = Path("books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles/metadata/sudoku_puzzle_001.json")
            if puzzle_path.exists():
                with open(puzzle_path, "r") as f:
                    puzzle_data = json.load(f)
                    
                puzzles = [{
                    "puzzle_id": puzzle_data.get("id", 1),
                    "grid": puzzle_data["initial_grid"],
                    "solution": puzzle_data["solution_grid"],
                    "difficulty": puzzle_data.get("difficulty", "easy"),
                    "clue_count": puzzle_data.get("clue_count", 0)
                }]
            else:
                # Use test puzzle
                puzzles = [{
                    "puzzle_id": "test-1",
                    "grid": [
                        [5, 3, 0, 0, 7, 0, 0, 0, 0],
                        [6, 0, 0, 1, 9, 5, 0, 0, 0],
                        [0, 9, 8, 0, 0, 0, 0, 6, 0],
                        [8, 0, 0, 0, 6, 0, 0, 0, 3],
                        [4, 0, 0, 8, 0, 3, 0, 0, 1],
                        [7, 0, 0, 0, 2, 0, 0, 0, 6],
                        [0, 6, 0, 0, 0, 0, 2, 8, 0],
                        [0, 0, 0, 4, 1, 9, 0, 0, 5],
                        [0, 0, 0, 0, 8, 0, 0, 7, 9]
                    ],
                    "solution": [
                        [5, 3, 4, 6, 7, 8, 9, 1, 2],
                        [6, 7, 2, 1, 9, 5, 3, 4, 8],
                        [1, 9, 8, 3, 4, 2, 5, 6, 7],
                        [8, 5, 9, 7, 6, 1, 4, 2, 3],
                        [4, 2, 6, 8, 5, 3, 7, 9, 1],
                        [7, 1, 3, 9, 2, 4, 8, 5, 6],
                        [9, 6, 1, 5, 3, 7, 2, 8, 4],
                        [2, 8, 7, 4, 1, 9, 6, 3, 5],
                        [3, 4, 5, 2, 8, 6, 1, 7, 9]
                    ],
                    "difficulty": "easy",
                    "clue_count": 32
                }]

            # Run validation
            result = await orchestrator.validate_puzzles(puzzles)
            
            assert result["total_puzzles"] == 1
            assert result["processed"] == 1
            assert "valid_puzzles" in result
            assert "invalid_puzzles" in result
            assert len(result["results"]) == 1
            
            # Check individual result
            puzzle_result = result["results"][0]
            assert puzzle_result["puzzle_id"] in ["test-1", 1]
            assert "valid" in puzzle_result
            assert "clue_count" in puzzle_result

        finally:
            # Cleanup
            await bus.stop()
            bus_task.cancel()
            try:
                await bus_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_validation(self):
        """Test concurrent validation of multiple puzzles"""
        # Create infrastructure
        bus = A2AMessageBus()
        orchestrator = A2AOrchestrator(bus)
        validator = PuzzleValidatorAgent()
        bus.register_agent(validator)

        # Start the message bus
        bus_task = asyncio.create_task(bus.start())

        try:
            # Create multiple test puzzles
            puzzles = []
            for i in range(10):
                puzzle = {
                    "puzzle_id": f"test-{i}",
                    "grid": [[0] * 9 for _ in range(9)]  # Empty puzzles
                }
                # Make some valid by filling with a simple pattern
                if i % 2 == 0:
                    # Create a valid puzzle using a shift pattern
                    base_row = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                    for row in range(9):
                        puzzle["grid"][row] = base_row[row:] + base_row[:row]
                puzzles.append(puzzle)

            # Validate all puzzles concurrently
            start_time = asyncio.get_event_loop().time()
            result = await orchestrator.validate_puzzles(puzzles)
            end_time = asyncio.get_event_loop().time()

            # Verify results
            assert result["total_puzzles"] == 10
            assert result["processed"] == 10
            assert result["valid_puzzles"] == 5  # Half should be valid
            assert result["invalid_puzzles"] == 5

            # Should be reasonably fast due to concurrency
            elapsed = end_time - start_time
            assert elapsed < 2.0  # Should complete in under 2 seconds

        finally:
            # Cleanup
            await bus.stop()
            bus_task.cancel()
            try:
                await bus_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling(self):
        """Test error handling in the A2A system"""
        bus = A2AMessageBus()
        orchestrator = A2AOrchestrator(bus)
        validator = PuzzleValidatorAgent()
        bus.register_agent(validator)

        bus_task = asyncio.create_task(bus.start())

        try:
            # Test with invalid puzzle format
            invalid_puzzles = [
                {
                    "puzzle_id": "bad-1",
                    "grid": "not a grid"  # Invalid format
                },
                {
                    "puzzle_id": "bad-2",
                    "grid": [[1, 2, 3], [4, 5, 6]]  # Wrong dimensions
                },
                {
                    "puzzle_id": "bad-3",
                    # Missing grid
                }
            ]

            result = await orchestrator.validate_puzzles(invalid_puzzles)
            
            # Should handle errors gracefully
            assert result["total_puzzles"] == 3
            assert result["processed"] == 3
            assert result["invalid_puzzles"] == 3
            
            # Check error details
            for puzzle_result in result["results"]:
                assert puzzle_result["valid"] is False
                assert "errors" in puzzle_result

        finally:
            await bus.stop()
            bus_task.cancel()
            try:
                await bus_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])