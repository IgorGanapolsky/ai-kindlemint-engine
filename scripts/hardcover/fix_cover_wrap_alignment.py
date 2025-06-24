#!/usr/bin/env python3
"""
Hardcover Cover Wrap Alignment Fix
Corrects positioning issues in the KDP hardcover cover wrap based on template specifications
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

class CoverWrapAlignmentFixer:
    """Fix hardcover cover wrap alignment issues for KDP compliance"""
    
    def __init__(self):
        # KDP template dimensions from the PNG template
        self.template_width = 4199   # 13.996" × 300 DPI
        self.template_height = 3125  # 10.417" × 300 DPI
        
        # Measured from the actual KDP template
        self.spine_width_px = 126    # 0.421" × 300 DPI (from template)
        self.bleed_margin = 9        # 0.03" bleed margin
        self.safe_margin = 38        # 0.125" safe margin for text
        
        # Cover areas (measured from template)
        self.back_cover_width = 1800   # 6" × 300 DPI
        self.front_cover_width = 1800  # 6" × 300 DPI
        self.cover_height = 2700       # 9" × 300 DPI
        
        # Positioning (from template measurements)
        self.back_cover_x = 200        # Left edge with bleed
        self.spine_x = 2000            # Spine start position
        self.front_cover_x = 2126      # Front cover start position
        
        # Vertical centering
        self.cover_y = (self.template_height - self.cover_height) // 2
        
        print(f"📐 KDP Template Specifications:")
        print(f"   Canvas: {self.template_width} × {self.template_height} px")
        print(f"   Spine width: {self.spine_width_px} px (0.421\")")
        print(f"   Cover dimensions: {self.front_cover_width} × {self.cover_height} px")
        
    def load_font(self, size):
        """Load font with fallbacks"""
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/ArialMT.ttf"
        ]
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        return ImageFont.load_default()
    
    def create_corrected_cover_wrap(self, cover_source_path, output_dir):
        """Create properly aligned cover wrap"""
        
        # Load source cover
        cover_source = Image.open(cover_source_path).convert("RGB")
        
        # Create main canvas with white background
        canvas = Image.new("RGB", (self.template_width, self.template_height), "white")
        
        # === FRONT COVER (RIGHT SIDE) ===
        # Scale front cover to fit the front cover area exactly
        front_ratio = min(
            self.front_cover_width / cover_source.width,
            self.cover_height / cover_source.height
        )
        
        scaled_width = int(cover_source.width * front_ratio)
        scaled_height = int(cover_source.height * front_ratio)
        front_scaled = cover_source.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
        
        # Center the front cover in the front cover area
        front_paste_x = self.front_cover_x + (self.front_cover_width - scaled_width) // 2
        front_paste_y = self.cover_y + (self.cover_height - scaled_height) // 2
        
        canvas.paste(front_scaled, (front_paste_x, front_paste_y))
        
        # === SPINE (CENTER) ===
        # Create spine background by sampling from the front cover
        spine_sample_x = max(0, cover_source.width // 4)  # Sample from left quarter
        spine_sample = cover_source.crop((
            spine_sample_x, 0, 
            spine_sample_x + 100, cover_source.height
        ))
        spine_background = spine_sample.resize((self.spine_width_px, self.cover_height), Image.Resampling.LANCZOS)
        canvas.paste(spine_background, (self.spine_x, self.cover_y))
        
        # === BACK COVER (LEFT SIDE) ===
        # Create back cover background
        back_sample = cover_source.crop((0, 0, 300, cover_source.height))
        back_background = back_sample.resize((self.back_cover_width, self.cover_height), Image.Resampling.LANCZOS)
        
        # Apply darker overlay for text readability
        overlay = Image.new("RGBA", (self.back_cover_width, self.cover_height), (0, 0, 0, 80))
        back_with_overlay = Image.alpha_composite(
            back_background.convert("RGBA"), 
            overlay
        ).convert("RGB")
        
        canvas.paste(back_with_overlay, (self.back_cover_x, self.cover_y))
        
        # === TEXT OVERLAYS ===
        self.add_text_overlays(canvas)
        
        # Save corrected cover wrap
        output_path = Path(output_dir) / "hardcover_cover_wrap_corrected.png"
        canvas.save(output_path, "PNG", quality=95)
        
        print(f"✅ Corrected cover wrap saved: {output_path}")
        return output_path
    
    def add_text_overlays(self, canvas):
        """Add properly positioned text overlays"""
        draw = ImageDraw.Draw(canvas)
        
        # Load fonts
        spine_title_font = self.load_font(36)
        spine_publisher_font = self.load_font(20)
        back_desc_font = self.load_font(32)
        back_title_font = self.load_font(40)
        
        # === SPINE TEXT ===
        # Title on spine (vertical, centered)
        spine_title = "LARGE PRINT CROSSWORD MASTERS"
        
        # Create vertical text image
        text_img = Image.new("RGBA", (400, self.spine_width_px - 20), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        
        # Draw title with proper spacing
        text_draw.text(
            (10, (self.spine_width_px - 20) // 2), 
            spine_title, 
            font=spine_title_font, 
            fill="white", 
            anchor="lm"
        )
        
        # Rotate and position on spine
        text_rotated = text_img.rotate(90, expand=True)
        spine_text_y = self.cover_y + self.safe_margin
        spine_text_x = self.spine_x + (self.spine_width_px - text_rotated.width) // 2
        
        canvas.paste(text_rotated, (spine_text_x, spine_text_y), text_rotated)
        
        # Publisher at bottom of spine
        publisher_text = "CROSSWORD MASTERS PUBLISHING"
        pub_img = Image.new("RGBA", (300, self.spine_width_px - 20), (0, 0, 0, 0))
        pub_draw = ImageDraw.Draw(pub_img)
        pub_draw.text(
            (10, (self.spine_width_px - 20) // 2), 
            publisher_text, 
            font=spine_publisher_font, 
            fill="white", 
            anchor="lm"
        )
        
        pub_rotated = pub_img.rotate(90, expand=True)
        pub_text_y = self.cover_y + self.cover_height - pub_rotated.height - self.safe_margin
        pub_text_x = self.spine_x + (self.spine_width_px - pub_rotated.width) // 2
        
        canvas.paste(pub_rotated, (pub_text_x, pub_text_y), pub_rotated)
        
        # === BACK COVER TEXT ===
        back_text_x = self.back_cover_x + self.safe_margin
        back_text_y = self.cover_y + self.safe_margin
        back_text_width = self.back_cover_width - (2 * self.safe_margin)
        
        # Title
        draw.text(
            (back_text_x, back_text_y), 
            "LARGE PRINT\nCROSSWORD MASTERS", 
            font=back_title_font, 
            fill="white"
        )
        
        # Description
        description_lines = [
            "Rediscover the joy of crossword puzzles with",
            "Large Print Crossword Masters – Volume 1,",
            "specially designed for seniors and anyone",
            "who loves clear, readable puzzles!",
            "",
            "• 50 completely unique crossword puzzles",
            "• Extra-large print for comfortable reading",
            "• Everyday vocabulary that's familiar",
            "• Complete answer key included",
            "• Premium hardcover edition",
            "",
            "Perfect for morning coffee, evening relaxation,",
            "or as a thoughtful gift for puzzle-loving",
            "friends and family."
        ]
        
        desc_y = back_text_y + 120
        line_height = 40
        
        for line in description_lines:
            draw.text(
                (back_text_x, desc_y), 
                line, 
                font=back_desc_font, 
                fill="white"
            )
            desc_y += line_height
        
        # Barcode area (yellow area from template)
        barcode_width = int(2.0 * 300)   # 2" × 300 DPI
        barcode_height = int(1.2 * 300)  # 1.2" × 300 DPI
        barcode_x = self.back_cover_x + self.back_cover_width - barcode_width - self.safe_margin
        barcode_y = self.cover_y + self.cover_height - barcode_height - self.safe_margin
        
        # Draw barcode placeholder with proper positioning
        draw.rectangle([
            (barcode_x, barcode_y), 
            (barcode_x + barcode_width, barcode_y + barcode_height)
        ], fill="white", outline="gray", width=2)
        
        # Barcode text
        barcode_font = self.load_font(24)
        draw.text(
            (barcode_x + barcode_width//2, barcode_y + barcode_height//2), 
            "BARCODE\nPLACEHOLDER", 
            font=barcode_font, 
            fill="black", 
            anchor="mm"
        )

def main():
    """Fix the cover wrap alignment"""
    fixer = CoverWrapAlignmentFixer()
    
    # Paths
    cover_source = "books/active_production/Large_Print_Crossword_Masters/volume_1/hardcover/cover_source_1600x2560.jpg"
    output_dir = "books/active_production/Large_Print_Crossword_Masters/volume_1/hardcover"
    
    # Create corrected cover wrap
    corrected_path = fixer.create_corrected_cover_wrap(cover_source, output_dir)
    
    print(f"\n🎯 Alignment corrections applied:")
    print(f"   ✅ Spine text properly centered within {fixer.spine_width_px}px width")
    print(f"   ✅ Back cover text positioned with {fixer.safe_margin}px margins")
    print(f"   ✅ Barcode area positioned according to KDP template")
    print(f"   ✅ Front cover scaled and centered correctly")
    print(f"\n📄 Next: Export to PDF/X-1a for KDP upload")

if __name__ == "__main__":
    main()