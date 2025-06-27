#!/usr/bin/env python3
"""
KDP Cover Calculator Integration
Calculates exact cover dimensions based on KDP specifications.
"""

import json
from pathlib import Path
from typing import Dict, Tuple, Optional


class KDPCoverCalculator:
    """Calculate KDP book cover dimensions."""
    
    # Constants from KDP specifications
    BLEED = 0.125  # inches on all sides
    PAPERBACK_PAPER_THICKNESS = 0.0025  # inches per page
    HARDCOVER_ADDITIONAL_SPINE = 0.06  # additional spine width for hardcover
    
    def __init__(self):
        """Initialize the calculator."""
        self.supported_trim_sizes = {
            "5x8": (5.0, 8.0),
            "5.5x8.5": (5.5, 8.5),
            "6x9": (6.0, 9.0),
            "6.14x9.21": (6.14, 9.21),
            "6.69x9.61": (6.69, 9.61),
            "7x10": (7.0, 10.0),
            "7.44x9.69": (7.44, 9.69),
            "7.5x9.25": (7.5, 9.25),
            "8x10": (8.0, 10.0),
            "8.25x11": (8.25, 11.0),
            "8.5x11": (8.5, 11.0),
            "8.5x8.5": (8.5, 8.5)
        }
    
    def calculate_spine_width(self, page_count: int, binding_type: str = "paperback") -> float:
        """
        Calculate spine width based on page count and binding type.
        
        Args:
            page_count: Number of pages in the book
            binding_type: "paperback" or "hardcover"
            
        Returns:
            Spine width in inches
        """
        base_spine = page_count * self.PAPERBACK_PAPER_THICKNESS
        
        if binding_type.lower() == "hardcover":
            return round(base_spine + self.HARDCOVER_ADDITIONAL_SPINE, 3)
        else:
            return round(base_spine, 3)
    
    def calculate_full_cover_dimensions(
        self, 
        trim_size: str, 
        page_count: int, 
        binding_type: str = "paperback"
    ) -> Dict[str, float]:
        """
        Calculate full wraparound cover dimensions.
        
        Args:
            trim_size: Book trim size (e.g., "8.5x11", "6x9")
            page_count: Number of pages
            binding_type: "paperback" or "hardcover"
            
        Returns:
            Dictionary with dimension details
        """
        if trim_size not in self.supported_trim_sizes:
            raise ValueError(f"Unsupported trim size: {trim_size}")
        
        width, height = self.supported_trim_sizes[trim_size]
        spine_width = self.calculate_spine_width(page_count, binding_type)
        
        # Calculate full dimensions
        full_width = (width * 2) + spine_width + (self.BLEED * 2)
        full_height = height + (self.BLEED * 2)
        
        return {
            "trim_size": trim_size,
            "page_count": page_count,
            "binding_type": binding_type,
            "spine_width": spine_width,
            "full_width": round(full_width, 3),
            "full_height": round(full_height, 3),
            "bleed": self.BLEED,
            "page_width": width,
            "page_height": height,
            "barcode_area": {
                "width": 2.0,
                "height": 1.2,
                "position": "back_cover_bottom_right"
            }
        }
    
    def generate_dall_e_prompt(
        self, 
        title: str, 
        volume: int, 
        dimensions: Dict[str, float]
    ) -> str:
        """
        Generate a complete DALL-E prompt with correct dimensions.
        
        Args:
            title: Book title
            volume: Volume number
            dimensions: Dimension dictionary from calculate_full_cover_dimensions
            
        Returns:
            Complete DALL-E prompt
        """
        binding = dimensions["binding_type"].title()
        
        prompt = f"""Create a professional FULL WRAPAROUND book cover for "{title} Volume {volume}" - a large print crossword puzzle book.

CRITICAL: This is a complete wraparound cover (back + spine + front) for {binding.lower()} binding.
Full cover dimensions: {dimensions['full_width']}" wide × {dimensions['full_height']}" tall (includes 0.125" bleed on all edges)
Spine width: {dimensions['spine_width']}" (centered in the design)
Book format: {dimensions['trim_size'].replace('x', ' × ')} inches {binding.lower()}

Design requirements:
- Back cover (left side): Book description area, barcode space (2" × 1.2")
- Spine (center, {dimensions['spine_width']}" wide): Title and volume number readable when shelved
- Front cover (right side): Main design with title "{title}", "Volume {volume}", and "LARGE PRINT" badge

Visual elements:
- Clean, modern design suitable for seniors
- Large, bold typography with high contrast
- Subtle crossword grid pattern in background
- Professional color scheme (blues, greens, or warm colors)
- Minimalist style that prints well at 300 DPI

Style: Professional, clean, accessible, senior-friendly
Format: Full wraparound cover ready for KDP printing"""
        
        return prompt
    
    def save_dimensions_report(
        self, 
        output_path: str, 
        dimensions_list: list
    ) -> None:
        """
        Save a dimensions report to a JSON file.
        
        Args:
            output_path: Path to save the report
            dimensions_list: List of dimension dictionaries
        """
        report = {
            "generator": "KDP Cover Calculator",
            "specifications": {
                "bleed": self.BLEED,
                "paperback_paper_thickness": self.PAPERBACK_PAPER_THICKNESS,
                "hardcover_additional_spine": self.HARDCOVER_ADDITIONAL_SPINE
            },
            "dimensions": dimensions_list
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def validate_page_count(self, page_count: int) -> bool:
        """
        Validate page count is within KDP limits.
        
        Args:
            page_count: Number of pages
            
        Returns:
            True if valid, False otherwise
        """
        # KDP limits for different binding types
        if page_count < 24:
            return False
        if page_count > 828:  # Maximum for paperback
            return False
        return True


def main():
    """Example usage and tests."""
    calculator = KDPCoverCalculator()
    
    # Test data for Large Print Crossword Masters series
    books = [
        {"volume": 1, "pages": 104, "paperback_trim": "8.5x11", "hardcover_trim": "6x9"},
        {"volume": 2, "pages": 112, "paperback_trim": "8.5x11", "hardcover_trim": "6x9"},
        {"volume": 3, "pages": 107, "paperback_trim": "8.5x11", "hardcover_trim": "6x9"},
        {"volume": 4, "pages": 156, "paperback_trim": "8.5x11", "hardcover_trim": "6x9"},
    ]
    
    print("KDP Cover Dimension Calculator")
    print("=" * 60)
    
    all_dimensions = []
    
    for book in books:
        print(f"\nVolume {book['volume']} ({book['pages']} pages):")
        print("-" * 40)
        
        # Calculate paperback dimensions
        pb_dims = calculator.calculate_full_cover_dimensions(
            book["paperback_trim"], book["pages"], "paperback"
        )
        print(f"Paperback ({book['paperback_trim']}):")
        print(f"  Spine: {pb_dims['spine_width']}\"")
        print(f"  Full Cover: {pb_dims['full_width']}\" × {pb_dims['full_height']}\"")
        
        # Calculate hardcover dimensions
        hc_dims = calculator.calculate_full_cover_dimensions(
            book["hardcover_trim"], book["pages"], "hardcover"
        )
        print(f"Hardcover ({book['hardcover_trim']}):")
        print(f"  Spine: {hc_dims['spine_width']}\"")
        print(f"  Full Cover: {hc_dims['full_width']}\" × {hc_dims['full_height']}\"")
        
        all_dimensions.extend([pb_dims, hc_dims])
    
    # Save report
    output_path = "kdp_cover_dimensions_report.json"
    calculator.save_dimensions_report(output_path, all_dimensions)
    print(f"\nDimensions report saved to: {output_path}")
    
    # Example DALL-E prompt
    print("\n" + "=" * 60)
    print("Example DALL-E Prompt for Volume 1 Hardcover:")
    print("-" * 60)
    dims = calculator.calculate_full_cover_dimensions("6x9", 104, "hardcover")
    prompt = calculator.generate_dall_e_prompt("Large Print Crossword Masters", 1, dims)
    print(prompt)


if __name__ == "__main__":
    main()