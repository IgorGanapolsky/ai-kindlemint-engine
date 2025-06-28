#!/usr/bin/env python3
"""
Add back cover DALL-E prompts to all physical books (paperback and hardcover)
"""

import json
import os
import glob
from pathlib import Path
from typing import Dict, Any


def generate_back_cover_prompt(metadata: Dict[str, Any]) -> str:
    """Generate a professional back cover prompt based on book metadata"""
    title = metadata.get("title", "Book Title")
    subtitle = metadata.get("subtitle", "")
    author = metadata.get("author", "Author Name")
    description = metadata.get("description", "")
    
    # Extract key points from description for back cover
    desc_lines = description.split('\n')
    bullet_points = []
    for line in desc_lines:
        if line.strip() and len(line.strip()) > 20:
            bullet_points.append(line.strip())
            if len(bullet_points) >= 3:
                break
    
    # Determine book type
    is_large_print = "Large Print" in title
    is_puzzle_book = any(word in title.lower() for word in ["crossword", "sudoku", "puzzle"])
    
    prompt = f"""Create a professional book back cover design for '{title}' by {author}.

Design specifications:
- Clean, elegant layout with ample white space
- Professional typography matching front cover style
- Subtle background pattern or texture (matching front cover theme)
- Clear hierarchy of information

Include these elements:
1. Book title at top in large, readable font
2. Author name below title
3. Brief compelling description (2-3 sentences)
4. 3-4 bullet points highlighting key features
5. Small author bio section at bottom
6. Barcode placeholder area (bottom right)
7. Publisher logo placeholder (bottom left)

Color scheme: Professional and calming, matching front cover
Style: Clean, modern, accessible
Target audience: {"Seniors and adults who prefer large print" if is_large_print else "Adults"}

Specific content to feature:
- Emphasize {"large print format" if is_large_print else "quality content"}
- Highlight {"brain training benefits" if is_puzzle_book else "engaging content"}
- Include testimonial placeholder: "★★★★★ 'Perfect for...' - Reader Review"

NO text should be generated - only design placeholders.
Professional publishing quality suitable for print."""
    
    return prompt


def add_back_cover_to_metadata(file_path: str) -> bool:
    """Add back cover prompt to a metadata file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if it's a physical book
        format_info = data.get("format", "")
        binding = data.get("binding", "")
        
        is_physical = False
        if isinstance(format_info, str):
            is_physical = format_info.lower() in ["paperback", "hardcover"]
        elif isinstance(format_info, dict):
            is_physical = format_info.get("type", "").lower() in ["paperback", "hardcover"]
        
        if not is_physical and binding:
            binding_lower = binding.lower()
            is_physical = any(term in binding_lower for term in ["paperback", "perfect", "hardcover", "case"])
        
        if not is_physical:
            return False
        
        # Check if cover_design exists
        if "cover_design" not in data:
            data["cover_design"] = {}
        
        # Check if back cover prompt already exists
        if "back_cover_dalle_prompt" in data["cover_design"]:
            print(f"  ✓ Already has back cover prompt: {os.path.basename(file_path)}")
            return False
        
        # Generate and add back cover prompt
        back_cover_prompt = generate_back_cover_prompt(data)
        data["cover_design"]["back_cover_dalle_prompt"] = back_cover_prompt
        
        # If front cover prompt is missing, add a placeholder
        if "dalle_prompt" not in data["cover_design"]:
            print(f"  ⚠️  Adding placeholder front cover prompt: {os.path.basename(file_path)}")
            data["cover_design"]["dalle_prompt"] = f"Professional book cover for '{data.get('title', 'Book')}' - NEEDS PROPER PROMPT"
        
        # Write updated file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Added back cover prompt: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def main():
    """Add back cover prompts to all physical books"""
    print("🎨 Adding Back Cover Prompts to Physical Books")
    print("=" * 50)
    
    base_dir = "/Users/igorganapolsky/workspace/git/ai/ai-kindlemint-engine"
    
    # Find all metadata files
    patterns = [
        "**/books/active_production/**/*metadata*.json",
        "**/books/active_production/**/amazon_kdp_metadata.json",
        "**/books/active_production/**/paperback_metadata.json",
        "**/books/active_production/**/hardcover_metadata.json"
    ]
    
    all_files = set()
    for pattern in patterns:
        files = glob.glob(os.path.join(base_dir, pattern), recursive=True)
        all_files.update(files)
    
    # Filter out backup files
    filtered_files = [f for f in all_files if "_backup" not in Path(f).parts]
    
    print(f"📁 Found {len(filtered_files)} metadata files to check")
    print()
    
    updated_count = 0
    for file_path in sorted(filtered_files):
        if add_back_cover_to_metadata(file_path):
            updated_count += 1
    
    print()
    print("=" * 50)
    print(f"✅ Updated {updated_count} files with back cover prompts")
    print()
    
    # Show example of a generated back cover prompt
    if updated_count > 0:
        print("📝 Example back cover prompt generated:")
        print("-" * 50)
        example_prompt = generate_back_cover_prompt({
            "title": "Large Print Sudoku Masters",
            "subtitle": "Volume 1",
            "author": "Puzzle Masters Publishing",
            "description": "Perfect for seniors and puzzle lovers"
        })
        print(example_prompt[:500] + "...")


if __name__ == "__main__":
    main()