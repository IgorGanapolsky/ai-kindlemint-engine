"""
A2A PDF Layout Agent - Handles PDF generation and layout for puzzle books
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..generators.pdf_generator import PDFGenerator
from .agent import A2AAgent
from .skill import Skill


@dataclass
class PDFLayoutRequest:
    """Request structure for PDF layout generation"""

    puzzles: List[Dict[str, Any]]
    book_title: str
    book_format: str = "paperback"  # "paperback", "hardcover"
    trim_size: str = "8.5x11"  # For paperback puzzles
    include_solutions: bool = True
    include_cover: bool = True
    include_copyright: bool = True
    font_size: int = 16
    output_path: Optional[str] = None


@dataclass
class PDFLayoutResponse:
    """Response structure for PDF layout generation"""

    success: bool
    pdf_path: Optional[str] = None
    page_count: int = 0
    file_size_mb: float = 0.0
    error: Optional[str] = None
    generated_at: str = None
    metadata: Dict[str, Any] = None


class PDFLayoutAgent(A2AAgent):
    """A2A Agent that handles PDF generation and layout for puzzle books"""

    def __init__(self, registry):
        super().__init__("pdf_layout", registry)
        self.pdf_generator = PDFGenerator()
        self.logger = logging.getLogger(__name__)

        # Register capabilities
        self.add_skill(
            "create_puzzle_book",
            self._create_puzzle_book,
            "Create a complete puzzle book PDF from puzzles",
        )
        self.add_skill(
            "create_puzzle_pages",
            self._create_puzzle_pages,
            "Create just the puzzle pages without cover/copyright",
        )
        self.add_skill(
            "create_solution_pages",
            self._create_solution_pages,
            "Create solution pages for puzzles",
        )
        self.add_skill(
            "validate_pdf_layout",
            self._validate_pdf_layout,
            "Validate PDF layout meets quality standards",
        )
        self.add_skill(
            "optimize_pdf_size",
            self._optimize_pdf_size,
            "Optimize PDF file size while maintaining quality",
        )

    def add_skill(self, name: str, handler, description: str):
        """Add a skill to the agent"""
        self.skills[name] = Skill(name, handler, description)

    async def _create_puzzle_book(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete puzzle book PDF"""
        try:
            # Parse request
            layout_req = PDFLayoutRequest(**request)

            # Validate request
            validation_result = await self._validate_pdf_layout(request)
            if not validation_result["valid"]:
                return PDFLayoutResponse(
                    success=False,
                    error=f"Invalid request: {validation_result['error']}",
                ).__dict__

            # Determine output path
            if not layout_req.output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                layout_req.output_path = f"puzzle_book_{timestamp}.pdf"

            # Generate PDF
            pdf_path = await self._generate_complete_pdf(layout_req)

            if not pdf_path or not Path(pdf_path).exists():
                return PDFLayoutResponse(
                    success=False, error="Failed to generate PDF file"
                ).__dict__

            # Get file info
            file_path = Path(pdf_path)
            file_size_mb = file_path.stat().st_size / (1024 * 1024)

            # Count pages (simplified - would use PyPDF2 in real implementation)
            page_count = len(layout_req.puzzles) * 2  # Puzzle + solution page
            if layout_req.include_cover:
                page_count += 2  # Front and back cover
            if layout_req.include_copyright:
                page_count += 1

            return PDFLayoutResponse(
                success=True,
                pdf_path=str(pdf_path),
                page_count=page_count,
                file_size_mb=round(file_size_mb, 2),
                generated_at=datetime.now().isoformat(),
                metadata={
                    "book_title": layout_req.book_title,
                    "book_format": layout_req.book_format,
                    "trim_size": layout_req.trim_size,
                    "puzzle_count": len(layout_req.puzzles),
                    "font_size": layout_req.font_size,
                    "includes_solutions": layout_req.include_solutions,
                    "includes_cover": layout_req.include_cover,
                },
            ).__dict__

        except Exception as e:
            self.logger.error(f"Error creating puzzle book PDF: {e}")
            return PDFLayoutResponse(success=False, error=str(e)).__dict__

    async def _create_puzzle_pages(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create just the puzzle pages without cover/copyright"""
        try:
            layout_req = PDFLayoutRequest(**request)
            layout_req.include_cover = False
            layout_req.include_copyright = False

            return await self._create_puzzle_book(layout_req.__dict__)

        except Exception as e:
            self.logger.error(f"Error creating puzzle pages: {e}")
            return PDFLayoutResponse(success=False, error=str(e)).__dict__

    async def _create_solution_pages(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create solution pages for puzzles"""
        try:
            layout_req = PDFLayoutRequest(**request)

            # Modify request to only include solutions
            solution_puzzles = []
            for puzzle in layout_req.puzzles:
                if "solution" in puzzle:
                    solution_puzzle = puzzle.copy()
                    solution_puzzle["puzzle"] = solution_puzzle["solution"]
                    solution_puzzle["is_solution"] = True
                    solution_puzzles.append(solution_puzzle)

            layout_req.puzzles = solution_puzzles
            layout_req.include_cover = False
            layout_req.include_copyright = False

            if not layout_req.output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                layout_req.output_path = f"solutions_{timestamp}.pdf"

            result = await self._create_puzzle_book(layout_req.__dict__)
            if result["success"]:
                result["metadata"]["content_type"] = "solutions_only"

            return result

        except Exception as e:
            self.logger.error(f"Error creating solution pages: {e}")
            return PDFLayoutResponse(success=False, error=str(e)).__dict__

    async def _validate_pdf_layout(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PDF layout request"""
        try:
            # Check required fields
            if "puzzles" not in request:
                return {"valid": False, "error": "Missing required field: puzzles"}

            if "book_title" not in request:
                return {"valid": False, "error": "Missing required field: book_title"}

            # Validate puzzles
            puzzles = request["puzzles"]
            if not isinstance(puzzles, list) or len(puzzles) == 0:
                return {"valid": False, "error": "Puzzles must be a non-empty list"}

            # Validate each puzzle
            for i, puzzle in enumerate(puzzles):
                if not isinstance(puzzle, dict):
                    return {
                        "valid": False,
                        "error": f"Puzzle {i + 1} must be a dictionary",
                    }

                if "puzzle" not in puzzle:
                    return {
                        "valid": False,
                        "error": f"Puzzle {i + 1} missing 'puzzle' field",
                    }

                # Validate puzzle grid structure
                puzzle_grid = puzzle["puzzle"]
                if not isinstance(puzzle_grid, list) or len(puzzle_grid) != 9:
                    return {
                        "valid": False,
                        "error": f"Puzzle {i + 1} has invalid grid structure",
                    }

            # Validate book format
            book_format = request.get("book_format", "paperback")
            if book_format not in ["paperback", "hardcover"]:
                return {
                    "valid": False,
                    "error": "Book format must be 'paperback' or 'hardcover'",
                }

            # Validate trim size for paperback
            if book_format == "paperback":
                trim_size = request.get("trim_size", "8.5x11")
                if trim_size != "8.5x11":
                    return {
                        "valid": False,
                        "error": "Paperback puzzle books must use 8.5x11 trim size",
                    }

            # Validate font size
            font_size = request.get("font_size", 16)
            if not isinstance(font_size, int) or font_size < 12 or font_size > 24:
                return {"valid": False, "error": "Font size must be between 12 and 24"}

            return {"valid": True, "error": None}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    async def _optimize_pdf_size(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize PDF file size while maintaining quality"""
        try:
            pdf_path = request.get("pdf_path")
            if not pdf_path or not Path(pdf_path).exists():
                return {"success": False, "error": "PDF file not found"}

            # Get original size
            original_size = Path(pdf_path).stat().st_size / (1024 * 1024)

            # Optimization techniques (simplified for example)
            # In reality, would use PyPDF2 or similar for actual optimization
            optimized_path = pdf_path.replace(".pdf", "_optimized.pdf")

            # Simulate optimization
            await self._simulate_pdf_optimization(pdf_path, optimized_path)

            if Path(optimized_path).exists():
                optimized_size = Path(optimized_path).stat().st_size / (1024 * 1024)
                size_reduction = (
                    (original_size - optimized_size) / original_size
                ) * 100

                return {
                    "success": True,
                    "original_path": pdf_path,
                    "optimized_path": optimized_path,
                    "original_size_mb": round(original_size, 2),
                    "optimized_size_mb": round(optimized_size, 2),
                    "size_reduction_percent": round(size_reduction, 1),
                }
            else:
                return {"success": False, "error": "Optimization failed"}

        except Exception as e:
            self.logger.error(f"Error optimizing PDF: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_complete_pdf(self, layout_req: PDFLayoutRequest) -> str:
        """Generate the complete PDF file"""
        try:
            # This would integrate with your existing PDF generation logic
            # For now, we'll simulate the process

            pdf_config = {
                "title": layout_req.book_title,
                "puzzles": layout_req.puzzles,
                "format": layout_req.book_format,
                "trim_size": layout_req.trim_size,
                "font_size": layout_req.font_size,
                "include_solutions": layout_req.include_solutions,
                "include_cover": layout_req.include_cover,
                "include_copyright": layout_req.include_copyright,
            }

            # Generate PDF using existing PDF generator
            pdf_result = await self.pdf_generator.create_puzzle_book(pdf_config)

            return pdf_result

        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            raise

    async def _simulate_pdf_optimization(self, input_path: str, output_path: str):
        """Simulate PDF optimization (placeholder for real implementation)"""
        # In real implementation, would use PDF libraries for optimization
        # For now, just copy the file to simulate
        import shutil

        shutil.copy2(input_path, output_path)


# Factory function for easy instantiation
def create_pdf_layout_agent(registry):
    """Create and return a configured PDFLayoutAgent"""
    return PDFLayoutAgent(registry)
