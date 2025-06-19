#!/usr/bin/env python3
"""
Stage 1: Art Director - Generate TEXT-FREE background art using AI
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

class BackgroundArtGenerator:
    def __init__(self):
        self.logger = get_logger('background_art_generator')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.openai_api_key and not self.gemini_api_key:
            raise ValueError("No AI API keys found. Need OPENAI_API_KEY or GEMINI_API_KEY")
    
    def generate_crossword_background(self, volume_number, series_theme="crossword"):
        """Generate TEXT-FREE background art optimized for text overlay"""
        
        # Create prompt focused ONLY on background art - NO TEXT
        art_prompt = self._create_background_prompt(volume_number, series_theme)
        
        # Try DALL-E first, fallback to Gemini
        background_path = None
        
        if self.openai_api_key:
            background_path = self._generate_with_dalle(art_prompt, volume_number)
        
        if not background_path and self.gemini_api_key:
            background_path = self._generate_with_gemini(art_prompt, volume_number)
        
        if background_path:
            self.logger.info(f"✅ Background art generated: {background_path}")
            return background_path
        else:
            self.logger.error("❌ Failed to generate background art with any provider")
            return None
    
    def _create_background_prompt(self, volume_number, series_theme):
        """Create art-focused prompt with NO TEXT requests"""
        
        base_prompts = {
            "crossword": [
                "Clean geometric pattern with crossword grid theme. Calming blue and turquoise gradient background. Modern abstract design. Empty grid squares only - absolutely no letters, numbers, or text of any kind.",
                
                "Abstract crossword-inspired pattern. Soft yellow to green gradient. Geometric grid design with empty squares. Professional book cover background - no text, no letters, no words whatsoever.",
                
                "Minimalist crossword grid pattern. Blue to white gradient background. Simple geometric squares arranged in grid formation. Pure background art - zero text or lettering allowed.",
                
                "Modern geometric background with crossword theme. Green and turquoise gradient. Clean grid pattern with empty squares only. Background artwork with no text elements.",
                
                "Professional crossword-inspired background. Calming blue gradient. Abstract grid pattern design. Clean background art - absolutely no text, letters, or words included."
            ]
        }
        
        prompts = base_prompts.get(series_theme, base_prompts["crossword"])
        prompt_index = (volume_number - 1) % len(prompts)
        selected_prompt = prompts[prompt_index]
        
        # Add bulletproof NO TEXT enforcement
        final_prompt = f"{selected_prompt} CRITICAL: Generate ONLY the background pattern. Do NOT include any text, letters, numbers, words, titles, or readable characters. The image must be completely text-free as text will be added separately using code."
        
        self.logger.info(f"🎨 Art prompt for Volume {volume_number}: {final_prompt[:100]}...")
        return final_prompt
    
    def _generate_with_dalle(self, prompt, volume_number):
        """Generate background using DALL-E 3"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            self.logger.info(f"🎨 Generating background art with DALL-E for Volume {volume_number}...")
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",
                quality="standard",
                n=1
            )
            
            # Download the image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            
            if image_response.status_code == 200:
                # Save as background art (not final cover)
                output_dir = Path("output/background_art")
                output_dir.mkdir(exist_ok=True)
                
                background_path = output_dir / f"background_vol_{volume_number}.png"
                with open(background_path, 'wb') as f:
                    f.write(image_response.content)
                
                self.logger.info(f"✅ DALL-E background saved: {background_path}")
                return str(background_path)
            else:
                self.logger.error(f"❌ Failed to download DALL-E image: {image_response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ DALL-E generation failed: {e}")
            return None
    
    def _generate_with_gemini(self, prompt, volume_number):
        """Generate background using Gemini (placeholder for now)"""
        try:
            # Note: Gemini doesn't have direct image generation yet
            # This is a placeholder for when it becomes available
            # For now, we'll create a simple gradient background
            
            self.logger.info(f"🎨 Creating gradient background for Volume {volume_number}...")
            return self._create_gradient_background(volume_number)
            
        except Exception as e:
            self.logger.error(f"❌ Gemini generation failed: {e}")
            return None
    
    def _create_gradient_background(self, volume_number):
        """Create a simple gradient background as fallback"""
        try:
            from PIL import Image, ImageDraw
            
            # Create gradient background
            width, height = 1024, 1024
            image = Image.new('RGB', (width, height), '#ffffff')
            draw = ImageDraw.Draw(image)
            
            # Define color schemes for different volumes
            color_schemes = [
                ('#e3f2fd', '#1976d2'),  # Light blue to blue
                ('#e8f5e8', '#2e7d32'),  # Light green to green  
                ('#fff3e0', '#f57c00'),  # Light orange to orange
                ('#f3e5f5', '#7b1fa2'),  # Light purple to purple
                ('#ffebee', '#c62828'),  # Light red to red
            ]
            
            scheme_index = (volume_number - 1) % len(color_schemes)
            light_color, dark_color = color_schemes[scheme_index]
            
            # Create vertical gradient
            for y in range(height):
                # Calculate blend ratio
                ratio = y / height
                
                # Blend colors
                light_rgb = tuple(int(light_color[i:i+2], 16) for i in (1, 3, 5))
                dark_rgb = tuple(int(dark_color[i:i+2], 16) for i in (1, 3, 5))
                
                blended = tuple(int(light_rgb[i] + (dark_rgb[i] - light_rgb[i]) * ratio) for i in range(3))
                
                draw.line([(0, y), (width, y)], fill=blended)
            
            # Add subtle grid pattern
            grid_color = (255, 255, 255, 30)  # Very light white
            grid_spacing = 50
            
            for x in range(0, width, grid_spacing):
                draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
            for y in range(0, height, grid_spacing):
                draw.line([(0, y), (width, y)], fill=grid_color, width=1)
            
            # Save background
            output_dir = Path("output/background_art")
            output_dir.mkdir(exist_ok=True)
            
            background_path = output_dir / f"background_vol_{volume_number}.png"
            image.save(background_path, 'PNG')
            
            self.logger.info(f"✅ Gradient background created: {background_path}")
            return str(background_path)
            
        except Exception as e:
            self.logger.error(f"❌ Gradient background creation failed: {e}")
            return None

def main():
    """Test background art generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate background art for book covers')
    parser.add_argument('--volume', type=int, default=1, help='Volume number')
    parser.add_argument('--theme', type=str, default='crossword', help='Series theme')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎨 BACKGROUND ART GENERATOR (Stage 1)")
    print("=" * 60)
    print(f"📚 Volume: {args.volume}")
    print(f"🎭 Theme: {args.theme}")
    print("=" * 60)
    
    generator = BackgroundArtGenerator()
    background_path = generator.generate_crossword_background(args.volume, args.theme)
    
    if background_path:
        print(f"✅ Background art ready: {background_path}")
        print("🔄 Ready for Stage 2: Text overlay")
    else:
        print("❌ Background art generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()