#!/usr/bin/env python3
"""
Update all PDF generators to use varied content approach
Ensures quality standards are met across all generators
"""

import os
import sys
from pathlib import Path
import shutil
from datetime import datetime


class PDFGeneratorUpdater:
    """Updates all PDF generators to include varied content"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.updated_files = []
        self.backup_dir = self.project_root / "backups" / f"pdf_generators_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def find_pdf_generators(self) -> list:
        """Find all Python files that generate PDFs"""
        generators = []
        
        # Search patterns
        patterns = [
            "**/pdf*.py",
            "**/*pdf.py", 
            "**/generate*.py",
            "**/create*book*.py"
        ]
        
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                # Skip test files and backups
                if any(skip in str(file_path) for skip in ["test", "backup", "__pycache__", ".git"]):
                    continue
                    
                # Check if file contains PDF generation code
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if any(indicator in content for indicator in [
                            "reportlab", "PDF", "SimpleDocTemplate", 
                            "create_puzzle_page", "generate_pdf"
                        ]):
                            generators.append(file_path)
                except Exception:
                    pass
                    
        return list(set(generators))  # Remove duplicates
    
    def backup_file(self, file_path: Path):
        """Create backup of original file"""
        relative_path = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        
    def add_varied_content_methods(self, file_path: Path) -> bool:
        """Add varied content methods to a PDF generator"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check if already has varied content
            if "get_varied_instructions" in content or "varied_tips" in content:
                print(f"  ✓ Already has varied content: {file_path.name}")
                return False
                
            # Check if it's a puzzle PDF generator
            if not any(term in content for term in ["puzzle", "sudoku", "crossword"]):
                print(f"  ⚠️  Not a puzzle generator: {file_path.name}")
                return False
                
            # Backup original
            self.backup_file(file_path)
            
            # Find where to insert the methods (after class definition or imports)
            lines = content.split('\n')
            insert_index = -1
            
            # Look for class definition
            for i, line in enumerate(lines):
                if line.strip().startswith("class ") and "PDF" in line:
                    # Find the end of __init__ method
                    for j in range(i, len(lines)):
                        if lines[j].strip().startswith("def ") and "__init__" not in lines[j]:
                            insert_index = j
                            break
                    break
                    
            if insert_index == -1:
                # No class found, insert after imports
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith(("import", "from", "#")):
                        insert_index = i
                        break
                        
            if insert_index == -1:
                print(f"  ❌ Could not find insertion point: {file_path.name}")
                return False
                
            # Insert varied content methods
            varied_methods = '''
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
'''
            
            # Insert the methods
            lines.insert(insert_index, varied_methods)
            
            # Update puzzle page creation to use varied content
            updated_content = '\n'.join(lines)
            
            # Replace hardcoded instructions with method calls
            replacements = [
                (
                    'INSTRUCTIONS: Fill in the empty squares so that',
                    'self.get_varied_instructions(difficulty.lower(), puzzle_number)'
                ),
                (
                    '"INSTRUCTIONS: Fill in the empty squares"',
                    'self.get_varied_instructions(difficulty.lower(), puzzle_number)'
                ),
                (
                    'TIP: Start with rows, columns, or boxes',
                    'self.get_varied_tips(difficulty.lower(), puzzle_number)'
                ),
            ]
            
            for old, new in replacements:
                if old in updated_content:
                    updated_content = updated_content.replace(old, new)
                    
            # Write updated content
            with open(file_path, 'w') as f:
                f.write(updated_content)
                
            self.updated_files.append(file_path)
            print(f"  ✅ Updated with varied content: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error updating {file_path.name}: {e}")
            return False
    
    def update_all_generators(self):
        """Update all PDF generators with varied content"""
        print("🔍 Finding PDF generators...")
        generators = self.find_pdf_generators()
        print(f"Found {len(generators)} PDF generator files")
        
        print(f"\n📁 Creating backups in: {self.backup_dir}")
        
        print("\n🔧 Updating generators...")
        updated_count = 0
        
        for generator in generators:
            print(f"\n📄 Processing: {generator.relative_to(self.project_root)}")
            if self.add_varied_content_methods(generator):
                updated_count += 1
                
        print(f"\n✅ Summary:")
        print(f"  • Total generators found: {len(generators)}")
        print(f"  • Successfully updated: {updated_count}")
        print(f"  • Already had varied content: {len(generators) - updated_count}")
        
        if self.updated_files:
            print(f"\n📝 Updated files:")
            for file in self.updated_files:
                print(f"  • {file.relative_to(self.project_root)}")
                
        print(f"\n💾 Backups saved to: {self.backup_dir}")
        
        return updated_count > 0


def main():
    """Main function"""
    updater = PDFGeneratorUpdater()
    
    print("🚀 PDF Generator Quality Update")
    print("=" * 60)
    print("This will update all PDF generators to use varied content")
    print("ensuring better quality and customer satisfaction.")
    print("=" * 60)
    
    # Run the update
    success = updater.update_all_generators()
    
    if success:
        print("\n✅ PDF generators have been updated!")
        print("All future PDFs will have varied instructions and tips.")
    else:
        print("\n⚠️  No generators needed updating.")
        
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())