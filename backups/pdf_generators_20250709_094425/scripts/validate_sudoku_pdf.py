#!/usr/bin/env python3
"""
Sudoku PDF Validator - Ensures puzzles are playable (not pre-filled)
Checks that puzzles have the correct number of empty cells
"""

import sys
from pathlib import Path
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