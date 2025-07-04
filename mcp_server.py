#!/usr/bin/env python3
"""
MCP Server for Kindlemint Puzzle Generation
Exposes puzzle generation capabilities as MCP tools
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from fastmcp import FastMCP
except ImportError:
    print("❌ FastMCP not installed. Install with: pip install fastmcp")
    sys.exit(1)

from kindlemint.agents.puzzle_generator_agent import PuzzleGeneratorAgent
from scripts.large_print_sudoku_generator import LargePrintSudokuGenerator

# Initialize MCP server
mcp = FastMCP("Kindlemint Puzzle Generator", host="0.0.0.0", port=8011)

@mcp.tool(name="generate_sudoku_book", description="Generate a complete Sudoku puzzle book ready for KDP publishing")
def generate_sudoku_book(
    title: str = "Sudoku Puzzles Volume 1",
    difficulty: str = "medium",
    puzzle_count: int = 100,
    large_print: bool = True,
    include_solutions: bool = True
) -> Dict[str, Any]:
    """
    Generate a complete Sudoku book with specified parameters.
    
    Args:
        title: Book title
        difficulty: Puzzle difficulty (easy, medium, hard)
        puzzle_count: Number of puzzles to include
        large_print: Whether to use large print format
        include_solutions: Whether to include solution pages
        
    Returns:
        Dict with status, file paths, and metadata
    """
    try:
        print(f"🚀 Generating Sudoku book: {title}")
        
        # Create output directory
        output_dir = Path(f"books/mcp_generated/{title.replace(' ', '_')}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize generator
        generator = LargePrintSudokuGenerator(str(output_dir / "puzzles"))
        
        # Generate puzzles
        print(f"📝 Creating {puzzle_count} {difficulty} puzzles...")
        puzzles = []
        for i in range(puzzle_count):
            puzzle = generator.generate_puzzle(difficulty)
            puzzles.append(puzzle)
            
        # Create PDF
        from scripts.sudoku_pdf_layout_v2 import create_book_pdf
        pdf_path = str(output_dir / f"{title.replace(' ', '_')}.pdf")
        
        # Generate the PDF with puzzles
        create_book_pdf(
            puzzles=puzzles,
            title=title,
            output_path=pdf_path,
            large_print=large_print,
            include_solutions=include_solutions
        )
        
        return {
            "status": "success",
            "title": title,
            "pdf_path": pdf_path,
            "puzzle_count": len(puzzles),
            "difficulty": difficulty,
            "large_print": large_print,
            "file_size_mb": round(os.path.getsize(pdf_path) / (1024*1024), 2) if os.path.exists(pdf_path) else 0,
            "ready_for_kdp": True
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "title": title
        }

@mcp.tool(name="generate_crossword_book", description="Generate a crossword puzzle book for KDP")
def generate_crossword_book(
    title: str = "Crossword Puzzles Volume 1",
    difficulty: str = "medium", 
    puzzle_count: int = 50,
    theme: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a crossword puzzle book.
    
    Args:
        title: Book title
        difficulty: Puzzle difficulty
        puzzle_count: Number of crosswords
        theme: Optional theme (e.g., "Animals", "Travel", "Movies")
        
    Returns:
        Dict with generation results
    """
    try:
        print(f"🎯 Generating Crossword book: {title}")
        
        # Use existing crossword generation
        from scripts.generate_crossword_volume_2_professional import main as generate_crosswords
        
        output_dir = Path(f"books/mcp_generated/{title.replace(' ', '_')}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_path = generate_crosswords(
            title=title,
            count=puzzle_count,
            difficulty=difficulty,
            theme=theme,
            output_dir=str(output_dir)
        )
        
        return {
            "status": "success",
            "title": title,
            "pdf_path": pdf_path,
            "puzzle_count": puzzle_count,
            "difficulty": difficulty,
            "theme": theme,
            "ready_for_kdp": True
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "title": title
        }

@mcp.tool(name="create_lead_magnet", description="Generate a free puzzle sampler for lead generation")
def create_lead_magnet(
    puzzle_type: str = "sudoku",
    count: int = 10,
    title: str = "Free Puzzle Sampler"
) -> Dict[str, Any]:
    """
    Create a lead magnet puzzle book for email capture.
    
    Args:
        puzzle_type: Type of puzzles (sudoku, crossword)
        count: Number of sample puzzles
        title: Lead magnet title
        
    Returns:
        Dict with lead magnet details
    """
    try:
        print(f"🎁 Creating lead magnet: {title}")
        
        from scripts.generate_lead_magnet_puzzles import main as create_lead_magnet
        
        output_dir = Path("books/lead_magnets")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_path = create_lead_magnet(
            puzzle_type=puzzle_type,
            count=count,
            title=title,
            output_dir=str(output_dir)
        )
        
        # Add QR code for email capture
        qr_code_url = f"https://your-landing-page.com/download?magnet={title.replace(' ', '_')}"
        
        return {
            "status": "success",
            "title": title,
            "pdf_path": pdf_path,
            "puzzle_type": puzzle_type,
            "count": count,
            "download_url": qr_code_url,
            "purpose": "email_capture"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "title": title
        }

@mcp.tool(name="get_book_stats", description="Get statistics about generated books")
def get_book_stats() -> Dict[str, Any]:
    """Get stats on all generated books."""
    try:
        books_dir = Path("books/mcp_generated")
        if not books_dir.exists():
            return {"total_books": 0, "books": []}
            
        books = []
        for book_dir in books_dir.iterdir():
            if book_dir.is_dir():
                pdf_files = list(book_dir.glob("*.pdf"))
                if pdf_files:
                    pdf_path = pdf_files[0]
                    size_mb = round(os.path.getsize(pdf_path) / (1024*1024), 2)
                    books.append({
                        "title": book_dir.name,
                        "pdf_path": str(pdf_path),
                        "size_mb": size_mb,
                        "created": pdf_path.stat().st_mtime
                    })
        
        return {
            "total_books": len(books),
            "books": sorted(books, key=lambda x: x["created"], reverse=True)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_books": 0
        }

if __name__ == "__main__":
    print("🤖 Starting Kindlemint MCP Server...")
    print("📚 Available tools:")
    print("  - generate_sudoku_book: Create KDP-ready Sudoku books")
    print("  - generate_crossword_book: Create crossword puzzle books") 
    print("  - create_lead_magnet: Generate free puzzle samplers")
    print("  - get_book_stats: View generated book statistics")
    print(f"🌐 Server running on http://localhost:8011")
    
    mcp.run()