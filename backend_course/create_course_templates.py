#!/usr/bin/env python3
"""
Generate puzzle templates for the $97 course
Gives students a head start with professional templates
"""

import json
import os
from datetime import datetime
from pathlib import Path

def create_course_templates():
    """Generate all templates for course students"""
    
    print("🎯 Creating Course Template Pack...")
    
    # Create output directory
    template_dir = Path("course_templates")
    template_dir.mkdir(exist_ok=True)
    
    # 1. Puzzle Book Planning Template
    planning_template = {
        "book_title": "Your Puzzle Book Title",
        "subtitle": "Engaging subtitle that sells",
        "target_audience": "Adults/Seniors/Kids",
        "puzzle_types": ["Sudoku", "Word Search", "Crossword"],
        "difficulty_levels": ["Easy", "Medium", "Hard"],
        "page_count": 120,
        "trim_size": "8.5 x 11 inches",
        "price_point": "$7.99",
        "keywords": [
            "primary keyword 1",
            "primary keyword 2",
            "long tail keyword 1",
            "long tail keyword 2"
        ],
        "competition_analysis": {
            "top_competitor_1": {
                "title": "",
                "price": "",
                "reviews": "",
                "weak_points": ""
            }
        }
    }
    
    with open(template_dir / "puzzle_book_planner.json", "w") as f:
        json.dump(planning_template, f, indent=2)
    
    # 2. Interior Page Templates (HTML/CSS)
    interior_css = """/* Professional Puzzle Book Interior Styles */

@page {
    size: 8.5in 11in;
    margin: 0.75in;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.5;
}

.puzzle-page {
    page-break-after: always;
    min-height: 9.5in;
    display: flex;
    flex-direction: column;
}

.puzzle-title {
    font-size: 24pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20pt;
}

.puzzle-number {
    font-size: 18pt;
    color: #666;
    text-align: center;
    margin-bottom: 10pt;
}

.difficulty {
    text-align: center;
    font-size: 14pt;
    color: #888;
    margin-bottom: 20pt;
}

.puzzle-grid {
    margin: 0 auto;
    border-collapse: collapse;
}

.puzzle-grid td {
    width: 40pt;
    height: 40pt;
    border: 1pt solid #333;
    text-align: center;
    font-size: 18pt;
}

.instructions {
    margin-top: auto;
    padding-top: 20pt;
    font-size: 10pt;
    text-align: center;
    color: #666;
}

/* Word Search Specific */
.wordsearch-grid {
    font-family: monospace;
    letter-spacing: 15pt;
    line-height: 2;
}

.word-list {
    columns: 3;
    column-gap: 20pt;
    margin-top: 30pt;
}

/* Solution Pages */
.solution-page {
    background-color: #f9f9f9;
}

.solution-grid td {
    font-size: 14pt;
    color: #666;
}
"""
    
    with open(template_dir / "interior_styles.css", "w") as f:
        f.write(interior_css)
    
    # 3. Cover Design Guidelines
    cover_guidelines = """# Cover Design Template Guidelines

## Dimensions (for 8.5 x 11 paperback)
- Front Cover: 8.5" x 11"
- Spine Width: Calculate based on page count (0.002252" per page)
- Back Cover: 8.5" x 11"
- Bleed: 0.125" on all sides

## Color Psychology for Puzzle Books
- **Blue**: Trust, intelligence (good for Sudoku)
- **Green**: Growth, harmony (good for nature-themed puzzles)
- **Purple**: Creativity, wisdom (good for premium books)
- **Orange**: Energy, enthusiasm (good for kids' books)

## Typography Rules
- Title: Bold, Sans-serif, 72pt+
- Subtitle: Light, Sans-serif, 36pt
- Author: Medium, 24pt
- Spine: Readable at thumbnail size

## Essential Elements
1. Clear puzzle type identification
2. Difficulty level indicator
3. Number of puzzles
4. Large print callout (if applicable)
5. Professional typography
6. High contrast for readability

## Canva Template Setup
1. Create new design: 8.75" x 11.25" (includes bleed)
2. Add guides at 0.125" from each edge
3. Keep all text within guides
4. Export as PDF with bleed marks
"""
    
    with open(template_dir / "cover_design_guidelines.md", "w") as f:
        f.write(cover_guidelines)
    
    # 4. Keyword Research Template
    keyword_template = {
        "primary_keywords": {
            "sudoku puzzles": {
                "search_volume": "40,500/month",
                "competition": "Medium",
                "suggested_books": []
            },
            "large print sudoku": {
                "search_volume": "8,100/month",
                "competition": "Low",
                "suggested_books": []
            }
        },
        "long_tail_keywords": [
            "sudoku puzzles for adults large print",
            "easy sudoku puzzles for beginners",
            "sudoku puzzle books for seniors with dementia"
        ],
        "title_formulas": [
            "{Puzzle Type} Puzzles for {Audience}: {Number} {Difficulty} Puzzles",
            "Large Print {Puzzle Type}: {Special Feature} Edition",
            "{Number} {Puzzle Type} Puzzles: {Difficulty} Level with Solutions"
        ],
        "profitable_niches": [
            "Seniors/Large Print",
            "Kids/Educational",
            "Travel/Portable",
            "Themed (Holidays, Seasons)",
            "Difficulty-Specific (Expert Only)"
        ]
    }
    
    with open(template_dir / "keyword_research_template.json", "w") as f:
        json.dump(keyword_template, f, indent=2)
    
    # 5. Quick Start Checklist
    checklist = """# 🚀 Your First Puzzle Book in 7 Days

## Day 1: Research & Planning
- [ ] Choose your puzzle type (Sudoku, Word Search, or Crossword)
- [ ] Identify your target audience
- [ ] Research top 10 competitors
- [ ] Select 7 main keywords
- [ ] Decide on book size and page count

## Day 2: Content Creation
- [ ] Generate 100-120 puzzles
- [ ] Create answer keys
- [ ] Write introduction page
- [ ] Add instructions/how-to section

## Day 3: Interior Formatting
- [ ] Set up page size and margins
- [ ] Format puzzle pages
- [ ] Format solution pages
- [ ] Add page numbers
- [ ] Create table of contents

## Day 4: Cover Design
- [ ] Create cover in Canva using template
- [ ] Design spine with title
- [ ] Write back cover copy
- [ ] Export as print-ready PDF

## Day 5: KDP Setup
- [ ] Create KDP account (if needed)
- [ ] Start new paperback project
- [ ] Enter book details and keywords
- [ ] Upload interior PDF
- [ ] Upload cover PDF

## Day 6: Final Review
- [ ] Order author proof copy
- [ ] Review digital previewer
- [ ] Check all formatting
- [ ] Verify solutions are correct
- [ ] Set pricing

## Day 7: Launch!
- [ ] Publish your book
- [ ] Share in course community
- [ ] Plan your next book
- [ ] Celebrate! 🎉

## Bonus Tasks:
- [ ] Create author central profile
- [ ] Request reviews from friends
- [ ] Plan a series (3-5 books)
- [ ] Set up Amazon ads ($5/day)
"""
    
    with open(template_dir / "7_day_quickstart_checklist.md", "w") as f:
        f.write(checklist)
    
    # 6. Profitable Puzzle Formulas
    formulas = {
        "sudoku_formula": {
            "easy": {
                "clues": 38-45,
                "solving_time": "5-10 minutes",
                "techniques": ["Single candidates", "Naked singles"]
            },
            "medium": {
                "clues": 30-37,
                "solving_time": "10-20 minutes",
                "techniques": ["Hidden singles", "Naked pairs"]
            },
            "hard": {
                "clues": 25-29,
                "solving_time": "20-40 minutes",
                "techniques": ["Pointing pairs", "Box/line reduction"]
            }
        },
        "word_search_formula": {
            "grid_size": "15x15 for standard, 20x20 for large print",
            "word_count": "15-20 words per puzzle",
            "word_length": "4-10 letters",
            "directions": "8 directions for adults, 4 for kids",
            "themes": ["Seasonal", "Educational", "Pop culture", "Hobbies"]
        },
        "series_formula": {
            "volume_1": "Easy - Build audience",
            "volume_2": "Medium - Retain readers",
            "volume_3": "Hard - Premium pricing",
            "volume_4": "Mixed - Best seller",
            "volume_5": "Special edition - Higher price"
        }
    }
    
    with open(template_dir / "profitable_puzzle_formulas.json", "w") as f:
        json.dump(formulas, f, indent=2)
    
    print(f"✅ Created 6 template files in {template_dir}/")
    print("\n📁 Template Pack Contents:")
    print("- Puzzle Book Planner (JSON)")
    print("- Interior Styles (CSS)")
    print("- Cover Design Guidelines (MD)")
    print("- Keyword Research Template (JSON)")
    print("- 7-Day Quick Start Checklist (MD)")
    print("- Profitable Puzzle Formulas (JSON)")
    
    return template_dir

if __name__ == "__main__":
    create_course_templates()