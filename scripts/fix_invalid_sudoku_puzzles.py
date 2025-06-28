#!/usr/bin/env python3
"""
Fix Invalid Sudoku Puzzles
Identifies and fixes puzzles with empty rows/columns by regenerating them
"""

import json
import os
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple

class SudokuPuzzleFixer:
    """Fix invalid Sudoku puzzles with empty rows/columns"""
    
    DIFFICULTY_CLUE_RANGES = {
        "easy": {"min": 35, "max": 45, "target": 40},
        "medium": {"min": 27, "max": 34, "target": 30},
        "hard": {"min": 20, "max": 26, "target": 23},
        "expert": {"min": 17, "max": 19, "target": 18}
    }
    
    def __init__(self, puzzles_dir: Path):
        self.puzzles_dir = puzzles_dir
        self.metadata_dir = puzzles_dir / "metadata"
        self.issues_found = []
        self.fixed_puzzles = []
        
    def check_puzzle_validity(self, grid: List[List[int]]) -> Tuple[bool, List[str]]:
        """Check if a puzzle grid is valid"""
        issues = []
        
        # Check for empty rows
        for i, row in enumerate(grid):
            if all(cell == 0 for cell in row):
                issues.append(f"Empty row {i + 1}")
        
        # Check for empty columns
        for j in range(9):
            if all(grid[i][j] == 0 for i in range(9)):
                issues.append(f"Empty column {j + 1}")
        
        # Count total clues
        clue_count = sum(1 for row in grid for cell in row if cell != 0)
        if clue_count < 17:
            issues.append(f"Too few clues: {clue_count} (minimum 17)")
        
        return len(issues) == 0, issues
    
    def find_invalid_puzzles(self) -> List[Dict[str, Any]]:
        """Find all puzzles with validity issues"""
        invalid_puzzles = []
        
        print("🔍 Checking all puzzles for validity issues...")
        
        for i in range(1, 101):
            puzzle_file = self.metadata_dir / f"sudoku_puzzle_{i:03d}.json"
            if puzzle_file.exists():
                with open(puzzle_file, 'r') as f:
                    puzzle_data = json.load(f)
                
                grid = puzzle_data.get('initial_grid', [])
                is_valid, issues = self.check_puzzle_validity(grid)
                
                if not is_valid:
                    invalid_puzzles.append({
                        'id': i,
                        'file': puzzle_file,
                        'data': puzzle_data,
                        'issues': issues
                    })
                    print(f"❌ Puzzle #{i}: {', '.join(issues)}")
        
        return invalid_puzzles
    
    def ensure_minimum_clues_per_unit(self, grid: List[List[int]], solution: List[List[int]], 
                                     target_clues: int) -> List[List[int]]:
        """Ensure each row, column, and box has at least one clue"""
        # Start with a copy of the grid
        new_grid = [row[:] for row in grid]
        
        # Ensure each row has at least one clue
        for i in range(9):
            if all(new_grid[i][j] == 0 for j in range(9)):
                # Add a clue in a random position
                valid_positions = [j for j in range(9) if solution[i][j] != 0]
                if valid_positions:
                    j = random.choice(valid_positions)
                    new_grid[i][j] = solution[i][j]
        
        # Ensure each column has at least one clue
        for j in range(9):
            if all(new_grid[i][j] == 0 for i in range(9)):
                # Add a clue in a random position
                valid_positions = [i for i in range(9) if solution[i][j] != 0 and new_grid[i][j] == 0]
                if valid_positions:
                    i = random.choice(valid_positions)
                    new_grid[i][j] = solution[i][j]
        
        # Ensure each 3x3 box has at least one clue
        for box_row in range(3):
            for box_col in range(3):
                has_clue = False
                for i in range(3):
                    for j in range(3):
                        if new_grid[box_row * 3 + i][box_col * 3 + j] != 0:
                            has_clue = True
                            break
                    if has_clue:
                        break
                
                if not has_clue:
                    # Add a clue in the box
                    valid_positions = []
                    for i in range(3):
                        for j in range(3):
                            row = box_row * 3 + i
                            col = box_col * 3 + j
                            if solution[row][col] != 0 and new_grid[row][col] == 0:
                                valid_positions.append((row, col))
                    
                    if valid_positions:
                        row, col = random.choice(valid_positions)
                        new_grid[row][col] = solution[row][col]
        
        # Add more clues if needed to reach target
        current_clues = sum(1 for row in new_grid for cell in row if cell != 0)
        
        while current_clues < target_clues:
            # Find empty positions
            empty_positions = [(i, j) for i in range(9) for j in range(9) if new_grid[i][j] == 0]
            
            if not empty_positions:
                break
            
            # Add a random clue
            i, j = random.choice(empty_positions)
            new_grid[i][j] = solution[i][j]
            current_clues += 1
        
        return new_grid
    
    def fix_puzzle(self, puzzle_info: Dict[str, Any]) -> bool:
        """Fix a single invalid puzzle"""
        puzzle_id = puzzle_info['id']
        puzzle_data = puzzle_info['data']
        issues = puzzle_info['issues']
        
        print(f"\n🔧 Fixing Puzzle #{puzzle_id}...")
        print(f"   Issues: {', '.join(issues)}")
        
        # Get the solution
        solution = puzzle_data.get('solution_grid', puzzle_data.get('solution', []))
        if not solution:
            print(f"   ❌ No solution found for puzzle #{puzzle_id}")
            return False
        
        # Get difficulty and target clue count
        difficulty = puzzle_data.get('difficulty', 'medium').lower()
        clue_range = self.DIFFICULTY_CLUE_RANGES.get(difficulty, self.DIFFICULTY_CLUE_RANGES['medium'])
        target_clues = clue_range['target']
        
        # Generate a new valid grid
        new_grid = self.ensure_minimum_clues_per_unit(
            puzzle_data.get('initial_grid', []), 
            solution, 
            target_clues
        )
        
        # Verify the fixed grid
        is_valid, remaining_issues = self.check_puzzle_validity(new_grid)
        
        if is_valid:
            # Update puzzle data
            puzzle_data['initial_grid'] = new_grid
            puzzle_data['grid'] = new_grid  # Some puzzles use 'grid' instead
            puzzle_data['clue_count'] = sum(1 for row in new_grid for cell in row if cell != 0)
            
            # Save the fixed puzzle
            with open(puzzle_info['file'], 'w') as f:
                json.dump(puzzle_data, f, indent=2)
            
            print(f"   ✅ Fixed! New clue count: {puzzle_data['clue_count']}")
            self.fixed_puzzles.append(puzzle_id)
            return True
        else:
            print(f"   ❌ Could not fix puzzle. Remaining issues: {', '.join(remaining_issues)}")
            return False
    
    def run(self):
        """Run the puzzle fixer"""
        print("🚀 Starting Sudoku Puzzle Fixer")
        print("=" * 50)
        
        # Find invalid puzzles
        invalid_puzzles = self.find_invalid_puzzles()
        
        if not invalid_puzzles:
            print("\n✅ All puzzles are valid! No fixes needed.")
            return
        
        print(f"\n📊 Found {len(invalid_puzzles)} invalid puzzles")
        
        # Fix each invalid puzzle
        fixed_count = 0
        for puzzle_info in invalid_puzzles:
            if self.fix_puzzle(puzzle_info):
                fixed_count += 1
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        print(f"Invalid puzzles found: {len(invalid_puzzles)}")
        print(f"Puzzles fixed: {fixed_count}")
        print(f"Failed to fix: {len(invalid_puzzles) - fixed_count}")
        
        if fixed_count > 0:
            print(f"\n✅ Successfully fixed puzzles: {', '.join(f'#{p}' for p in self.fixed_puzzles)}")
        
        if fixed_count < len(invalid_puzzles):
            failed = [p['id'] for p in invalid_puzzles if p['id'] not in self.fixed_puzzles]
            print(f"\n❌ Failed to fix puzzles: {', '.join(f'#{p}' for p in failed)}")
            print("   These puzzles may need manual regeneration.")


def main():
    """Main function"""
    base_path = Path(__file__).parent.parent
    puzzles_dir = base_path / "books" / "active_production" / "Large_Print_Sudoku_Masters" / "volume_1" / "puzzles"
    
    if not puzzles_dir.exists():
        print(f"❌ ERROR: Puzzles directory not found: {puzzles_dir}")
        return
    
    fixer = SudokuPuzzleFixer(puzzles_dir)
    fixer.run()


if __name__ == "__main__":
    main()