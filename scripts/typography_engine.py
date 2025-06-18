#!/usr/bin/env python3
"""
Stage 2: Typography Engine - Add professional text overlay to background art
"""

import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

class TypographyEngine:
    def __init__(self):
        self.logger = get_logger('typography_engine')
        self.config = self._load_typography_config()
        
    def _load_typography_config(self):
        """Load typography configuration for consistent branding"""
        return {
            "canvas_size": (1024, 1024),
            "fonts": {
                "title": {
                    "family": "fonts/Montserrat-Bold.ttf",
                    "fallback": "arial",
                    "size": 48,
                    "color": "#1a365d",  # Dark blue
                    "position": (512, 200),  # Center X, Y from top
                    "align": "center",
                    "max_width": 900,
                    "line_spacing": 1.2
                },
                "subtitle": {
                    "family": "fonts/Montserrat-Regular.ttf", 
                    "fallback": "arial",
                    "size": 28,
                    "color": "#2d5aa0",  # Medium blue
                    "position": (512, 320),
                    "align": "center",
                    "max_width": 800
                },
                "volume": {
                    "family": "fonts/Montserrat-Bold.ttf",
                    "fallback": "arial", 
                    "size": 36,
                    "color": "#1a365d",
                    "position": (512, 400),
                    "align": "center"
                },
                "brand": {
                    "family": "fonts/Montserrat-Regular.ttf",
                    "fallback": "arial",
                    "size": 24,
                    "color": "#4a5568",  # Gray
                    "position": (512, 950),
                    "align": "center"
                }
            },
            "text_shadow": {
                "enabled": True,
                "offset": (2, 2),
                "color": "white",
                "blur": 0
            },
            "text_background": {
                "enabled": True,
                "color": "white",
                "opacity": 180,  # 0-255
                "padding": 20
            }
        }
    
    def create_professional_cover(self, background_path, volume_data, output_path):
        """Combine background art with professional typography"""
        
        try:
            self.logger.info(f"🖋️ Creating professional cover for Volume {volume_data.get('volume', '?')}")
            
            # Load background image
            if not Path(background_path).exists():
                raise FileNotFoundError(f"Background image not found: {background_path}")
            
            background = Image.open(background_path)
            
            # Ensure correct size
            canvas_size = self.config["canvas_size"]
            if background.size != canvas_size:
                background = background.resize(canvas_size, Image.Resampling.LANCZOS)
            
            # Convert to RGBA for text overlay
            if background.mode != 'RGBA':
                background = background.convert('RGBA')
            
            # Create text overlay
            cover = self._add_text_layers(background, volume_data)
            
            # Save final cover
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert back to RGB for final save
            final_cover = Image.new('RGB', canvas_size, (255, 255, 255))
            final_cover.paste(cover, mask=cover.split()[-1] if cover.mode == 'RGBA' else None)
            
            final_cover.save(output_path, 'PNG', quality=95, optimize=True)
            
            self.logger.info(f"✅ Professional cover created: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Cover creation failed: {e}")
            return False
    
    def _add_text_layers(self, background, volume_data):
        """Add all text layers with professional typography"""
        
        # Create drawing context
        cover = background.copy()
        
        # Add semi-transparent background for text readability
        if self.config["text_background"]["enabled"]:
            cover = self._add_text_background(cover, volume_data)
        
        # Create text overlay
        text_overlay = Image.new('RGBA', cover.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_overlay)
        
        # Add each text element
        self._draw_title(draw, volume_data.get('title', 'Large Print Crossword Masters'))
        self._draw_subtitle(draw, volume_data.get('subtitle', 'Easy Large Print Crosswords for Seniors'))
        self._draw_volume(draw, f"Volume {volume_data.get('volume', 1)}")
        self._draw_brand(draw, volume_data.get('brand', 'Senior Puzzle Studio'))
        
        # Composite text onto cover
        cover = Image.alpha_composite(cover, text_overlay)
        
        return cover
    
    def _add_text_background(self, cover, volume_data):
        """Add semi-transparent background for better text readability"""
        
        overlay = Image.new('RGBA', cover.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Text area background
        bg_config = self.config["text_background"]
        color = (*self._hex_to_rgb(bg_config["color"]), bg_config["opacity"])
        
        # Calculate text area bounds
        padding = bg_config["padding"]
        text_area = (
            50,      # Left
            150,     # Top
            cover.size[0] - 50,  # Right
            500      # Bottom
        )
        
        draw.rounded_rectangle(text_area, radius=15, fill=color)
        
        return Image.alpha_composite(cover, overlay)
    
    def _draw_title(self, draw, title):
        """Draw main title with proper wrapping and positioning"""
        font_config = self.config["fonts"]["title"]
        font = self._load_font(font_config["family"], font_config["size"])
        
        # Word wrap if needed
        wrapped_lines = self._wrap_text(title, font, font_config["max_width"])
        
        # Calculate total height for centering
        line_height = font_config["size"] * font_config["line_spacing"]
        total_height = len(wrapped_lines) * line_height
        start_y = font_config["position"][1] - (total_height / 2)
        
        # Draw each line
        for i, line in enumerate(wrapped_lines):
            y = start_y + (i * line_height)
            self._draw_text_with_shadow(
                draw, line, font, 
                (font_config["position"][0], y),
                font_config["color"],
                font_config["align"]
            )
    
    def _draw_subtitle(self, draw, subtitle):
        """Draw subtitle"""
        font_config = self.config["fonts"]["subtitle"]
        font = self._load_font(font_config["family"], font_config["size"])
        
        wrapped_lines = self._wrap_text(subtitle, font, font_config["max_width"])
        
        for i, line in enumerate(wrapped_lines):
            y = font_config["position"][1] + (i * font_config["size"] * 1.2)
            self._draw_text_with_shadow(
                draw, line, font,
                (font_config["position"][0], y),
                font_config["color"],
                font_config["align"]
            )
    
    def _draw_volume(self, draw, volume_text):
        """Draw volume number"""
        font_config = self.config["fonts"]["volume"]
        font = self._load_font(font_config["family"], font_config["size"])
        
        self._draw_text_with_shadow(
            draw, volume_text, font,
            font_config["position"],
            font_config["color"],
            font_config["align"]
        )
    
    def _draw_brand(self, draw, brand_text):
        """Draw brand name"""
        font_config = self.config["fonts"]["brand"]
        font = self._load_font(font_config["family"], font_config["size"])
        
        self._draw_text_with_shadow(
            draw, brand_text, font,
            font_config["position"],
            font_config["color"],
            font_config["align"]
        )
    
    def _draw_text_with_shadow(self, draw, text, font, position, color, align="center"):
        """Draw text with shadow for better readability"""
        
        # Get text dimensions for alignment
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Adjust position based on alignment
        x, y = position
        if align == "center":
            x = x - (text_width / 2)
        elif align == "right":
            x = x - text_width
        
        # Draw shadow first
        if self.config["text_shadow"]["enabled"]:
            shadow_offset = self.config["text_shadow"]["offset"]
            shadow_color = self.config["text_shadow"]["color"]
            shadow_pos = (x + shadow_offset[0], y + shadow_offset[1])
            draw.text(shadow_pos, text, font=font, fill=shadow_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=color)
    
    def _load_font(self, font_path, size):
        """Load font with fallback"""
        try:
            # Try to load custom font
            if Path(font_path).exists():
                return ImageFont.truetype(font_path, size)
            else:
                # Fallback to default font
                self.logger.warning(f"⚠️ Font not found: {font_path}, using default")
                return ImageFont.load_default()
        except Exception as e:
            self.logger.warning(f"⚠️ Font loading failed: {e}, using default")
            return ImageFont.load_default()
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = current_line + [word]
            test_text = ' '.join(test_line)
            
            bbox = font.getbbox(test_text)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)  # Single word too long
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def main():
    """Test typography engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add typography to background art')
    parser.add_argument('--background', type=str, required=True, help='Background image path')
    parser.add_argument('--volume', type=int, default=1, help='Volume number')
    parser.add_argument('--output', type=str, required=True, help='Output cover path')
    
    args = parser.parse_args()
    
    # Sample volume data
    volume_data = {
        'volume': args.volume,
        'title': 'Large Print Crossword Masters',
        'subtitle': 'Easy Large Print Crosswords for Seniors',
        'brand': 'Senior Puzzle Studio'
    }
    
    print("=" * 60)
    print("🖋️ TYPOGRAPHY ENGINE (Stage 2)")
    print("=" * 60)
    print(f"🎨 Background: {args.background}")
    print(f"📚 Volume: {args.volume}")
    print(f"💾 Output: {args.output}")
    print("=" * 60)
    
    engine = TypographyEngine()
    success = engine.create_professional_cover(args.background, volume_data, args.output)
    
    if success:
        print("✅ Professional cover created successfully!")
    else:
        print("❌ Cover creation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()