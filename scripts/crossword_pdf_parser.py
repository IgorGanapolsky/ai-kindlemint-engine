#!/usr/bin/env python3
"""
Crossword PDF Parser
Extracts puzzle grids, clues, and solutions from PDF files
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import PyPDF2
from pdf2image import convert_from_path
import numpy as np
from PIL import Image
import pytesseract

@dataclass
class ExtractedPuzzle:
    """Extracted puzzle data"""
    number: int
    grid_text: str
    clues_text: str
    solution_text: str
    grid_array: Optional[List[List[str]]] = None
    across_clues: Optional[Dict[int, str]] = None
    down_clues: Optional[Dict[int, str]] = None
    solution_array: Optional[List[List[str]]] = None

class CrosswordPDFParser:
    """Parse crossword puzzles from PDF files"""
    
    def __init__(self):
        self.grid_size = 15
        self.puzzle_pattern = re.compile(r'Puzzle\s+(\d+)(?:\s|$)', re.IGNORECASE)
        self.clue_pattern = re.compile(r'(\d+)\.\s+(.+?)(?=\d+\.|$)', re.DOTALL)
        
    def extract_puzzles(self, pdf_path: str) -> List[ExtractedPuzzle]:
        """Extract all puzzles from PDF"""
        puzzles = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            # Track which pages contain what
            puzzle_pages = {}
            clue_pages = {}
            solution_pages = {}
            
            # First pass: identify page types
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                
                # Check for puzzle number
                puzzle_match = self.puzzle_pattern.search(text)
                if puzzle_match:
                    puzzle_num = int(puzzle_match.group(1))
                    
                    if 'clues' in text.lower():
                        clue_pages[puzzle_num] = i
                    elif 'solution' in text.lower():
                        solution_pages[puzzle_num] = i
                    else:
                        # Likely the grid page
                        puzzle_pages[puzzle_num] = i
            
            # Second pass: extract puzzle data
            for puzzle_num in sorted(puzzle_pages.keys()):
                if puzzle_num <= 50:  # We expect 50 puzzles
                    puzzle = ExtractedPuzzle(number=puzzle_num, 
                                           grid_text='', 
                                           clues_text='', 
                                           solution_text='')
                    
                    # Extract grid page
                    if puzzle_num in puzzle_pages:
                        page_num = puzzle_pages[puzzle_num]
                        puzzle.grid_text = reader.pages[page_num].extract_text()
                        
                        # Try to extract grid visually
                        grid = self._extract_grid_visual(pdf_path, page_num)
                        if grid:
                            puzzle.grid_array = grid
                    
                    # Extract clues
                    if puzzle_num in clue_pages:
                        page_num = clue_pages[puzzle_num]
                        puzzle.clues_text = reader.pages[page_num].extract_text()
                        
                        # Parse clues
                        across, down = self._parse_clues(puzzle.clues_text)
                        puzzle.across_clues = across
                        puzzle.down_clues = down
                    
                    # Extract solution
                    if puzzle_num in solution_pages:
                        page_num = solution_pages[puzzle_num]
                        puzzle.solution_text = reader.pages[page_num].extract_text()
                        
                        # Try to extract solution grid
                        solution = self._extract_grid_visual(pdf_path, page_num, is_solution=True)
                        if solution:
                            puzzle.solution_array = solution
                    
                    puzzles.append(puzzle)
        
        return puzzles
    
    def _extract_grid_visual(self, pdf_path: str, page_num: int, is_solution: bool = False) -> Optional[List[List[str]]]:
        """Extract grid using visual analysis"""
        try:
            # Convert page to image
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1, dpi=150)
            if not images:
                return None
            
            image = images[0]
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Find grid boundaries (look for large square region)
            grid_region = self._find_grid_region(img_array)
            if not grid_region:
                return None
            
            # Extract grid
            x, y, w, h = grid_region
            grid_img = img_array[y:y+h, x:x+w]
            
            # Divide into cells
            cell_width = w // self.grid_size
            cell_height = h // self.grid_size
            
            grid = []
            for row in range(self.grid_size):
                grid_row = []
                for col in range(self.grid_size):
                    # Extract cell
                    cell_y = row * cell_height
                    cell_x = col * cell_width
                    cell = grid_img[cell_y:cell_y+cell_height, cell_x:cell_x+cell_width]
                    
                    # Analyze cell
                    if self._is_black_square(cell):
                        grid_row.append('#')
                    elif is_solution:
                        # Extract letter using OCR
                        letter = self._extract_letter(cell)
                        grid_row.append(letter if letter else '?')
                    else:
                        grid_row.append('.')
                
                grid.append(grid_row)
            
            return grid
            
        except Exception as e:
            print(f"Error extracting grid visually: {e}")
            return None
    
    def _find_grid_region(self, img_array: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Find the crossword grid region in the image"""
        # Convert to grayscale
        gray = np.mean(img_array, axis=2).astype(np.uint8)
        
        # Find edges
        edges = self._detect_edges(gray)
        
        # Find largest square-ish region
        contours = self._find_contours(edges)
        
        best_region = None
        best_score = 0
        
        for x, y, w, h in contours:
            # Score based on size and squareness
            area = w * h
            squareness = min(w, h) / max(w, h)
            
            if squareness > 0.9 and area > best_score:
                best_score = area
                best_region = (x, y, w, h)
        
        return best_region
    
    def _is_black_square(self, cell: np.ndarray) -> bool:
        """Check if cell is a black square"""
        # Calculate average brightness
        avg_brightness = np.mean(cell)
        return avg_brightness < 50  # Threshold for black
    
    def _extract_letter(self, cell: np.ndarray) -> Optional[str]:
        """Extract letter from cell using OCR"""
        try:
            # Convert to PIL Image
            cell_img = Image.fromarray(cell)
            
            # Use OCR
            text = pytesseract.image_to_string(cell_img, config='--psm 10')
            
            # Clean and validate
            letter = text.strip().upper()
            if len(letter) == 1 and letter.isalpha():
                return letter
            
            return None
            
        except Exception:
            return None
    
    def _parse_clues(self, clues_text: str) -> Tuple[Dict[int, str], Dict[int, str]]:
        """Parse clues from text"""
        across_clues = {}
        down_clues = {}
        
        # Split into sections
        parts = re.split(r'\b(ACROSS|DOWN)\b', clues_text, flags=re.IGNORECASE)
        
        current_section = None
        for part in parts:
            if part.upper() == 'ACROSS':
                current_section = 'across'
            elif part.upper() == 'DOWN':
                current_section = 'down'
            elif current_section:
                # Extract clues from this section
                clues = self.clue_pattern.findall(part)
                
                for num_str, clue_text in clues:
                    try:
                        num = int(num_str)
                        clue = clue_text.strip()
                        
                        if current_section == 'across':
                            across_clues[num] = clue
                        else:
                            down_clues[num] = clue
                    except ValueError:
                        pass
        
        return across_clues, down_clues
    
    def _detect_edges(self, gray: np.ndarray) -> np.ndarray:
        """Simple edge detection"""
        # Sobel edge detection
        from scipy import ndimage
        
        sx = ndimage.sobel(gray, axis=0, mode='constant')
        sy = ndimage.sobel(gray, axis=1, mode='constant')
        edges = np.hypot(sx, sy)
        
        # Threshold
        edges = edges > np.percentile(edges, 90)
        
        return edges.astype(np.uint8) * 255
    
    def _find_contours(self, edges: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Find rectangular contours"""
        # Simplified contour detection
        # In real implementation, would use cv2.findContours
        
        # For now, return some dummy regions
        h, w = edges.shape
        
        # Look for large rectangular regions
        regions = []
        
        # Simple heuristic: assume grid is centered and takes up most of the page
        margin = 100
        grid_size = min(h, w) - 2 * margin
        
        if grid_size > 200:  # Minimum size check
            x = (w - grid_size) // 2
            y = (h - grid_size) // 2
            regions.append((x, y, grid_size, grid_size))
        
        return regions
    
    def validate_extracted_puzzle(self, puzzle: ExtractedPuzzle) -> Dict[str, bool]:
        """Validate extracted puzzle data"""
        validation = {
            'has_grid': bool(puzzle.grid_array),
            'has_across_clues': bool(puzzle.across_clues),
            'has_down_clues': bool(puzzle.down_clues),
            'has_solution': bool(puzzle.solution_array),
            'grid_size_correct': False,
            'clue_count_reasonable': False
        }
        
        # Check grid size
        if puzzle.grid_array:
            validation['grid_size_correct'] = (
                len(puzzle.grid_array) == self.grid_size and
                all(len(row) == self.grid_size for row in puzzle.grid_array)
            )
        
        # Check clue counts
        total_clues = len(puzzle.across_clues or {}) + len(puzzle.down_clues or {})
        validation['clue_count_reasonable'] = 20 <= total_clues <= 80
        
        return validation


def analyze_puzzle_balance(puzzles: List[ExtractedPuzzle]) -> Dict:
    """Analyze clue balance across all puzzles"""
    analysis = {
        'total_puzzles': len(puzzles),
        'puzzles_with_issues': [],
        'average_across': 0,
        'average_down': 0,
        'balance_scores': []
    }
    
    total_across = 0
    total_down = 0
    
    for puzzle in puzzles:
        across_count = len(puzzle.across_clues or {})
        down_count = len(puzzle.down_clues or {})
        total = across_count + down_count
        
        if total > 0:
            down_ratio = down_count / total
            balance_score = 100 * (1 - abs(0.5 - down_ratio) * 2)
            
            analysis['balance_scores'].append({
                'puzzle': puzzle.number,
                'across': across_count,
                'down': down_count,
                'down_ratio': down_ratio,
                'balance_score': balance_score
            })
            
            total_across += across_count
            total_down += down_count
            
            # Flag issues
            if down_ratio < 0.35 or down_ratio > 0.65:
                analysis['puzzles_with_issues'].append({
                    'puzzle': puzzle.number,
                    'issue': f'Imbalanced: {across_count} across, {down_count} down'
                })
    
    if puzzles:
        analysis['average_across'] = total_across / len(puzzles)
        analysis['average_down'] = total_down / len(puzzles)
    
    return analysis


def main():
    """Test the parser"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python crossword_pdf_parser.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    parser = CrosswordPDFParser()
    
    print("Extracting puzzles from PDF...")
    puzzles = parser.extract_puzzles(pdf_path)
    
    print(f"\nExtracted {len(puzzles)} puzzles")
    
    # Analyze balance
    analysis = analyze_puzzle_balance(puzzles)
    
    print(f"\nClue Balance Analysis:")
    print(f"Average ACROSS clues: {analysis['average_across']:.1f}")
    print(f"Average DOWN clues: {analysis['average_down']:.1f}")
    
    if analysis['puzzles_with_issues']:
        print(f"\n⚠️  Puzzles with balance issues:")
        for issue in analysis['puzzles_with_issues']:
            print(f"  - Puzzle {issue['puzzle']}: {issue['issue']}")
    
    # Show sample
    if puzzles:
        sample = puzzles[0]
        print(f"\nSample - Puzzle {sample.number}:")
        print(f"  ACROSS clues: {len(sample.across_clues or {})}")
        print(f"  DOWN clues: {len(sample.down_clues or {})}")
        
        if sample.grid_array:
            print(f"  Grid preview:")
            for row in sample.grid_array[:5]:
                print(f"    {''.join(row)}")
            print("    ...")


if __name__ == "__main__":
    main()