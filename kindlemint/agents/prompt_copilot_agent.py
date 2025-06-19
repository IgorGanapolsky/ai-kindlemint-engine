#!/usr/bin/env python3
"""
Prompt Co-Pilot Agent - Professional Cover Prompt Generation
Replaces failed automatic cover generation with intelligent prompt creation.

ARCHITECTURE: Human-in-the-loop workflow for guaranteed quality
AGENT ROLE: Generate perfect, detailed prompts for cover creation
HUMAN ROLE: Execute prompt in preferred tool and place final cover
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger
from kindlemint.notifications.slack_notifier import SlackNotifier

class PromptCoPilotAgent:
    """Generates detailed, professional cover prompts for human execution."""
    
    def __init__(self):
        self.logger = get_logger('prompt_copilot_agent')
        self.slack_notifier = SlackNotifier()
        
    def generate_cover_prompt(self, book_data: Dict[str, Any], output_dir: Path) -> str:
        """Generate a detailed, professional cover prompt for the book.
        
        Args:
            book_data: Book information (title, volume, series, etc.)
            output_dir: Directory to save the prompt file
            
        Returns:
            Path to the generated prompt file
        """
        try:
            self.logger.info(f"🎨 Generating cover prompt for: {book_data.get('title', 'Unknown')}")
            
            # Extract book information
            title = book_data.get('title', 'Large Print Crossword Masters')
            volume = book_data.get('volume', 1)
            series_name = book_data.get('series', 'Large Print Crossword Masters')
            brand = book_data.get('brand', 'Senior Puzzle Studio')
            subtitle = book_data.get('subtitle', '50 Easy Large Print Crosswords for Seniors')
            
            # Generate the detailed prompt
            prompt = self._create_professional_prompt(
                title=title,
                volume=volume,
                series_name=series_name,
                brand=brand,
                subtitle=subtitle
            )
            
            # Save prompt to book directory
            prompt_file = output_dir / "cover_prompt.txt"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            self.logger.info(f"✅ Cover prompt saved: {prompt_file}")
            
            # Send Slack notification
            self._send_prompt_ready_notification(book_data, prompt_file)
            
            return str(prompt_file)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate cover prompt: {e}")
            raise
    
    def _create_professional_prompt(self, title: str, volume: int, series_name: str, 
                                  brand: str, subtitle: str) -> str:
        """Create a detailed, professional cover generation prompt.
        
        Based on successful prompt engineering that produces KDP-quality covers.
        """
        
        prompt = f"""Create a professional book cover for Amazon KDP with the following specifications:

BOOK INFORMATION:
- Title: "{title}"
- Volume: Volume {volume}
- Series: {series_name}
- Subtitle: "{subtitle}"
- Brand: {brand}

DESIGN REQUIREMENTS:

Visual Theme:
- Professional crossword puzzle book cover design
- Clean, modern layout optimized for seniors (55+ demographic)
- High contrast design for accessibility and thumbnail visibility
- Crossword grid imagery as primary visual element

Color Scheme:
- Primary colors: Navy blue (#000080) and bright orange (#FF6B35)
- Background: Clean white or light blue gradient
- Accent colors: Turquoise, yellow, or green for vibrancy
- Ensure senior-friendly, high-contrast color palette

Typography Hierarchy:
1. Main Title: "{title}" 
   - Large, bold, navy blue text
   - Highly readable at thumbnail size (150x240px)
   - Sans-serif font (Arial, Helvetica, or Montserrat)

2. "LARGE PRINT" Banner:
   - Prominent placement, bright orange background
   - White text with black outline
   - Make this the second most visible element

3. Volume Number: "VOLUME {volume}"
   - Clear, bold text in navy blue
   - Positioned below main title

4. Brand Name: "{brand}"
   - Smaller text at bottom
   - Professional, trustworthy appearance

Design Elements:
- Include actual crossword grid pattern (black and white squares)
- Show partially filled crossword puzzle for authenticity
- Use geometric patterns that suggest puzzle-solving
- Ensure crossword imagery is immediately recognizable

Technical Specifications:
- Dimensions: 1600 x 2560 pixels (Amazon KDP eBook cover ratio)
- Resolution: 300 DPI minimum
- Format: PNG or JPEG
- File size: Under 50MB

Accessibility Features:
- High contrast between text and background
- Large, readable fonts for senior demographic
- Clear visual hierarchy
- Thumbnail-optimized legibility (must be readable at 150x240px)

Professional Quality:
- Commercial book cover appearance
- Genre-appropriate design (puzzle/activity books)
- Amazon marketplace optimization
- Competitor-level visual quality

Target Market Considerations:
- Appeal to seniors who enjoy puzzles
- Emphasize "Large Print" as primary selling point
- Trustworthy, professional brand appearance
- Easy-to-scan design for quick decision making

CRITICAL SUCCESS FACTORS:
1. Must be immediately recognizable as a crossword book
2. "LARGE PRINT" must be highly visible
3. Professional appearance that builds trust
4. Optimized for Amazon thumbnail display
5. High contrast for senior accessibility

Generate a cover that matches the quality and professionalism of top-selling crossword books on Amazon KDP."""

        return prompt
    
    def _send_prompt_ready_notification(self, book_data: Dict[str, Any], prompt_file: Path):
        """Send Slack notification that cover prompt is ready."""
        try:
            title = book_data.get('title', 'Unknown')
            volume = book_data.get('volume', '?')
            
            message = f"""🎨 **COVER PROMPT READY FOR CREATIVE DIRECTOR**

📚 **Book**: {title} - Volume {volume}
📄 **Prompt File**: `{prompt_file.name}`
📁 **Location**: `{prompt_file.parent.name}/`

**Next Steps:**
1. Open the prompt file and copy the detailed instructions
2. Paste into ChatGPT or your preferred AI tool
3. Generate the cover image
4. Save as `cover.png` in the same directory
5. System will auto-resume KDP publishing workflow

**Workflow Status**: ⏸️ PAUSED - Waiting for cover creation"""

            self.slack_notifier.send_notification(
                message=message,
                title="Cover Prompt Ready",
                color="warning"  # Yellow color for "waiting" status
            )
            
            self.logger.info("📱 Slack notification sent - Cover prompt ready")
            
        except Exception as e:
            self.logger.warning(f"Failed to send Slack notification: {e}")
    
    def check_cover_completion(self, output_dir: Path) -> bool:
        """Check if cover.png has been added to complete the workflow.
        
        Args:
            output_dir: Directory to check for cover.png
            
        Returns:
            True if cover.png exists and workflow can resume
        """
        cover_file = output_dir / "cover.png"
        
        if cover_file.exists():
            self.logger.info(f"✅ Cover detected: {cover_file}")
            
            # Send completion notification
            self._send_cover_completion_notification(output_dir)
            return True
        
        return False
    
    def _send_cover_completion_notification(self, output_dir: Path):
        """Send notification that cover has been added and workflow can resume."""
        try:
            message = f"""✅ **COVER COMPLETED - RESUMING WORKFLOW**

📁 **Directory**: `{output_dir.name}/`
🖼️ **Cover**: `cover.png` detected
🚀 **Status**: Resuming automated KDP publishing pipeline

The system will now automatically proceed with:
1. Package preparation
2. KDP upload
3. Marketing campaign activation
4. Social media automation

**Workflow Status**: ▶️ RESUMED - Full automation active"""

            self.slack_notifier.send_notification(
                message=message,
                title="Cover Complete - Workflow Resumed",
                color="good"  # Green color for success
            )
            
            self.logger.info("📱 Slack notification sent - Cover complete, workflow resumed")
            
        except Exception as e:
            self.logger.warning(f"Failed to send completion notification: {e}")

def main():
    """Test the Prompt Co-Pilot Agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate professional cover prompt')
    parser.add_argument('--title', type=str, default='Large Print Crossword Masters',
                      help='Book title')
    parser.add_argument('--volume', type=int, default=1,
                      help='Volume number')
    parser.add_argument('--output', type=str, required=True,
                      help='Output directory for prompt file')
    
    args = parser.parse_args()
    
    # Sample book data
    book_data = {
        'title': args.title,
        'volume': args.volume,
        'series': 'Large Print Crossword Masters',
        'brand': 'Senior Puzzle Studio',
        'subtitle': f'50 Easy Large Print Crosswords for Seniors'
    }
    
    print("=" * 70)
    print("🎨 PROMPT CO-PILOT AGENT")
    print("=" * 70)
    print(f"📚 Book: {book_data['title']} - Volume {book_data['volume']}")
    print(f"📁 Output: {args.output}")
    print("=" * 70)
    
    agent = PromptCoPilotAgent()
    
    try:
        output_dir = Path(args.output)
        prompt_file = agent.generate_cover_prompt(book_data, output_dir)
        
        print(f"✅ Success! Cover prompt generated: {prompt_file}")
        print("\n📋 Next steps:")
        print("1. Open the prompt file")
        print("2. Copy prompt to ChatGPT or preferred AI tool")
        print("3. Generate cover image")
        print("4. Save as 'cover.png' in the same directory")
        print("5. System will automatically detect and resume workflow")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()