#!/usr/bin/env python3

    def get_varied_instructions(self, difficulty, puzzle_number):
        """Generate varied instructions for each puzzle to avoid repetition"""
        instructions = {
            "easy": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>HOW TO SOLVE:</b> Your goal is to complete the grid by placing numbers 1-9 in each empty cell. Remember: no number can repeat in the same row, column, or 3×3 box.",
                "<b>PUZZLE RULES:</b> Fill every empty square with a number from 1 to 9. Each row, column, and 3×3 section must contain all nine numbers exactly once.",
                "<b>SOLVING GOAL:</b> Complete the 9×9 grid by adding numbers 1-9 to empty cells. Every row, column, and 3×3 box must have all nine numbers with no repeats.",
                "<b>GAME RULES:</b> Place numbers 1 through 9 in each empty square. Each horizontal row, vertical column, and 3×3 box must contain all nine numbers.",
            ],
            "medium": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>CHALLENGE RULES:</b> Complete the grid by placing numbers 1-9 in empty cells. The constraint: no number can repeat within any row, column, or 3×3 box.",
                "<b>SOLVING INSTRUCTIONS:</b> Your task is to fill every empty cell with a number from 1 to 9, ensuring each row, column, and 3×3 section contains all nine numbers exactly once.",
                "<b>PUZZLE OBJECTIVE:</b> Fill the 9×9 grid completely. Each row, column, and 3×3 box must contain the numbers 1-9 with no duplicates.",
                "<b>GAME OBJECTIVE:</b> Complete the grid by adding numbers 1 through 9 to empty squares. Every row, column, and outlined 3×3 box must have all nine numbers.",
            ],
            "hard": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>EXPERT CHALLENGE:</b> Complete this grid by placing numbers 1-9 in each empty cell. The rule: no number can appear twice in the same row, column, or 3×3 box.",
                "<b>ADVANCED RULES:</b> Fill every empty square with a number from 1 to 9. Each horizontal row, vertical column, and 3×3 section must contain all nine numbers without repetition.",
                "<b>MASTER PUZZLE:</b> Your goal is to complete the 9×9 grid. Each row, column, and 3×3 box must contain the numbers 1-9 with no number appearing more than once.",
                "<b>CHALLENGE GOAL:</b> Fill the entire grid with numbers 1 through 9. Every row, column, and 3×3 box must have all nine numbers exactly once.",
            ],
        }
        
        instruction_list = instructions.get(difficulty, instructions["medium"])
        instruction_index = (puzzle_number - 1) % len(instruction_list)
        return instruction_list[instruction_index]

    def get_varied_tips(self, difficulty, puzzle_number):
        """Generate varied tips for each puzzle to avoid repetition"""
        tips = {
            "easy": [
                "<b>💡 TIP:</b> Start with rows, columns, or boxes that have the most numbers already filled in!",
                "<b>💡 HINT:</b> Look for cells where only one number can possibly fit by checking what's already in that row, column, and box.",
                "<b>💡 STRATEGY:</b> Focus on the number that appears most frequently in the grid - find where it can go in empty areas.",
                "<b>💡 APPROACH:</b> Work on one 3×3 box at a time. Complete boxes give you more clues for adjacent areas.",
                "<b>💡 METHOD:</b> If a row has 8 numbers filled, the empty cell must contain the missing number - look for these 'gift' cells first.",
                "<b>💡 TECHNIQUE:</b> Scan each number 1-9 systematically. For each number, see where it can legally go in each 3×3 box.",
                "<b>💡 SHORTCUT:</b> Start with areas that are nearly complete - they often reveal obvious moves that unlock other areas.",
            ],
            "medium": [
                "<b>💡 TIP:</b> Look for cells where only one number can fit by checking the row, column, and box constraints.",
                "<b>💡 STRATEGY:</b> Use pencil marks to write small numbers in cell corners showing all possibilities, then eliminate them systematically.",
                "<b>💡 TECHNIQUE:</b> Look for 'naked pairs' - when two cells in the same unit can only contain the same two numbers.",
                "<b>💡 METHOD:</b> When a number can only go in one row or column within a 3×3 box, eliminate it from the rest of that row/column.",
                "<b>💡 APPROACH:</b> If you find a cell where only one number fits, fill it immediately and scan for new opportunities this creates.",
                "<b>💡 HINT:</b> Focus on cells that are constrained by multiple factors - intersections of nearly-complete rows, columns, and boxes.",
                "<b>💡 STRATEGY:</b> Make a few moves, then re-scan the entire grid for new possibilities that your moves have created.",
            ],
            "hard": [
                "<b>💡 TIP:</b> Use pencil marks to note possible numbers in each cell, then eliminate them systematically.",
                "<b>💡 EXPERT TIP:</b> Advanced puzzles often require 'chain logic' - following a series of if-then statements through multiple cells.",
                "<b>💡 X-WING:</b> Look for numbers that appear in only two cells across two rows (or columns) - this creates elimination opportunities.",
                "<b>💡 ADVANCED:</b> Use 'coloring' technique - mark cells with the same candidate in different colors to spot contradictions.",
                "<b>💡 FORCING:</b> If a cell has only two possibilities, try assuming one is correct and follow the logical chain to find contradictions.",
                "<b>💡 PATTERN:</b> Look for 'Swordfish' patterns - when a number appears in only three cells across three rows, forming elimination chains.",
                "<b>💡 PERSISTENCE:</b> Hard puzzles may require multiple advanced techniques in sequence. Don't give up after one method fails.",
            ],
        }
        
        tip_list = tips.get(difficulty, tips["medium"])
        tip_index = (puzzle_number - 1) % len(tip_list)
        return tip_list[tip_index]

"""
Sudoku PDF Validator - Ensures puzzles are playable (not pre-filled)
Checks that puzzles have the correct number of empty cells
"""

import sys
from pathlib import Path
import PyPDF2
from PIL import Image
import numpy as np
import fitz  # PyMuPDF for better image extraction

def extract_images_from_pdf(pdf_path):
    """Extract all images from PDF for analysis"""
    pdf_document = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(pdf_document, xref)
            
            if pix.n - pix.alpha < 4:  # GRAY or RGB
                img_data = pix.tobytes("png")
                images.append({
                    'page': page_num + 1,
                    'data': img_data,
                    'index': img_index
                })
            pix = None
    
    pdf_document.close()
    return images

def count_filled_cells(image_data):
    """Count how many cells are filled in a Sudoku grid"""
    # Convert bytes to PIL Image
    import io
    img = Image.open(io.BytesIO(image_data))
    
    # Convert to grayscale numpy array
    img_array = np.array(img.convert('L'))
    
    # Basic grid detection (assuming 9x9 Sudoku)
    height, width = img_array.shape
    cell_height = height // 9
    cell_width = width // 9
    
    filled_count = 0
    empty_count = 0
    
    # Check each cell
    for row in range(9):
        for col in range(9):
            # Get cell boundaries
            y1 = row * cell_height + cell_height // 4
            y2 = (row + 1) * cell_height - cell_height // 4
            x1 = col * cell_width + cell_width // 4
            x2 = (col + 1) * cell_width - cell_width // 4
            
            # Extract cell region
            cell = img_array[y1:y2, x1:x2]
            
            # Check if cell contains a number (dark pixels in center)
            center_region = cell[
                cell.shape[0]//3:2*cell.shape[0]//3,
                cell.shape[1]//3:2*cell.shape[1]//3
            ]
            
            # If there are many dark pixels, it's likely a number
            if np.mean(center_region) < 200:  # Threshold for detecting numbers
                filled_count += 1
            else:
                empty_count += 1
    
    return filled_count, empty_count

def validate_sudoku_pdf(pdf_path):
    """Validate that puzzles in PDF are playable"""
    print(f"🔍 Validating Sudoku PDF: {pdf_path}")
    print("=" * 70)
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return False
    
    # Extract images
    print("📄 Extracting images from PDF...")
    images = extract_images_from_pdf(pdf_path)
    
    if not images:
        print("❌ No images found in PDF!")
        return False
    
    print(f"✅ Found {len(images)} images in PDF")
    print()
    
    # Analyze each image
    puzzle_count = 0
    solution_count = 0
    issues = []
    
    for img_info in images:
        page = img_info['page']
        filled, empty = count_filled_cells(img_info['data'])
        total = filled + empty
        
        if total != 81:
            continue  # Not a Sudoku grid
        
        fill_percentage = (filled / total) * 100
        
        print(f"Page {page}: {filled} filled cells, {empty} empty cells ({fill_percentage:.1f}% filled)")
        
        # Categorize based on fill percentage
        if fill_percentage > 90:
            # This is likely a solution (bad if labeled as puzzle)
            solution_count += 1
            if page < len(images) // 2:  # Assuming puzzles come before solutions
                issues.append(f"Page {page}: Puzzle appears to be fully solved ({fill_percentage:.1f}% filled)")
        elif 5 <= fill_percentage <= 50:
            # This is likely a valid puzzle (5-50% is normal range for Sudoku)
            # Easy: 40-50 clues (49-62% filled)
            # Medium: 30-40 clues (37-49% filled)  
            # Hard: 20-30 clues (25-37% filled)
            # Expert: 17-25 clues (21-31% filled)
            puzzle_count += 1
        else:
            # Unusual fill percentage
            issues.append(f"Page {page}: Unusual fill percentage ({fill_percentage:.1f}%)")
    
    print()
    print("📊 Summary:")
    print(f"  - Valid puzzles detected: {puzzle_count}")
    print(f"  - Solutions detected: {solution_count}")
    
    if issues:
        print()
        print("❌ Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    if puzzle_count == 0:
        print()
        print("❌ CRITICAL: No valid puzzles found! All grids appear to be solutions.")
        return False
    
    print()
    print("✅ PDF validation passed! Puzzles are playable.")
    return True

def quick_validate_images(image_dir):
    """Quick validation of puzzle images before PDF generation"""
    print(f"🔍 Quick validation of images in: {image_dir}")
    print("=" * 70)
    
    image_path = Path(image_dir)
    if not image_path.exists():
        print(f"❌ Directory not found: {image_dir}")
        return False
    
    puzzle_files = list(image_path.glob("sudoku_puzzle_*.png"))
    solution_files = list(image_path.glob("sudoku_solution_*.png"))
    
    print(f"Found {len(puzzle_files)} puzzle images")
    print(f"Found {len(solution_files)} solution images")
    
    # Check a sample of puzzles
    sample_size = min(5, len(puzzle_files))
    issues = []
    
    for i, puzzle_file in enumerate(puzzle_files[:sample_size]):
        img = Image.open(puzzle_file)
        img_array = np.array(img.convert('L'))
        
        # Quick check: count dark regions (numbers)
        dark_pixels = np.sum(img_array < 128)
        total_pixels = img_array.size
        dark_ratio = dark_pixels / total_pixels
        
        print(f"  {puzzle_file.name}: {dark_ratio*100:.1f}% dark pixels", end="")
        
        if dark_ratio > 0.15:  # Too many dark pixels for a puzzle
            print(" ❌ Too filled!")
            issues.append(f"{puzzle_file.name} appears to be a solution, not a puzzle")
        else:
            print(" ✅")
    
    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("\n✅ Image validation passed!")
    return True

def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print("Usage: python validate_sudoku_pdf.py <pdf_path> [--check-images <image_dir>]")
        sys.exit(1)
    
    if "--check-images" in sys.argv:
        # Quick image validation mode
        idx = sys.argv.index("--check-images")
        if idx + 1 < len(sys.argv):
            image_dir = sys.argv[idx + 1]
            success = quick_validate_images(image_dir)
            sys.exit(0 if success else 1)
    
    # PDF validation mode
    pdf_path = sys.argv[1]
    success = validate_sudoku_pdf(pdf_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()