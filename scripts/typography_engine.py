#!/usr/bin/env python3
"""
Stage 2: Typography Engine - Add professional text overlay to background art
Bulletproof text rendering with configuration-driven layout
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
        """Load typography configuration from JSON file"""
        config_path = Path("config/cover_typography.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load config file: {e}, using defaults")
        
        # Fallback to hardcoded config
        return self._get_default_config()
    
    def _get_default_config(self):
        """Default configuration as fallback"""
        return {
            "canvas_size": {"width": 1600, "height": 2560, "dpi": 300},
            "text_elements": {
                "main_title": {
                    "text": "CROSSWORD MASTERS",
                    "font_family": "fonts/Montserrat-Bold.ttf",
                    "font_size": 140,
                    "color": "#000080",
                    "position": {"x": 800, "y": 500},
                    "alignment": "center"
                }
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
            canvas_width = self.config["canvas_size"]["width"]
            canvas_height = self.config["canvas_size"]["height"]
            canvas_size = (canvas_width, canvas_height)
            
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
        if self.config.get("background", {}).get("text_safe_area", {}).get("enabled", False):
            cover = self._add_text_background(cover, volume_data)
        
        # Create text overlay
        text_overlay = Image.new('RGBA', cover.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_overlay)
        
        # Add each text element using config
        self._draw_configured_text(draw, "main_title", volume_data)
        self._draw_configured_text(draw, "large_print_banner", volume_data)
        self._draw_configured_text(draw, "volume_number", volume_data)
        self._draw_configured_text(draw, "brand_name", volume_data)
        self._draw_configured_text(draw, "puzzle_count", volume_data)
        
        # Composite text onto cover
        cover = Image.alpha_composite(cover, text_overlay)
        
        return cover
    
    def _add_text_background(self, cover, volume_data):
        """Add semi-transparent background for better text readability"""
        
        if not self.config.get("background", {}).get("text_safe_area", {}).get("enabled", False):
            return cover
            
        overlay = Image.new('RGBA', cover.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Text area background from config
        bg_config = self.config["background"]["text_safe_area"]
        try:
            color = (*self._hex_to_rgb(bg_config["color"]), bg_config["opacity"])
        except (ValueError, KeyError):
            color = (255, 255, 255, 180)
        
        # Get area from config
        area_config = bg_config.get("area", {"x": 100, "y": 400, "width": 1400, "height": 800})
        text_area = (
            area_config["x"],
            area_config["y"],
            area_config["x"] + area_config["width"],
            area_config["y"] + area_config["height"]
        )
        
        radius = bg_config.get("radius", 15)
        draw.rounded_rectangle(text_area, radius=radius, fill=color)
        
        return Image.alpha_composite(cover, overlay)
    
    def _draw_configured_text(self, draw, element_key, volume_data):
        """Draw text element based on configuration"""
        if element_key not in self.config.get("text_elements", {}):
            return
            
        element_config = self.config["text_elements"][element_key]
        
        # Get text content
        text = element_config["text"]
        if "{volume}" in text:
            text = text.format(volume=volume_data.get('volume', 1))
            
        # Load font
        font = self._load_font(element_config["font_family"], element_config["font_size"])
        
        # Get position
        pos_config = element_config["position"]
        position = (pos_config["x"], pos_config["y"])
        
        # Draw background if configured
        if element_config.get("background", {}).get("enabled", False):
            self._draw_text_background_box(draw, text, font, position, element_config)
        
        # Draw text with stroke if configured
        if element_config.get("stroke", {}).get("enabled", False):
            self._draw_text_with_stroke(
                draw, text, font, position, 
                element_config["color"], 
                element_config["stroke"],
                element_config["alignment"]
            )
        else:
            self._draw_text_simple(
                draw, text, font, position,
                element_config["color"],
                element_config["alignment"]
            )
    
    def _draw_text_background_box(self, draw, text, font, position, element_config):
        """Draw background box for text element"""
        bg_config = element_config["background"]
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate box position
        padding = bg_config.get("padding", 20)
        x, y = position
        
        if element_config["alignment"] == "center":
            box_x = x - (text_width / 2) - padding
        else:
            box_x = x - padding
            
        box_y = y - padding
        box_width = text_width + (padding * 2)
        box_height = text_height + (padding * 2)
        
        # Draw background box
        try:
            color = (*self._hex_to_rgb(bg_config["color"]), bg_config["opacity"])
        except (ValueError, KeyError):
            color = (255, 255, 255, 240)
            
        radius = bg_config.get("radius", 10)
        draw.rounded_rectangle(
            [box_x, box_y, box_x + box_width, box_y + box_height],
            radius=radius, fill=color
        )
    
    def _draw_text_with_stroke(self, draw, text, font, position, color, stroke_config, align="center"):
        """Draw text with stroke outline"""
        x, y = position
        
        # Adjust position based on alignment
        if align == "center":
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = x - (text_width / 2)
        
        # Draw stroke
        stroke_width = stroke_config.get("width", 2)
        stroke_color = stroke_config.get("color", "#FFFFFF")
        
        for adj_x in range(-stroke_width, stroke_width + 1):
            for adj_y in range(-stroke_width, stroke_width + 1):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=stroke_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=color)
    
    def _draw_text_simple(self, draw, text, font, position, color, align="center"):
        """Draw simple text without effects"""
        x, y = position
        
        if align == "center":
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = x - (text_width / 2)
        
        draw.text((x, y), text, font=font, fill=color)
    
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
        
        # Draw main text - ensure color is valid
        try:
            text_color = color if isinstance(color, (tuple, str)) else self._hex_to_rgb(color)
        except (ValueError, TypeError):
            text_color = "#1a365d"  # Fallback dark blue
            
        draw.text((x, y), text, font=font, fill=text_color)
    
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
        if not isinstance(hex_color, str):
            raise ValueError(f"Color must be string, got {type(hex_color)}")
            
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) != 6:
            raise ValueError(f"Hex color must be 6 characters, got {len(hex_color)}: {hex_color}")
            
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError as e:
            raise ValueError(f"Invalid hex color '{hex_color}': {e}")

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