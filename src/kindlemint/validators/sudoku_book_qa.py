#!/usr/bin/env python3
"""
Automated QA Validator for Sudoku Books
Ensures puzzle books meet quality standards before publication
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import numpy as np
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class SudokuBookQAValidator:
    """Comprehensive QA validator for Sudoku puzzle books"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_checks = []
        
    def validate_book(self, book_path: Path) -> Dict:
        """Run all QA checks on a Sudoku book.
        
        Args:
            book_path: Path to the book file (PDF) to validate
            
        Returns:
            Dictionary containing validation report with:
                - status: 'PASS' or 'FAIL'
                - total_checks: Total number of checks performed
                - passed: Number of passed checks
                - warnings: Number of warnings
                - errors: Number of errors
                - error_details: List of error messages
                - warning_details: List of warning messages
                - passed_details: List of passed check messages
        """
        print(f"🔍 Running QA validation on: {book_path}")
        
        # Reset results
        self.errors = []
        self.warnings = []
        self.passed_checks = []
        
        # Run all checks
        if book_path.suffix == '.pdf':
            self._validate_pdf(book_path)
        
        # Check puzzle directory if available
        puzzle_dir = book_path.parent.parent / "puzzles"
        if puzzle_dir.exists():
            self._validate_puzzle_directory(puzzle_dir)
        
        # Generate report
        return self._generate_report()
    
    def _validate_pdf(self, pdf_path: Path):
        """Validate PDF content.
        
        Args:
            pdf_path: Path to the PDF file to validate
            
        Note:
            - Checks page count (expects 200+ pages)
            - Extracts text from sample pages
            - Ensures puzzles show blanks, not complete solutions
            - Updates self.errors, self.warnings, and self.passed_checks
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                # Check page count
                if num_pages < 200:
                    self.warnings.append(f"PDF has only {num_pages} pages (expected 200+)")
                else:
                    self.passed_checks.append(f"✓ PDF has correct page count: {num_pages}")
                
                # Extract text from a sample puzzle page
                if num_pages > 10:
                    sample_page = pdf_reader.pages[10]
                    text = sample_page.extract_text()
                    
                    # Critical check: Ensure puzzles aren't showing complete solutions
                    if self._is_complete_grid_in_text(text):
                        self.errors.append("❌ CRITICAL: Puzzle pages appear to contain complete solutions!")
                    else:
                        self.passed_checks.append("✓ Puzzle pages appear to have blanks (not complete solutions)")
                        
        except Exception as e:
            self.errors.append(f"Failed to read PDF: {str(e)}")
    
    def _validate_puzzle_directory(self, puzzle_dir: Path):
        """Validate puzzle files and metadata.
        
        Args:
            puzzle_dir: Path to directory containing puzzle files
            
        Note:
            - Checks metadata JSON files exist
            - Validates initial grids have blank cells
            - Checks clue counts are within valid range (17-50)
            - Verifies puzzle image files exist
            - Analyzes puzzle images for blank cells
        """
        metadata_dir = puzzle_dir / "metadata"
        puzzles_dir = puzzle_dir / "puzzles"
        
        # Check metadata files
        if metadata_dir.exists():
            json_files = list(metadata_dir.glob("sudoku_puzzle_*.json"))
            
            if len(json_files) == 0:
                self.errors.append("No puzzle metadata files found")
                return
            
            # Validate each puzzle
            issues = {
                'all_filled': 0,
                'no_blanks': 0,
                'wrong_clues': 0,
                'missing_images': 0
            }
            
            for json_file in json_files[:10]:  # Check first 10 puzzles
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Check initial grid has blanks (zeros)
                grid = data.get('initial_grid', [])
                blank_count = sum(1 for row in grid for cell in row if cell == 0)
                
                if blank_count == 0:
                    issues['all_filled'] += 1
                
                # Check clue count
                clue_count = data.get('clue_count', 0)
                if clue_count < 17 or clue_count > 50:
                    issues['wrong_clues'] += 1
                
                # Check puzzle image exists
                puzzle_id = data.get('id', 0)
                puzzle_image = puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}.png"
                if not puzzle_image.exists():
                    issues['missing_images'] += 1
                else:
                    # Analyze the image
                    self._validate_puzzle_image(puzzle_image, puzzle_id)
            
            # Report issues
            if issues['all_filled'] > 0:
                self.errors.append(f"❌ CRITICAL: {issues['all_filled']} puzzles have no blank cells!")
            else:
                self.passed_checks.append("✓ All checked puzzles have blank cells")
                
            if issues['wrong_clues'] > 0:
                self.warnings.append(f"⚠️ {issues['wrong_clues']} puzzles have unusual clue counts")
                
            if issues['missing_images'] > 0:
                self.errors.append(f"❌ {issues['missing_images']} puzzle images are missing")
        else:
            self.errors.append("Metadata directory not found")
    
    def _validate_puzzle_image(self, image_path: Path, puzzle_id: int):
        """Analyze puzzle image to ensure it has blank cells.
        
        Args:
            image_path: Path to the puzzle image file
            puzzle_id: ID of the puzzle being validated
            
        Note:
            - Converts image to grayscale
            - Analyzes white space ratio
            - Detects if puzzle appears completely filled
            - Adds errors if white ratio < 50%
        """
        try:
            img = Image.open(image_path)
            
            # Convert to grayscale numpy array
            img_array = np.array(img.convert('L'))
            
            # Simple heuristic: count white/empty regions
            # In a filled puzzle, there would be numbers everywhere
            # In a proper puzzle, there should be significant white space
            
            # Get the central region (avoiding borders)
            h, w = img_array.shape
            central = img_array[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)]
            
            # Count very white pixels (potential blank cells)
            white_pixels = np.sum(central > 240)
            total_pixels = central.size
            white_ratio = white_pixels / total_pixels
            
            # A complete grid would have less white space due to numbers
            if white_ratio < 0.5:
                self.errors.append(f"❌ Puzzle {puzzle_id} image appears to be completely filled")
            
        except Exception as e:
            self.warnings.append(f"Could not analyze image {puzzle_id}: {str(e)}")
    
    def _is_complete_grid_in_text(self, text: str) -> bool:
        """Check if extracted text looks like a complete sudoku grid.
        
        Args:
            text: Extracted text from PDF page
            
        Returns:
            True if text appears to contain a complete grid (>75 digits),
            False if it appears to be a puzzle with blanks
        """
        # Count digits in the text
        digit_count = sum(1 for char in text if char.isdigit())
        
        # A complete 9x9 grid would have 81 digits
        # A puzzle should have significantly fewer
        return digit_count > 75
    
    def _generate_report(self) -> Dict:
        """Generate QA report.
        
        Returns:
            Dictionary containing:
                - status: 'PASS' if no errors, 'FAIL' otherwise
                - total_checks: Total number of checks performed
                - passed: Number of passed checks
                - warnings: Number of warnings
                - errors: Number of errors
                - error_details: List of error messages
                - warning_details: List of warning messages
                - passed_details: List of passed check messages
        """
        total_checks = len(self.errors) + len(self.warnings) + len(self.passed_checks)
        
        report = {
            'status': 'PASS' if len(self.errors) == 0 else 'FAIL',
            'total_checks': total_checks,
            'passed': len(self.passed_checks),
            'warnings': len(self.warnings),
            'errors': len(self.errors),
            'error_details': self.errors,
            'warning_details': self.warnings,
            'passed_details': self.passed_checks
        }
        
        # Print summary
        print("\n" + "="*50)
        print("📊 QA VALIDATION REPORT")
        print("="*50)
        
        if report['status'] == 'FAIL':
            print(f"❌ STATUS: FAILED - {len(self.errors)} critical errors found!")
        else:
            print("✅ STATUS: PASSED")
        
        print(f"\n📈 Summary:")
        print(f"  • Passed checks: {len(self.passed_checks)}")
        print(f"  • Warnings: {len(self.warnings)}")
        print(f"  • Errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️ Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.passed_checks:
            print(f"\n✅ Passed Checks:")
            for check in self.passed_checks[:5]:  # Show first 5
                print(f"  • {check}")
            if len(self.passed_checks) > 5:
                print(f"  • ... and {len(self.passed_checks) - 5} more")
        
        print("\n" + "="*50)
        
        return report


def validate_sudoku_book(book_path: str) -> bool:
    """Main entry point for QA validation.
    
    Args:
        book_path: Path to the book file (PDF) to validate
        
    Returns:
        True if validation passed (no errors), False otherwise
        
    Side Effects:
        - Creates qa_report.json in the same directory as the book
        - Prints validation summary to console
    """
    validator = SudokuBookQAValidator()
    report = validator.validate_book(Path(book_path))
    
    # Save report
    report_path = Path(book_path).parent / "qa_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_path}")
    
    return report['status'] == 'PASS'


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sudoku_book_qa.py <path_to_pdf>")
        sys.exit(1)
    
    book_path = sys.argv[1]
    passed = validate_sudoku_book(book_path)
    
    sys.exit(0 if passed else 1)