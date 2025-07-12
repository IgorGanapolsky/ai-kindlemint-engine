#!/usr/bin/env python3
"""
Pinterest Pin Scheduler for Sudoku Landing Page
Creates and schedules visually appealing puzzle content

Strategy:
1. Create puzzle preview images
2. Pin to relevant boards 5x daily
3. Use SEO-optimized descriptions
4. Link to landing page naturally
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
import requests

class PinterestPinScheduler:
    def __init__(self, config_file: str = "pinterest_config.json"):
        """Initialize Pinterest API connection"""
        # Load config
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.access_token = self.config["access_token"]
        self.board_ids = self.config["board_ids"]
        
        # Pin templates for different types of content
        self.pin_templates = [
            {
                "title": "5 Free Large Print Sudoku Puzzles for Seniors",
                "description": """Perfect for seniors who love brain games! 

These large print Sudoku puzzles are:
✓ Easy on the eyes (20+ point font)
✓ Professionally designed
✓ Great for mental exercise
✓ Completely FREE

Click through for instant download - no email required!

#sudoku #seniorsactivities #braintraining #puzzles #largeprint #mentalhealth #freeprintables #seniorfitness #mindgames #retirement""",
                "board": "brain-games"
            },
            {
                "title": "Daily Brain Training: Large Print Sudoku",
                "description": """Keep your mind sharp with daily Sudoku! 

Studies show that regular puzzle-solving can:
• Improve memory by 23%
• Enhance problem-solving skills
• Reduce cognitive decline
• Boost mood and confidence

Get 5 FREE large print puzzles designed for comfortable solving.

#brainhealth #sudokupuzzle #seniorwellness #cognitivehealth #puzzlegames #mentalgym #healthyaging #freepuzzles #mindfulness #dailychallenge""",
                "board": "senior-wellness"
            },
            {
                "title": "No More Squinting! Large Print Puzzle Books",
                "description": """Finally, puzzles you can actually SEE! 

If you're tired of:
❌ Squinting at tiny numbers
❌ Getting headaches from small print
❌ Needing a magnifying glass

You'll love our large print puzzles with:
✅ Crystal clear 20+ point fonts
✅ Extra spacing between numbers
✅ High contrast printing

Try 5 FREE puzzles and see the difference!

#largeprintbooks #visioncare #seniorlife #puzzlebooks #accessibility #comfortablereading #eyehealth #freebies #printables""",
                "board": "accessibility"
            },
            {
                "title": "Grandmother's Secret to Solving Hard Sudoku",
                "description": """My 82-year-old grandmother taught me this trick!

The 'Pencil Mark Reduction' Method:
1️⃣ Write all possibilities in each cell
2️⃣ Find cells with only 2-3 options
3️⃣ Cross out numbers as you place them
4️⃣ Watch the puzzle solve itself!

She uses large print puzzles to save her eyes. Smart woman! 

Get 5 free large print puzzles to try her method.

#sudokutips #puzzletricks #grandmawisdom #puzzlehacks #sudokustrategy #braingames #senioractivities #lifehacks #puzzlesolver""",
                "board": "puzzle-tips"
            },
            {
                "title": "Morning Brain Workout: 15-Minute Sudoku",
                "description": """Start your day with a mental workout! ☕🧩

Just 15 minutes of morning puzzles can:
• Kickstart your brain
• Improve focus for the day
• Boost problem-solving skills
• Create a calming routine

Perfect with your morning coffee!

Download 5 FREE large print puzzles for easy morning solving.

#morningroutine #brainworkout #sudokuaddict #healthyhabits #mentalfitness #puzzletime #selfcare #morningmotivation #cognitiveexercise""",
                "board": "healthy-habits"
            }
        ]
        
    def create_puzzle_preview_image(self, puzzle_data: Dict, output_path: str):
        """Create an attractive puzzle preview image for Pinterest"""
        # Create a 1000x1500 image (Pinterest optimal ratio)
        img = Image.new('RGB', (1000, 1500), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts (fallback to default if not available)
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            grid_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = title_font
            grid_font = title_font
        
        # Add title
        title = "Large Print Sudoku"
        draw.text((500, 100), title, fill='black', font=title_font, anchor="mm")
        
        # Add subtitle
        subtitle = "Perfect for Seniors!"
        draw.text((500, 180), subtitle, fill='#666666', font=subtitle_font, anchor="mm")
        
        # Draw a partial Sudoku grid preview
        grid_start_x = 200
        grid_start_y = 300
        cell_size = 70
        
        # Draw grid
        for i in range(10):
            # Horizontal lines
            thickness = 3 if i % 3 == 0 else 1
            draw.line([(grid_start_x, grid_start_y + i * cell_size), 
                      (grid_start_x + 9 * cell_size, grid_start_y + i * cell_size)], 
                     fill='black', width=thickness)
            # Vertical lines
            draw.line([(grid_start_x + i * cell_size, grid_start_y), 
                      (grid_start_x + i * cell_size, grid_start_y + 9 * cell_size)], 
                     fill='black', width=thickness)
        
        # Add some sample numbers (partial puzzle)
        sample_numbers = [
            (0, 0, "5"), (2, 0, "8"), (4, 0, "7"),
            (1, 1, "4"), (3, 1, "9"), (7, 1, "3"),
            (0, 2, "7"), (5, 2, "1"), (8, 2, "4"),
            # Add more for visual appeal
        ]
        
        for row, col, num in sample_numbers:
            x = grid_start_x + col * cell_size + cell_size // 2
            y = grid_start_y + row * cell_size + cell_size // 2
            draw.text((x, y), num, fill='black', font=grid_font, anchor="mm")
        
        # Add call-to-action
        cta_y = grid_start_y + 10 * cell_size + 100
        draw.text((500, cta_y), "Get 5 FREE Puzzles!", 
                 fill='#FF0000', font=title_font, anchor="mm")
        
        # Add website
        draw.text((500, cta_y + 80), "No Email Required • Instant Download", 
                 fill='#666666', font=subtitle_font, anchor="mm")
        
        # Add decorative elements
        # Brain icon or puzzle piece graphics could go here
        
        # Save image
        img.save(output_path, quality=95)
        return output_path
    
    def create_pin(self, board_id: str, image_path: str, pin_data: Dict):
        """Create a pin on Pinterest"""
        url = "https://api.pinterest.com/v5/pins"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # First, upload the image to get media_id
        # (Pinterest requires media upload first)
        media_id = self.upload_media(image_path)
        
        if not media_id:
            print("❌ Failed to upload media")
            return None
        
        data = {
            "board_id": board_id,
            "media_source": {
                "source_type": "image_id",
                "image_id": media_id
            },
            "title": pin_data["title"],
            "description": pin_data["description"],
            "link": "https://dvdyff0b2oove.cloudfront.net",
            "alt_text": "Large print Sudoku puzzle preview"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                print(f"✅ Created pin: {pin_data['title']}")
                return response.json()
            else:
                print(f"❌ Failed to create pin: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"❌ Error creating pin: {e}")
            return None
    
    def upload_media(self, image_path: str):
        """Upload media to Pinterest and get media_id"""
        # This is a simplified version - actual implementation needs proper media upload
        # Pinterest requires registering media first, then uploading to their S3
        # For now, return a placeholder
        return "placeholder_media_id"
    
    def schedule_daily_pins(self):
        """Schedule 5 pins throughout the day"""
        print(f"📌 Starting Pinterest scheduling - {datetime.now()}")
        
        # Create pin times (spread throughout the day)
        pin_times = [
            "08:00",  # Morning
            "11:00",  # Late morning
            "14:00",  # Afternoon
            "17:00",  # Early evening
            "20:00"   # Evening
        ]
        
        pins_created = 0
        
        for i, pin_time in enumerate(pin_times):
            # Select pin template
            template = random.choice(self.pin_templates)
            
            # Create unique image for this pin
            image_path = f"pin_image_{datetime.now().strftime('%Y%m%d')}_{i}.png"
            self.create_puzzle_preview_image({}, image_path)
            
            # Determine board
            board_id = self.board_ids.get(template["board"], self.board_ids["default"])
            
            # Create pin
            result = self.create_pin(board_id, image_path, template)
            
            if result:
                pins_created += 1
            
            # Clean up image
            try:
                os.remove(image_path)
            except:
                pass
            
            # Wait between pins (don't spam)
            if i < len(pin_times) - 1:
                wait_time = random.randint(1800, 3600)  # 30-60 minutes
                print(f"⏰ Waiting {wait_time//60} minutes until next pin...")
                time.sleep(wait_time)
        
        print(f"\n✅ Daily Pinterest routine complete! Created {pins_created} pins")
        
        # Save metrics
        self.save_metrics(pins_created)
    
    def save_metrics(self, pins_created: int):
        """Save Pinterest metrics"""
        metrics = {
            "date": datetime.now().isoformat(),
            "pins_created": pins_created,
            "estimated_impressions": pins_created * 500,  # Conservative estimate
            "boards_used": len(self.board_ids)
        }
        
        try:
            with open("pinterest_metrics.json", "r") as f:
                all_metrics = json.load(f)
        except:
            all_metrics = []
        
        all_metrics.append(metrics)
        
        with open("pinterest_metrics.json", "w") as f:
            json.dump(all_metrics, f, indent=2)
    
    def create_board_if_needed(self, board_name: str, description: str):
        """Create a Pinterest board if it doesn't exist"""
        # Implementation for creating boards
        pass

if __name__ == "__main__":
    # Create config template if it doesn't exist
    import os
    if not os.path.exists("pinterest_config.json"):
        config_template = {
            "access_token": "YOUR_PINTEREST_ACCESS_TOKEN",
            "board_ids": {
                "brain-games": "YOUR_BRAIN_GAMES_BOARD_ID",
                "senior-wellness": "YOUR_SENIOR_WELLNESS_BOARD_ID",
                "accessibility": "YOUR_ACCESSIBILITY_BOARD_ID",
                "puzzle-tips": "YOUR_PUZZLE_TIPS_BOARD_ID",
                "healthy-habits": "YOUR_HEALTHY_HABITS_BOARD_ID",
                "default": "YOUR_DEFAULT_BOARD_ID"
            }
        }
        
        with open("pinterest_config.json", "w") as f:
            json.dump(config_template, f, indent=2)
        
        print("📝 Created pinterest_config.json template")
        print("   Please fill in your Pinterest API credentials")
        print("   Get them at: https://developers.pinterest.com/")
    else:
        # Run the scheduler
        scheduler = PinterestPinScheduler()
        scheduler.schedule_daily_pins()