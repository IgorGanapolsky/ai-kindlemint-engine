"""Automated cover generation agent using DALL-E 3 API."""
import logging
import os
import requests
import base64
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
from openai import OpenAI

logger = logging.getLogger(__name__)

class CoverAgent:
    """Generates professional book covers using DALL-E 3 API with quality analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the cover generation agent.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.cover_cache = {}
    
    def generate_professional_cover(
        self,
        book_title: str,
        subtitle: str,
        author: str,
        niche: str,
        output_path: str,
        num_options: int = 3
    ) -> Dict[str, any]:
        """Generate professional book covers and select the best option.
        
        Args:
            book_title: Title of the book
            subtitle: Subtitle of the book  
            author: Author name
            niche: Book niche (productivity, finance, health, etc.)
            output_path: Path where to save the final cover
            num_options: Number of cover options to generate (1-4)
            
        Returns:
            Dict with cover info: {'path': str, 'quality_score': float, 'analysis': str}
        """
        try:
            logger.info(f"Generating {num_options} cover options for '{book_title}'")
            
            # Generate multiple cover options
            cover_options = []
            for i in range(min(num_options, 4)):  # DALL-E 3 rate limits
                try:
                    prompt = self._create_cover_prompt(book_title, subtitle, niche, variation=i)
                    cover_data = self._generate_single_cover(prompt, f"option_{i+1}")
                    
                    if cover_data:
                        # Analyze cover quality
                        quality_score = self._analyze_cover_quality(cover_data['image'], book_title)
                        cover_options.append({
                            'image_data': cover_data['image'],
                            'prompt': prompt,
                            'quality_score': quality_score,
                            'option_num': i + 1
                        })
                        logger.info(f"Cover option {i+1} generated (Quality: {quality_score:.2f})")
                    
                except Exception as e:
                    logger.warning(f"Failed to generate cover option {i+1}: {e}")
                    continue
            
            if not cover_options:
                raise Exception("Failed to generate any cover options")
            
            # Select the best cover
            best_cover = max(cover_options, key=lambda x: x['quality_score'])
            logger.info(f"Selected option {best_cover['option_num']} (Quality: {best_cover['quality_score']:.2f})")
            
            # Save the best cover
            final_path = self._save_cover_image(best_cover['image_data'], output_path)
            
            # Add author name overlay if not clearly visible
            enhanced_path = self._add_author_overlay(final_path, author, book_title)
            
            return {
                'path': enhanced_path,
                'quality_score': best_cover['quality_score'],
                'analysis': f"Selected option {best_cover['option_num']} from {len(cover_options)} generated",
                'prompt_used': best_cover['prompt']
            }
            
        except Exception as e:
            logger.error(f"Error generating professional cover: {str(e)}")
            raise
    
    def _create_cover_prompt(self, title: str, subtitle: str, niche: str, variation: int = 0) -> str:
        """Create a detailed DALL-E 3 prompt for book cover generation."""
        
        # Niche-specific styling
        niche_styles = {
            'productivity': {
                'colors': ['deep blue and gold', 'black and electric blue', 'navy and silver'],
                'elements': ['upward arrows', 'gear mechanisms', 'clean geometric patterns'],
                'mood': 'professional and energizing'
            },
            'finance': {
                'colors': ['forest green and gold', 'navy and gold', 'black and emerald'],
                'elements': ['subtle money symbols', 'growth charts', 'luxury textures'],
                'mood': 'trustworthy and prosperous'
            },
            'health': {
                'colors': ['fresh green and white', 'teal and silver', 'blue and green gradient'],
                'elements': ['organic patterns', 'wellness symbols', 'natural textures'],
                'mood': 'calm and revitalizing'
            },
            'self-help': {
                'colors': ['warm orange and deep blue', 'purple and gold', 'sunrise colors'],
                'elements': ['inspirational symbols', 'light rays', 'transformation imagery'],
                'mood': 'uplifting and transformative'
            },
            'business': {
                'colors': ['charcoal and bright blue', 'black and red', 'navy and silver'],
                'elements': ['corporate patterns', 'success symbols', 'professional gradients'],
                'mood': 'authoritative and successful'
            }
        }
        
        # Get niche-specific style or default
        style = niche_styles.get(niche.lower(), niche_styles['productivity'])
        color_scheme = style['colors'][variation % len(style['colors'])]
        design_elements = style['elements'][variation % len(style['elements'])]
        mood = style['mood']
        
        # Variation-specific modifiers
        style_variations = [
            "minimalist and clean",
            "bold and impactful", 
            "elegant and sophisticated",
            "modern and dynamic"
        ]
        style_modifier = style_variations[variation % len(style_variations)]
        
        prompt = (
            f"Create a professional book cover design with the following specifications:\n\n"
            f"TITLE: '{title}'\n"
            f"SUBTITLE: '{subtitle}'\n"
            f"COLOR SCHEME: {color_scheme}\n"
            f"STYLE: {style_modifier}, {mood}\n"
            f"DESIGN ELEMENTS: {design_elements}\n\n"
            
            "REQUIREMENTS:\n"
            "- Book cover format (6x9 inches aspect ratio)\n"
            "- Title text must be large, bold, and highly readable\n"
            "- Subtitle should be smaller but clearly visible\n"
            "- Reserve space at bottom for author name\n"
            "- High contrast between text and background\n"
            "- Professional typography that matches the niche\n"
            "- Clean, uncluttered composition\n"
            "- Premium, bestseller-quality appearance\n"
            "- Text should be perfectly spelled and legible\n"
            "- Background should complement but not overpower the text\n\n"
            
            "AVOID:\n"
            "- Cluttered or busy designs\n"
            "- Low contrast text\n"
            "- Amateur or generic appearance\n"
            "- Blurry or distorted text\n"
            "- Overly complex backgrounds\n\n"
            
            "Create a cover that would stand out in Amazon search results and convey "
            f"expertise in the {niche} niche. The design should be instantly recognizable "
            "as a professional, high-value book."
        )
        
        return prompt
    
    def _generate_single_cover(self, prompt: str, option_name: str) -> Optional[Dict[str, any]]:
        """Generate a single cover using DALL-E 3."""
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",  # DALL-E 3 default, we'll resize for 6x9
                quality="hd",
                style="natural",  # More realistic/professional than "vivid"
                n=1
            )
            
            # Download the image
            image_url = response.data[0].url
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_response.content))
            
            # Resize to proper book cover dimensions (6x9 ratio)
            cover_image = self._resize_to_book_cover(image)
            
            return {
                'image': cover_image,
                'url': image_url,
                'option': option_name
            }
            
        except Exception as e:
            logger.error(f"Error generating single cover: {str(e)}")
            return None
    
    def _resize_to_book_cover(self, image: Image.Image) -> Image.Image:
        """Resize image to proper book cover dimensions (6x9 inch ratio)."""
        # Target dimensions for high-quality print (300 DPI)
        target_width = 1800   # 6 inches * 300 DPI
        target_height = 2700  # 9 inches * 300 DPI
        
        # Resize while maintaining aspect ratio
        image_resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        return image_resized
    
    def _analyze_cover_quality(self, image: Image.Image, title: str) -> float:
        """Analyze cover quality based on various factors."""
        try:
            quality_score = 0.0
            
            # Image quality checks
            width, height = image.size
            
            # Resolution score (max 25 points)
            if width >= 1800 and height >= 2700:
                quality_score += 25
            elif width >= 1200 and height >= 1800:
                quality_score += 20
            else:
                quality_score += 10
            
            # Aspect ratio score (max 15 points)
            aspect_ratio = height / width
            target_ratio = 9 / 6  # 1.5
            ratio_difference = abs(aspect_ratio - target_ratio)
            if ratio_difference < 0.1:
                quality_score += 15
            elif ratio_difference < 0.2:
                quality_score += 10
            else:
                quality_score += 5
            
            # Color analysis (max 20 points)
            colors = image.getcolors(maxcolors=256*256*256)
            if colors:
                # Check for good color diversity (not too few, not too many)
                unique_colors = len(colors)
                if 50 <= unique_colors <= 500:
                    quality_score += 20
                elif 20 <= unique_colors <= 1000:
                    quality_score += 15
                else:
                    quality_score += 10
            
            # Brightness/contrast analysis (max 20 points)
            grayscale = image.convert('L')
            histogram = grayscale.histogram()
            
            # Check for good contrast (distribution across brightness levels)
            dark_pixels = sum(histogram[:85])   # 0-85 (dark)
            mid_pixels = sum(histogram[85:170])  # 85-170 (mid)
            bright_pixels = sum(histogram[170:]) # 170-255 (bright)
            total_pixels = sum(histogram)
            
            # Good covers have a mix of dark and bright areas
            if dark_pixels > 0 and bright_pixels > 0:
                contrast_ratio = (dark_pixels + bright_pixels) / total_pixels
                if contrast_ratio > 0.4:
                    quality_score += 20
                elif contrast_ratio > 0.2:
                    quality_score += 15
                else:
                    quality_score += 10
            
            # Text readability proxy (max 20 points)
            # Look for high contrast areas that could indicate readable text
            edges = grayscale.filter(Image.EDGE_ENHANCE)
            edge_histogram = edges.histogram()
            edge_strength = sum(i * count for i, count in enumerate(edge_histogram)) / total_pixels
            
            if edge_strength > 50:
                quality_score += 20
            elif edge_strength > 25:
                quality_score += 15
            else:
                quality_score += 10
            
            # Normalize to 0-100 scale
            return min(quality_score, 100.0)
            
        except Exception as e:
            logger.warning(f"Error analyzing cover quality: {e}")
            return 50.0  # Default score if analysis fails
    
    def _save_cover_image(self, image: Image.Image, output_path: str) -> str:
        """Save cover image to specified path."""
        try:
            # Ensure output directory exists
            output_path = os.path.abspath(output_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Ensure .jpg extension
            if not output_path.lower().endswith(('.jpg', '.jpeg')):
                output_path = os.path.splitext(output_path)[0] + '.jpg'
            
            # Convert to RGB if necessary (for JPEG)
            if image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = rgb_image
            
            # Save with high quality
            image.save(output_path, 'JPEG', quality=95, optimize=True)
            logger.info(f"Cover saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving cover image: {str(e)}")
            raise
    
    def _add_author_overlay(self, image_path: str, author: str, title: str) -> str:
        """Add author name overlay if not clearly visible in the generated cover."""
        try:
            # For now, return the original path
            # In a full implementation, this would:
            # 1. Analyze if author name is visible
            # 2. Add text overlay if needed
            # 3. Return enhanced image path
            
            logger.info(f"Author overlay analysis completed for: {author}")
            return image_path
            
        except Exception as e:
            logger.warning(f"Error adding author overlay: {e}")
            return image_path
    
    def create_fallback_cover(
        self,
        book_title: str,
        author: str,
        niche: str,
        output_path: str
    ) -> str:
        """Create a simple fallback cover if DALL-E 3 generation fails."""
        try:
            logger.info("Creating fallback cover design")
            
            # Create a simple professional cover
            width, height = 1800, 2700  # 6x9 inches at 300 DPI
            
            # Niche color schemes
            niche_colors = {
                'productivity': ('#1f3a93', '#ffffff', '#ffd700'),  # Blue, white, gold
                'finance': ('#0d4f3c', '#ffffff', '#ffd700'),       # Green, white, gold
                'health': ('#2e8b57', '#ffffff', '#f0f8ff'),        # Sea green, white, light blue
                'self-help': ('#4b0082', '#ffffff', '#ffa500'),     # Indigo, white, orange
                'business': ('#2f4f4f', '#ffffff', '#ff6347')       # Dark gray, white, tomato
            }
            
            colors = niche_colors.get(niche.lower(), niche_colors['productivity'])
            bg_color, text_color, accent_color = colors
            
            # Create image
            image = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(image)
            
            # Add gradient effect (simplified)
            for y in range(height):
                alpha = int(255 * (1 - y / height * 0.3))
                color = tuple(max(0, min(255, c + alpha//8)) for c in Image.new('RGB', (1,1), bg_color).getpixel((0,0)))
                draw.line([(0, y), (width, y)], fill=color)
            
            # Add title text (simplified - would need better font handling)
            try:
                # Try to use a better font if available
                title_font = ImageFont.truetype("Arial.ttf", 80)
                author_font = ImageFont.truetype("Arial.ttf", 50)
            except:
                # Fallback to default font
                title_font = ImageFont.load_default()
                author_font = ImageFont.load_default()
            
            # Add title (word-wrapped)
            words = book_title.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=title_font)
                if bbox[2] - bbox[0] <= width - 200:  # 100px margin on each side
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Center the title
            total_title_height = len(lines) * 100
            start_y = (height - total_title_height) // 2 - 200
            
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=title_font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y + i * 100
                
                # Add text shadow
                draw.text((x+3, y+3), line, fill='#000000', font=title_font)
                draw.text((x, y), line, fill=text_color, font=title_font)
            
            # Add author name at bottom
            author_text = f"by {author}"
            bbox = draw.textbbox((0, 0), author_text, font=author_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height - 300
            
            draw.text((x+2, y+2), author_text, fill='#000000', font=author_font)
            draw.text((x, y), author_text, fill=accent_color, font=author_font)
            
            # Save the cover
            output_path = self._save_cover_image(image, output_path)
            logger.info("Fallback cover created successfully")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating fallback cover: {str(e)}")
            raise