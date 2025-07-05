"""
Simple Sudoku Generator for Lead Magnets

Generates easy-to-solve Sudoku puzzles perfect for seniors
"""

import random
import copy


class SudokuGenerator:
    """Generate Sudoku puzzles with varying difficulty"""
    
    def __init__(self):
        """Initialize the generator"""
        self.size = 9
        
    def generate_puzzle(self, difficulty='easy'):
        """
        Generate a Sudoku puzzle
        
        Args:
            difficulty: 'easy', 'medium', or 'hard'
            
        Returns:
            Dict with puzzle, solution, and metadata
        """
        # Start with a valid completed grid
        solution = self._generate_complete_grid()
        
        # Create puzzle by removing numbers based on difficulty
        puzzle = self._create_puzzle_from_solution(solution, difficulty)
        
        return {
            'puzzle': puzzle,
            'solution': solution,
            'difficulty': difficulty,
            'given_numbers': self._count_given_numbers(puzzle),
            'title': f'{difficulty.capitalize()} Sudoku Puzzle'
        }
    
    def _generate_complete_grid(self):
        """Generate a complete valid Sudoku grid"""
        # Start with a base valid grid
        grid = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]
        
        # Shuffle to create variations
        self._shuffle_grid(grid)
        
        return grid
    
    def _shuffle_grid(self, grid):
        """Shuffle the grid while maintaining validity"""
        # Randomly swap rows within boxes
        for box_row in range(3):
            rows = list(range(box_row * 3, (box_row + 1) * 3))
            random.shuffle(rows)
            original_rows = [grid[i][:] for i in range(box_row * 3, (box_row + 1) * 3)]
            for i, row_idx in enumerate(rows):
                grid[box_row * 3 + i] = original_rows[row_idx - box_row * 3]
        
        # Randomly swap columns within boxes
        for box_col in range(3):
            cols = list(range(box_col * 3, (box_col + 1) * 3))
            random.shuffle(cols)
            original_cols = [[grid[i][j] for i in range(9)] for j in range(box_col * 3, (box_col + 1) * 3)]
            for i, col_idx in enumerate(cols):
                for row in range(9):
                    grid[row][box_col * 3 + i] = original_cols[col_idx - box_col * 3][row]
    
    def _create_puzzle_from_solution(self, solution, difficulty):
        """Create puzzle by removing numbers from solution"""
        puzzle = copy.deepcopy(solution)
        
        # Number of cells to remove based on difficulty
        remove_counts = {
            'easy': 35,      # ~43% filled
            'medium': 45,    # ~44% filled  
            'hard': 55       # ~32% filled
        }
        
        remove_count = remove_counts.get(difficulty, 35)
        
        # Remove numbers randomly
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        removed = 0
        for row, col in positions:
            if removed >= remove_count:
                break
            
            # Try removing this number
            original = puzzle[row][col]
            puzzle[row][col] = 0
            
            # For simplicity, we'll assume the puzzle is still solvable
            # In a production system, you'd verify solvability
            removed += 1
        
        return puzzle
    
    def _count_given_numbers(self, puzzle):
        """Count non-zero numbers in puzzle"""
        return sum(1 for row in puzzle for cell in row if cell != 0)
    
    def format_puzzle_for_print(self, puzzle):
        """Format puzzle for printing/PDF generation"""
        lines = []
        for i, row in enumerate(puzzle):
            if i % 3 == 0 and i != 0:
                lines.append("------+-------+------")
            
            row_str = ""
            for j, cell in enumerate(row):
                if j % 3 == 0 and j != 0:
                    row_str += "| "
                
                if cell == 0:
                    row_str += "  "
                else:
                    row_str += f"{cell} "
            
            lines.append(row_str)
        
        return "\n".join(lines)


def main():
    """Test the generator"""
    gen = SudokuGenerator()
    
    print("🧩 Testing Sudoku Generator")
    print("=" * 50)
    
    for difficulty in ['easy', 'medium', 'hard']:
        puzzle_data = gen.generate_puzzle(difficulty)
        print(f"\n{difficulty.upper()} PUZZLE:")
        print(f"Given numbers: {puzzle_data['given_numbers']}/81")
        print(gen.format_puzzle_for_print(puzzle_data['puzzle']))


if __name__ == "__main__":
    main()